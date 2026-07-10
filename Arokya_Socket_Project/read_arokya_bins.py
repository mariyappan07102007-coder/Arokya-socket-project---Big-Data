import struct
import sys

EVENT_CODE = {"PROCUREMENT": 0, "QUALITY_CHECK": 1, "PROCESSING": 2, "ALERT": 3}
CODE_EVENT = {v: k for k, v in EVENT_CODE.items()}

def read_binary(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    offset = 0
    records = []
    while offset < len(data):
        (rec_len,) = struct.unpack_from("!I", data, offset)
        offset += 4

        record = data[offset : offset + rec_len]
        offset += rec_len

        ts_bytes, evt_byte, cen_len = struct.unpack_from("!19sBH", record, 0)
        pos = 22 # 19 + 1 + 2

        center = record[pos : pos + cen_len].decode("utf-8")
        pos += cen_len

        (msg_len,) = struct.unpack_from("!H", record, pos)
        pos += 2
        message = record[pos : pos + msg_len].decode("utf-8")

        records.append({
            "timestamp": ts_bytes.decode("ascii").strip(),
            "event": CODE_EVENT[evt_byte],
            "center": center,
            "message": message,
        })
    return records

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_arokya_bins.py <path-to-.bin-file>")
        sys.exit(1)

    records = read_binary(sys.argv[1])
    print(f"Decoded {len(records)} records from {sys.argv[1]}:\n")
    for r in records:
        print(f"[{r['timestamp']}] {r['event']} | {r['center']} -> {r['message']}")