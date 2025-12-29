# core/log_parser.py
from __future__ import annotations
from typing import List, Dict, Any, Optional, Iterable
from dataclasses import dataclass
from pathlib import Path
import re
import pandas as pd

# ---------- Event model ----------
@dataclass
class LogEntry:
    action: str                 # e.g., "file_create", "process_exec"
    location: Optional[str] = None  # filename or image/exe
    ts: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None

# ---------- AUDITD PARSER ----------
_AUDIT_LOG = Path("/var/log/audit/audit.log")

# We tagged our audit rules with keys:
#   - simlab_file  (file activity in /tmp/sim_lab)
#   - proc_exec    (process execution events)
_AUDIT_EVENT_ID_RE = re.compile(r"msg=audit\((\d+\.\d+):\d+\)")
_KEY_RE            = re.compile(r' key="([^"]+)"')
_PATH_RE           = re.compile(r'type=PATH .* name="([^"]*)"')
_EXE_RE            = re.compile(r' exe="([^"]*)"')
_CWD_RE            = re.compile(r'type=CWD .* cwd="([^"]*)"')

def parse_audit_log(
    log_path: str = str(_AUDIT_LOG),
    max_bytes: int = 2_000_000
) -> List[LogEntry]:
    """
    Parse auditd log and return normalized LogEntry items.
    Recognizes our two keys: 'simlab_file' and 'proc_exec'.
    """
    p = Path(log_path)
    if not p.exists():
        return []

    # Read tail of the file (in case it's large)
    data: str
    with p.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - max_bytes))
        data = f.read().decode("utf-8", errors="ignore")

    # Coalesce multi-line audit records by audit(ID)
    out: List[LogEntry] = []
    cur_id: Optional[str] = None
    buf: List[str] = []

    def flush():
        if not buf:
            return
        record = " ".join(buf)
        # Which key?
        km = _KEY_RE.search(record)
        key = km.group(1) if km else None

        # Common fields
        tm = _AUDIT_EVENT_ID_RE.search(record)
        ts = float(tm.group(1)) if tm else None
        path = (_PATH_RE.search(record).group(1)
                if _PATH_RE.search(record) else None)
        exe  = (_EXE_RE.search(record).group(1)
                if _EXE_RE.search(record) else None)
        cwd  = (_CWD_RE.search(record).group(1)
                if _CWD_RE.search(record) else None)

        if key == "simlab_file":
            out.append(LogEntry(
                action="file_create",
                location=path,
                ts=ts,
                meta={"exe": exe, "cwd": cwd, "key": key}
            ))
        elif key == "proc_exec":
            out.append(LogEntry(
                action="process_exec",
                location=exe,
                ts=ts,
                meta={"cwd": cwd, "key": key}
            ))
        buf.clear()

    for line in data.splitlines():
        m = _AUDIT_EVENT_ID_RE.search(line)
        if not m:
            continue
        evt_id = m.group(1)  # e.g., "1733550943.123:456"
        if cur_id is None:
            cur_id = evt_id
        if evt_id != cur_id:
            flush()
            buf = [line.strip()]
            cur_id = evt_id
        else:
            buf.append(line.strip())
    flush()
    return out

# ---------- (Optional) Sysmon parser shim ----------
# Keeping a tiny stub so old code doesn't break if you later re-enable Sysmon.
def parse_sysmon_log(*_, **__) -> List[LogEntry]:
    """
    Deprecated here. We moved to auditd. Returns [] by default.
    Keep this function name so upstream imports don't fail.
    """
    return []

# ---------- Features ----------
def logs_to_features(
    logs: Iterable[LogEntry | Dict[str, Any]],
    columns: List[str]
) -> pd.DataFrame:
    """
    Convert a list of LogEntry (or dicts with 'action') into a single-row feature vector.
    Each column is a counter for that action.
    """
    # Normalize to LogEntry
    norm: List[LogEntry] = []
    for x in logs:
        if isinstance(x, LogEntry):
            norm.append(x)
        elif isinstance(x, dict):
            norm.append(LogEntry(action=x.get("action", ""), location=x.get("location")))
        else:
            continue

    # Count actions
    counts = {col: 0 for col in columns}
    for e in norm:
        if e.action in counts:
            counts[e.action] += 1

    df = pd.DataFrame([counts], columns=columns)
    df = df.reindex(columns=columns, fill_value=0)
    return df
