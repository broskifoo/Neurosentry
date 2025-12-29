#!/usr/bin/env python3
import re, sys
from pathlib import Path

LOG = Path("/var/log/audit/audit.log")

def main():
    if not LOG.exists():
        print("audit.log not found")
        sys.exit(2)

    file_creates = proc_execs = 0
    cur = None
    buf = []
    idre = re.compile(r'msg=audit\((\d+\.\d+:\d+)\)')

    with LOG.open(errors='ignore') as f:
        for line in f:
            m = idre.search(line)
            if not m:
                continue
            eid = m.group(1)
            if cur is None:
                cur = eid
            if eid != cur:
                rec = " ".join(buf)
                if ' key="simlab_file"' in rec:
                    file_creates += 1
                if ' key="proc_exec"' in rec:
                    proc_execs += 1
                buf = [line.strip()]
                cur = eid
            else:
                buf.append(line.strip())

    if buf:
        rec = " ".join(buf)
        if ' key="simlab_file"' in rec:
            file_creates += 1
        if ' key="proc_exec"' in rec:
            proc_execs += 1

    print("Parsed counts from /var/log/audit/audit.log:")
    print(f"  ProcessCreate (exec): {proc_execs}")
    print(f"  FileCreate    (writes in /tmp/sim_lab): {file_creates}")

if __name__ == "__main__":
    main()
