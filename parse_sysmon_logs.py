#!/usr/bin/env python3
# ~/malware_detector_project/parse_sysmon_logs.py
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import sys

SYSLOG_PATH = Path("/var/log/syslog")  # Sysmon for Linux writes here

def iter_event_blobs_from_file(path: Path):
    text = path.read_text(errors='ignore')
    pattern = re.compile(r'(<Event[\s\S]*?</Event>)', re.MULTILINE)
    for m in pattern.finditer(text):
        yield m.group(1)

def strip_namespace(elem):
    for e in elem.iter():
        if '}' in e.tag:
            e.tag = e.tag.split('}', 1)[1]

def parse_and_count(blobs):
    counts = {1: 0, 11: 0}
    for xml_str in blobs:
        try:
            root = ET.fromstring(xml_str)
            strip_namespace(root)
            sys_node = root.find('System')
            if sys_node is None:
                continue
            eid_node = sys_node.find('EventID')
            if eid_node is None:
                continue
            eid = int((eid_node.text or "").strip())
            if eid in counts:
                counts[eid] += 1
        except ET.ParseError:
            continue
    return counts

def main():
    if not SYSLOG_PATH.exists():
        print(f"ERROR: {SYSLOG_PATH} not found.")
        sys.exit(2)

    counts = parse_and_count(iter_event_blobs_from_file(SYSLOG_PATH))
    print(f"Parsed counts from {SYSLOG_PATH}:")
    print(f"  ProcessCreate (EventID 1): {counts[1]}")
    print(f"  FileCreate    (EventID 11): {counts[11]}")

if __name__ == "__main__":
    main()
