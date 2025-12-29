#!/usr/bin/env python3
"""
safe_simulator.py - v2 (with Auth Key)
Improved safe simulator for teaching socket programming + safe malware simulation.
Includes 'auth' key to match collector_final.py's default.
"""

from __future__ import annotations
import socket
import json
import time
import random
import signal
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Any
import uuid

# --------------------
# Configuration Defaults
# --------------------
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9999
DEFAULT_SANDBOX = Path("/tmp/sim_lab") # <-- This is the important path
DEFAULT_ITERATIONS = 10
CONNECT_RETRY_MAX = 5
CONNECT_BASE_BACKOFF = 0.5  # seconds


# --------------------
# Global state for graceful shutdown
# --------------------
_shutdown = False

def handle_sigint(signum, frame):
    global _shutdown
    logging.info("Received shutdown signal.")
    _shutdown = True

signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTERM, handle_sigint)

# --------------------
# Helpers
# --------------------
def make_message(action: str, extra: Dict[str, Any]) -> Dict[str, Any]:
    """Return a structured message with metadata and auth key."""
    return {
        
        "id": uuid.uuid4().hex,
        "ts": time.time(),
        "action": action,
        "payload": extra,
    }

def send_line(sock: socket.socket, obj: Dict[str, Any]) -> bool:
    """ Send JSON as a newline-terminated line. """
    try:
        line = (json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8")
        sock.sendall(line)
        return True
    except (BrokenPipeError, ConnectionResetError, socket.timeout, OSError) as e:
        logging.warning("Send failed: %s", e)
        return False

def connect_with_retry(host: str, port: int, max_retries: int = CONNECT_RETRY_MAX) -> socket.socket | None:
    """ Try to connect with exponential backoff. """
    attempt = 0
    while attempt <= max_retries and not _shutdown:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((host, port))
            logging.info("Connected to %s:%d", host, port)
            return sock
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            backoff = CONNECT_BASE_BACKOFF * (2 ** attempt) + random.uniform(0, 0.1)
            logging.warning("Connect attempt %d failed: %s. Backing off %.2fs", attempt + 1, e, backoff)
            time.sleep(backoff)
            attempt += 1
    logging.error("Failed to connect after %d attempts.", max_retries)
    return None

# --------------------
# Simulated behaviors
# --------------------
def simulate_file_creation(sock: socket.socket, sandbox_dir: Path) -> None:
    """Create a harmless file inside the sandbox."""
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    name = f"suspicious_file_{random.randint(100, 999)}.txt"
    file_path = sandbox_dir / name # <-- Creates file in /tmp/sim_lab/

    msg = make_message("file_create", {"path": str(file_path)})
    if send_line(sock, msg):
        try:
            file_path.write_text("This is a harmless file for simulation.\n")
            logging.info("Created sandbox file: %s", file_path)
        except OSError as e:
            logging.error("Failed to write file %s: %s", file_path, e)

def simulate_persistence(sock: socket.socket) -> None:
    """ Log an intent to persist via bashrc. """
    fake_command = "echo 'run_evil.sh' >> ~/.bashrc"
    msg = make_message("persistence_attempt", {"technique": "bashrc", "command": fake_command})
    if send_line(sock, msg):
        logging.info("Logged persistence attempt (intent only).")

def simulate_network_c2(sock: socket.socket) -> None:
    """ Log intent to beacon to a documentation-only IP. """
    fake_c2_ip = f"198.51.100.{random.randint(1, 254)}"
    msg = make_message("network_c2_beacon", {"dst_ip": fake_c2_ip, "port": 443})
    if send_line(sock, msg):
        logging.info("Logged C2 beacon intent to %s", fake_c2_ip)

# --------------------
# Main
# --------------------
def main(argv=None):
    global _shutdown
    parser = argparse.ArgumentParser(description="Safe Simulator (v2 - with Auth)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Collector host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Collector port")
    parser.add_argument("--sandbox", default=str(DEFAULT_SANDBOX), help="Sandbox directory path")
    parser.add_argument("--iters", type=int, default=DEFAULT_ITERATIONS, help="Number of actions") # <-- Accepts --iters
    parser.add_argument("--loglevel", default="INFO", help="Logging level (DEBUG/INFO/WARNING/ERROR)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.loglevel.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s %(message)s")

    sandbox_dir = Path(args.sandbox).expanduser().resolve()

    sock = connect_with_retry(args.host, args.port)
    if sock is None:
        logging.error("Exiting due to connection issues.")
        return 1

    try:
        actions = [simulate_file_creation, simulate_persistence, simulate_network_c2]
        for i in range(args.iters):
            if _shutdown:
                logging.info("Shutdown requested; stopping simulation loop.")
                break
            action = random.choice(actions)
            try:
                if action is simulate_file_creation:
                    action(sock, sandbox_dir)
                else:
                    action(sock)
            except Exception as e:
                logging.exception("Unexpected error while running action: %s", e)
            
            sleep_time = random.uniform(0.5, 2.0)
            logging.debug("Sleeping %.2fs", sleep_time)
            time.sleep(sleep_time)
    finally:
        try:
            sock.close()
        except Exception:
            pass
        logging.info("Simulator exiting cleanly.")
    return 0

if __name__ == "__main__":
    sys.exit(main())