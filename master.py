import socket
import time
import json
import struct
import sounddevice as sd
import numpy as np

UDP_IP = "255.255.255.255"
UDP_PORT = 5005
UDP_SERVER_PORT = 9000
BPM = 120
INTERVAL = 60 / BPM

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("0.0.0.0", UDP_SERVER_PORT))

start_time = time.time()
#start_recording()
print(sd.query_devices())
stream = sd.OutputStream(
    samplerate=44100,
    channels=1,
    dtype='int16',
    blocksize=1024,
    device=2
)

stream.start()
HEADER_SIZE = struct.calcsize("IdH")

print("Master with sync timestamps...")
while True:

    # RECEIVE AUDIO PACKET
    packet, addr = sock.recvfrom(4096)

    header = packet[:HEADER_SIZE]
    sequence, timestamp, size = struct.unpack("IdH", header)
    pcm = packet[HEADER_SIZE:]
    audio = np.frombuffer(pcm, dtype=np.int16)
    stream.write(audio)

    #SEND BEAT PACKET
    now = time.time()
    next_beat = now + 0.2  # sends beat to be executed 200ms after
    msg = {
        "command": "BEAT",
        "timestamp": next_beat,
        "bpm": BPM
    }
    sock.sendto(json.dumps(msg).encode(), (UDP_IP, UDP_PORT))
    time.sleep(INTERVAL)


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
