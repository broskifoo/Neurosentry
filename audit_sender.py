#!/usr/bin/env python3
"""
audit_sender.py — Real auditd → NeuroSentry agent

Continuously tails /var/log/audit/audit.log,
maps audit rules to simplified security actions,
and streams them to the NeuroSentry collector.

Requires:
- auditd running
- audit rules with keys:
  - proc_exec
  - tmp_write
  - etc_write
"""

import subprocess
import socket
import json
import argparse
import sys
import time


def connect_collector(host: str, port: int) -> socket.socket:
    """Connect to NeuroSentry collector."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def main():
    parser = argparse.ArgumentParser(description="NeuroSentry auditd sender (no auth)")
    parser.add_argument("--host", default="127.0.0.1", help="Collector host")
    parser.add_argument("--port", type=int, default=9999, help="Collector port")
    args = parser.parse_args()

    try:
        sock = connect_collector(args.host, args.port)
        print("[i] Connected to collector")
    except Exception as e:
        print(f"[ERROR] Failed to connect to collector: {e}", file=sys.stderr)
        sys.exit(1)

    # Tail audit log continuously (this is the KEY fix)
    proc = subprocess.Popen(
        ["tail", "-F", "/var/log/audit/audit.log"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue

            action = None

            # ---- Map audit rules → model actions ----
            if 'key="proc_exec"' in line:
                action = "process_info"
            elif 'key="tmp_write"' in line:
                action = "file_create"
            elif 'key="etc_write"' in line:
                action = "persistence_attempt"

            if action:
                event = {
                    "action": action,
                    "raw": line,
                }

                try:
                    sock.sendall((json.dumps(event) + "\n").encode("utf-8"))
                except BrokenPipeError:
                    print("[ERROR] Collector connection lost", file=sys.stderr)
                    break

    except KeyboardInterrupt:
        print("\n[i] audit_sender stopped by user")

    finally:
        try:
            sock.close()
        except Exception:
            pass
        try:
            proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
