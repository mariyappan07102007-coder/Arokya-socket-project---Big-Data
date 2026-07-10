# Arokya Milk Supply Chain Data Harvester

This project simulates a real-time, distributed data ingestion system for the Arokya Milk supply chain. It uses Python TCP sockets to stream high-velocity data from remote processing centers to a central headquarters, where it is validated and stored in a highly compact, custom binary format.

---

## Project Structure

The project consists of three main components:

* **arokya_simulator.py**: Acts as three "high-velocity" remote branch servers (Salem, Madurai, Villupuram)[cite: 2]. It continuously streams structured log lines over TCP at random intervals to simulate bursty traffic[cite: 2].
* **arokya_harvester.py**: The central headquarters daemon that opens a dedicated TCP socket thread for each center. It manually slices the byte stream into individual lines, validates them against a regex pattern, and dynamically partitions the data into separate binary files based on the center and event type[cite: 3].
* **read_arokya_bins.py**: A verification tool that reads the custom `.bin` partition files and decodes the raw bytes back into human-readable structured logs[cite: 1].

---

## Key Technical Features

* **Multi-threading:** The simulator runs one thread per branch server, while the harvester uses separate threads to continuously read raw bytes from each branch concurrently[cite: 2, 3].
* **Socket Slicing:** Because TCP only guarantees a stream of bytes, the harvester manually buffers and slices the incoming data at newline characters to reconstruct individual records[cite: 3].
* **Regex Validation:** Incoming lines are rigorously validated using regular expressions to ensure structural integrity; corrupted lines are dropped automatically[cite: 3].
* **Dynamic Partitioning:** Custom binary partition files are created on-the-fly the first time a specific combination of branch and event type is encountered[cite: 3].
* **Binary Packing:** Plain text payloads are converted into a highly compact binary format using Python's `struct` module[cite: 3].

---

## How to Run in VS Code

### 1. Setup Your Environment
* Create a new folder named `Arokya_Socket_Project` and open it in VS Code.
* Save the three Python scripts (`arokya_simulator.py`, `arokya_harvester.py`, `read_arokya_bins.py`) into this workspace.

### 2. Start the Simulator
* Open a new terminal in VS Code (`Terminal` -> `New Terminal`).
* Run the simulator script:
  ```bash
  python arokya_simulator.py
