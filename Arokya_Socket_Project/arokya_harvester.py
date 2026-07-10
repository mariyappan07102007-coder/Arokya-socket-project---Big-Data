import socket
import threading
import re
import struct
import os
import time
from collections import defaultdict

CENTERS = [
    ("arokya-salem", 8001),
    ("arokya-madurai", 8002),
    ("arokya-villupuram", 8003),
]

HOST = "127.0.0.1"
PARTITION_DIR = "arokya_data"

# Regex for: 2026-07-10 14:32:10 | QUALITY_CHECK | arokya-salem | message
PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*"
    r"(?P<event>PROCUREMENT|QUALITY_CHECK|PROCESSING|ALERT)\s*\|\s*"
    r"(?P<center>[\w\-]+)\s*\|\s*"
    r"(?P<message>.+)$"
)

EVENT_CODE = {"PROCUREMENT": 0, "QUALITY_CHECK": 1, "PROCESSING": 2, "ALERT": 3}

partition_files = {}
partition_locks = defaultdict(threading.Lock)
master_lock = threading.Lock()
stats_lock = threading.Lock()
stats = defaultdict(int)

def get_file(center, event):
    key = (center, event)
    with master_lock:
        if key not in partition_files:
            os.makedirs(PARTITION_DIR, exist_ok=True)
            path = os.path.join(PARTITION_DIR, f"{center}_{event}.bin")
            partition_files[key] = open(path, "ab")
            print(f"[Partition] New data file created: {path}")
        return partition_files[key]

def encode_record(ts, event, center, msg):
    ts_bytes = ts.encode("ascii").ljust(19, b" ")[:19]
    evt_byte = EVENT_CODE[event]
    cen_bytes = center.encode("utf-8")
    msg_bytes = msg.encode("utf-8")

    header = struct.pack("!19sBH", ts_bytes, evt_byte, len(cen_bytes))
    mid = struct.pack("!H", len(msg_bytes))
    return header + cen_bytes + mid + msg_bytes

def write_payload(data):
    bin_record = encode_record(data["timestamp"], data["event"], data["center"], data["message"])
    length_prefix = struct.pack("!I", len(bin_record))
    
    key = (data["center"], data["event"])
    f = get_file(data["center"], data["event"])
    with partition_locks[key]:
        f.write(length_prefix + bin_record)
        f.flush()

def process_stream(raw_line, center_name):
    match = PATTERN.match(raw_line)
    if not match: return

    data = {
        "timestamp": match.group("timestamp"),
        "event": match.group("event"),
        "center": match.group("center"),
        "message": match.group("message"),
    }
    write_payload(data)
    with stats_lock:
        stats[(center_name, data["event"])] += 1

def harvest(center_name, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, port))
    buffer = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk: break
            buffer += chunk
            while b"\n" in buffer:
                line_bytes, buffer = buffer.split(b"\n", 1)
                try:
                    if line := line_bytes.decode("utf-8").strip():
                        process_stream(line, center_name)
                except UnicodeDecodeError: continue
    finally:
        sock.close()

def dashboard():
    while True:
        time.sleep(3)
        with stats_lock:
            if not stats: continue
            print("\n--- Arokya HQ Live Data Ingestion ---")
            for (center, evt), count in sorted(stats.items()):
                print(f"  {center:18s} | {evt:14s} | {count} records")
            print("-------------------------------------\n")

if __name__ == "__main__":
    for name, port in CENTERS:
        threading.Thread(target=harvest, args=(name, port), daemon=True).start()
    threading.Thread(target=dashboard, daemon=True).start()
    print("HQ Harvester running. Press Ctrl+C to stop.\n")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        for f in partition_files.values(): f.close()