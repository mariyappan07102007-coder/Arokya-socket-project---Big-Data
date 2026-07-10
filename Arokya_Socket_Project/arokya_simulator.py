import socket
import threading
import random
import time
from datetime import datetime

# Simulated Arokya Centers in Tamil Nadu
CENTERS = [
    ("arokya-salem", 8001),
    ("arokya-madurai", 8002),
    ("arokya-villupuram", 8003),
]

EVENTS = ["PROCUREMENT", "QUALITY_CHECK", "PROCESSING", "ALERT"]

MESSAGE_TEMPLATES = {
    "PROCUREMENT": [
        "Received {qty}L from Farmer#{fid}",
        "Procurement truck arrived from village {fid}",
    ],
    "QUALITY_CHECK": [
        "Batch#{bid} cleared - FAT: 4.5% SNF: 8.5%",
        "Batch#{bid} cleared - FAT: 5.0% SNF: 9.0%",
        "Batch#{bid} rejected - low SNF detected",
    ],
    "PROCESSING": [
        "Pasteurization started for Batch#{bid}",
        "Homogenization complete for Batch#{bid}",
        "Packaging line A active for 500ml packets",
    ],
    "ALERT": [
        "Chiller temperature critical at 6.5°C for Batch#{bid}",
        "Power failure at main processing unit, running on generator",
    ],
}

def build_data_line(center_name):
    event = random.choice(EVENTS)
    bid = random.randint(100, 999)
    fid = random.randint(1000, 9999)
    qty = random.randint(50, 500)
    
    msg_template = random.choice(MESSAGE_TEMPLATES[event])
    message = msg_template.format(bid=bid, fid=fid, qty=qty)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"{timestamp} | {event} | {center_name} | {message}\n"

def handle_harvester(conn, center_name):
    print(f"[{center_name}] HQ connected, streaming data...")
    try:
        while True:
            line = build_data_line(center_name)
            conn.sendall(line.encode("utf-8"))
            time.sleep(random.uniform(0.1, 0.6)) # Simulate bursty data
    except (BrokenPipeError, ConnectionResetError):
        print(f"[{center_name}] HQ disconnected.")
    finally:
        conn.close()

def run_center(center_name, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", port))
    server.listen(1)
    print(f"[{center_name}] online and chilling milk on port {port}...")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_harvester, args=(conn, center_name), daemon=True)
        t.start()

if __name__ == "__main__":
    for name, port in CENTERS:
        threading.Thread(target=run_center, args=(name, port), daemon=True).start()
    print("\nAll Arokya centers operational. Press Ctrl+C to stop.\n")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down centers.")