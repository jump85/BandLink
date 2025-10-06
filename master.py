import socket
import time
import json

UDP_IP = "255.255.255.255"
UDP_PORT = 5005
BPM = 120
INTERVAL = 60 / BPM

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print("Master con timestamp sincronizzati...")

while True:
    now = time.time()
    next_beat = now + 0.2  # invia beat da eseguire 200ms dopo
    msg = {
        "command": "BEAT",
        "timestamp": next_beat,
        "bpm": BPM
    }
    sock.sendto(json.dumps(msg).encode(), (UDP_IP, UDP_PORT))
    time.sleep(INTERVAL)
