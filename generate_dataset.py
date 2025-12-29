#!/usr/bin/env python3
"""
Simulator v4 — improved sender for the JSON-line collector.

Improvements:
- Newline-delimited JSON framing (collector-friendly)
- Includes 'auth' field with configurable key
- Uses logging (levels + timestamps)
- Retries on transient socket errors
- Socket timeouts and safe sends
- Safer psutil usage and sandbox dir creation
- CLI options for host/port/auth/events/delays/retries
"""

from __future__ import annotations
import socket
import json
import time
import random
import os
import argparse
import logging
import sys
import psutil
from datetime import datetime, timezone

# --- Defaults (match collector defaults unless overridden) ---
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9999
DEFAULT_AUTH = "MY_SECRET_KEY"
SANDBOX_DIR = "/tmp/sim_lab"
DEFAULT_EVENTS = 100
DEFAULT_MIN_DELAY = 0.10
DEFAULT_MAX_DELAY = 0.50
DEFAULT_RETRIES = 3
CONNECT_TIMEOUT = 5.0
SEND_TIMEOUT = 5.0

# --- CLI ---
parser = argparse.ArgumentParser(description="Improved simulator that sends JSON logs (with auth).")
parser.add_argument('--host', default=DEFAULT_HOST, help="Collector host")
parser.add_argument('--port', type=int, default=DEFAULT_PORT, help="Collector port")
parser.add_argument('--auth', default=DEFAULT_AUTH, help="Authentication key to include in each log")
parser.add_argument('--label', required=True, choices=['benign', 'malicious'], help="Simulation label")
parser.add_argument('--events', type=int, default=DEFAULT_EVENTS, help="Total number of events to generate")
parser.add_argument('--min-delay', type=float, default=DEFAULT_MIN_DELAY, help="Min delay between events (s)")
parser.add_argument('--max-delay', type=float, default=DEFAULT_MAX_DELAY, help="Max delay between events (s)")
parser.add_argument('--retries', type=int, default=DEFAULT_RETRIES, help="Socket connect retries")
args = parser.parse_args()

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# --- Utility: safe JSON send with newline framing ---
def safe_send_json(sock: socket.socket, obj: dict) -> bool:
    """
    Send JSON object with newline framing. Return True on success, False on failure.
    """
    try:
        raw = json.dumps(obj, ensure_ascii=False) + "\n"
        # Use encode with utf-8; socket has a send timeout to avoid hangs
        sock.sendall(raw.encode('utf-8'))
        return True
    except (BrokenPipeError, ConnectionResetError, socket.timeout) as e:
        logging.warning(f"Connection lost while sending: {e}")
        return False
    except Exception as e:
        logging.exception(f"Unexpected error while sending: {e}")
        return False

# --- Simulation functions ---
def simulate_benign_file_read(sock: socket.socket, sim_id: str) -> bool:
    path = "/var/log/syslog"
    logging.info(f"[BENIGN] Simulated reading {path}")
    event = {
        "auth": args.auth,
        "sim_id": sim_id,
        "label": "benign",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "file_read",
        "path": path
    }
    return safe_send_json(sock, event)

def simulate_benign_process_list(sock: socket.socket, sim_id: str) -> bool:
    pids = psutil.pids()
    if not pids:
        logging.warning("[BENIGN] No processes found via psutil.")
        return True
    # try a few times to get a valid process with accessible info
    for _ in range(5):
        pid = random.choice(pids)
        try:
            p = psutil.Process(pid)
            name = p.name()
            user = p.username()
            logging.info(f"[BENIGN] Simulated listing process info for PID {pid} ({name})")
            event = {
                "auth": args.auth,
                "sim_id": sim_id,
                "label": "benign",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "process_info",
                "pid": pid,
                "name": name,
                "user": user
            }
            return safe_send_json(sock, event)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            logging.exception("Unexpected psutil error.")
            return True
    # If we couldn't get process info, just return True (sim still continues)
    logging.info("[BENIGN] Could not fetch process info after retries; skipping.")
    return True

def simulate_malicious_file_creation(sock: socket.socket, sim_id: str) -> bool:
    os.makedirs(SANDBOX_DIR, mode=0o700, exist_ok=True)
    file_path = os.path.join(SANDBOX_DIR, f"evil_{random.randint(100, 999)}.sh")
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("#!/bin/bash\necho 'I am not evil.'\n")
        # make it non-world-executable (owner only) for sandbox safety
        try:
            os.chmod(file_path, 0o700)
        except Exception:
            pass
        logging.info(f"[MALICIOUS] Created file: {file_path}")
        event = {
            "auth": args.auth,
            "sim_id": sim_id,
            "label": "malicious",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "file_create",
            "path": file_path
        }
        return safe_send_json(sock, event)
    except Exception as e:
        logging.exception(f"Failed to create sandbox file: {e}")
        return False

def simulate_malicious_persistence(sock: socket.socket, sim_id: str) -> bool:
    logging.info("[MALICIOUS] Logged persistence attempt")
    event = {
        "auth": args.auth,
        "sim_id": sim_id,
        "label": "malicious",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "persistence_attempt",
        "technique": "bashrc",
        "command": "echo 'run_evil.sh' >> ~/.bashrc"
    }
    return safe_send_json(sock, event)

def simulate_malicious_network_c2(sock: socket.socket, sim_id: str) -> bool:
    dst_ip = f"203.0.113.{random.randint(1, 254)}"
    logging.info(f"[MALICIOUS] Logged C2 beacon to {dst_ip}:8080")
    event = {
        "auth": args.auth,
        "sim_id": sim_id,
        "label": "malicious",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "network_c2_beacon",
        "dst_ip": dst_ip,
        "port": 8080
    }
    return safe_send_json(sock, event)

# --- Main runner ---
def run_simulation():
    sim_id = f"sim-{int(time.time())}-{random.randint(1000,9999)}"
    label = args.label
    events = max(0, args.events)
    min_delay = max(0.0, args.min_delay)
    max_delay = max(min_delay, args.max_delay)
    retries = max(0, args.retries)

    if label == 'benign':
        behaviors = [simulate_benign_file_read, simulate_benign_process_list]
    else:
        behaviors = [simulate_malicious_file_creation, simulate_malicious_persistence, simulate_malicious_network_c2]

    logging.info(f"Starting {label} simulation (sim_id={sim_id}) with {events} events. Collector: {args.host}:{args.port}")
    logging.info("Ensure collector.py is running in another terminal.")

    events_generated = 0
    attempt = 0
    while attempt <= retries:
        try:
            with socket.create_connection((args.host, args.port), timeout=CONNECT_TIMEOUT) as sock:
                # optional socket-level timeout for sends/receives
                sock.settimeout(SEND_TIMEOUT)
                logging.info("Connected to collector.")
                # send events
                for i in range(events):
                    # choose a behavior at random to mix actions
                    behavior = random.choice(behaviors)
                    ok = behavior(sock, sim_id)
                    if not ok:
                        logging.warning("Send failed; aborting simulation run.")
                        return events_generated
                    events_generated += 1
                    # delay between events
                    time.sleep(random.uniform(min_delay, max_delay))
                logging.info("Finished sending events; closing connection.")
                return events_generated
        except (ConnectionRefusedError, socket.timeout) as e:
            attempt += 1
            logging.warning(f"Connection attempt {attempt}/{retries} failed: {e}. Retrying in 1s...")
            time.sleep(1.0)
        except Exception as e:
            logging.exception(f"Unexpected error while connecting/sending: {e}")
            return events_generated

    logging.error("Exceeded maximum connect retries. Exiting.")
    return events_generated

if __name__ == "__main__":
    try:
        generated = run_simulation()
        logging.info(f"Finished simulation for label: {args.label} (Generated {generated} events)")
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Exiting.")
