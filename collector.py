#!/usr/bin/env python3
"""
NeuroSentry Collector (no auth)
- TCP server that accepts newline-delimited JSON records.
- Thread-per-connection for reads; single writer thread for ordered disk writes.
- Adds ISO8601 UTC timestamp if missing.
- Rotating server log; JSONL output is append-only.
- Graceful SIGINT/SIGTERM shutdown.

Run:
  python3 collector.py \
    --host 0.0.0.0 --port 9999 \
    --log-file ~/malware_detector_project/data/dynamic_trace.jsonl \
    --server-log ~/malware_detector_project/logs/collector.log
"""
from __future__ import annotations
import argparse
import json
import logging
import signal
import socket
import sys
import threading
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from queue import Queue, Empty

# ---------------- Config defaults ----------------
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 9999
BUFFER_SIZE = 4096
CONN_TIMEOUT = 10.0
WRITE_QUEUE_MAX = 10000

# ---------------- Writer thread ----------------
def writer_loop(stop_evt: threading.Event, q: Queue, jsonl_path: Path, logger: logging.Logger):
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "a", encoding="utf-8") as fh:
        while not stop_evt.is_set() or not q.empty():
            try:
                rec = q.get(timeout=0.25)
            except Empty:
                continue
            try:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
            except Exception:
                logger.exception("Failed to write JSONL")
            finally:
                q.task_done()

# ---------------- Client handler ----------------
def handle_client(conn: socket.socket, addr, q: Queue, stop_evt: threading.Event, logger: logging.Logger):
    logger.info(f"connection from {addr}")
    conn.settimeout(CONN_TIMEOUT)
    buf = ""
    try:
        while not stop_evt.is_set():
            try:
                data = conn.recv(BUFFER_SIZE)
            except socket.timeout:
                logger.info(f"{addr} timed out; closing")
                break
            if not data:
                break
            buf += data.decode("utf-8", errors="replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip("\r ")
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(f"invalid JSON from {addr}: {line[:200]}")
                    continue
                # add server timestamp if missing
                rec.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

                # backpressure: drop oldest if queue is full
                if q.qsize() >= WRITE_QUEUE_MAX:
                    logger.warning("write queue full; dropping oldest")
                    try:
                        q.get_nowait()
                        q.task_done()
                    except Empty:
                        pass
                q.put(rec)
    except Exception:
        logger.exception(f"handler error for {addr}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
        logger.info(f"closed {addr}")

# ---------------- Main ----------------
def main():
    ap = argparse.ArgumentParser(description="NeuroSentry TCP JSONL collector (no auth)")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--log-file", default="dynamic_trace.jsonl", help="JSONL output path")
    ap.add_argument("--server-log", default="collector.log", help="server log path (rotates)")
    args = ap.parse_args()

    # logging
    logger = logging.getLogger("collector")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console = logging.StreamHandler(sys.stdout); console.setFormatter(fmt)
    Path(args.server_log).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    rot = RotatingFileHandler(args.server_log, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    rot.setFormatter(fmt)
    logger.handlers.clear(); logger.addHandler(console); logger.addHandler(rot)

    jsonl_path = Path(args.log_file).expanduser().resolve()
    stop_evt = threading.Event()
    write_q: Queue = Queue(maxsize=WRITE_QUEUE_MAX)
    threads: list[threading.Thread] = []

    # signals
    def stop(_sig, _frm):
        logger.info("shutdown requested")
        stop_evt.set()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    # writer
    wt = threading.Thread(target=writer_loop, args=(stop_evt, write_q, jsonl_path, logger), daemon=True)
    wt.start()

    # server socket
    logger.info(f"starting collector on {args.host}:{args.port}, writing to {jsonl_path}")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.host, args.port))
    srv.listen(200)
    srv.settimeout(1.0)
    logger.info("listening for connections…")

    try:
        while not stop_evt.is_set():
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            t = threading.Thread(target=handle_client, args=(conn, addr, write_q, stop_evt, logger), daemon=True)
            threads.append(t); t.start()
    except Exception:
        logger.exception("main loop error")
    finally:
        logger.info("shutting down: closing listen socket")
        try: srv.close()
        except Exception: pass

        for t in threads:
            t.join(timeout=1.0)
        write_q.join()
        stop_evt.set()
        wt.join(timeout=1.0)
        logger.info("collector stopped cleanly")

if __name__ == "__main__":
    main()

