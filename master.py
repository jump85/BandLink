import socket
import time
import json

UDP_IP = "255.255.255.255"
UDP_PORT = 5005
BPM = 120
INTERVAL = 60 / BPM

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Start recording
def start_recording():
    print("Start recording...")
    msg = {
        "command": "RECORD_START"
    }
    sock.sendto(json.dumps(msg).encode(), (UDP_IP, UDP_PORT))

# Stop recording
def stop_recording():
    print("Stop recording...")
    msg = {
        "command": "RECORD_STOP"
    }
    sock.sendto(json.dumps(msg).encode(), (UDP_IP, UDP_PORT))

start_time = time.time()
start_recording()

print("Master with sync timestamps...")
while True:
    now = time.time()
    next_beat = now + 0.2  # sends beat to be executed 200ms after
    msg = {
        "command": "BEAT",
        "timestamp": next_beat,
        "bpm": BPM
    }
    sock.sendto(json.dumps(msg).encode(), (UDP_IP, UDP_PORT))
    time.sleep(INTERVAL)
    if (now - start_time > 10):
        stop_recording()


