import socket
import simpleaudio as sa
import time
import board
import neopixel
import json
import pyaudio
import wave
import time

# Configurazione
RATE = 44100
CHUNK = 1024
CHANNELS = 2
FORMAT = pyaudio.paInt16

NUM_LEDS = 10
LED_PIN = board.D18
UDP_PORT = 5005
LATENCY_CORRECTION = 0.0  # aggiusta qui se noti ritardi

# Setup
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=0.5, auto_write=False)
click = sa.WaveObject.from_wave_file("click.wav")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))

# Setup audio record
audio = pyaudio.PyAudio()
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    input_device_index=1   # Sabrent
)
timestamp = time.strftime("%Y%m%d_%H%M%S")
filename = f"recording_{timestamp}.wav"

frames = []

def flash_leds():
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.1)
    pixels.fill((0, 0, 0))
    pixels.show()

print("Client in ascolto con timestamp...")

while True:
    data, addr = sock.recvfrom(1024)
    try:
        msg = json.loads(data.decode())
        if msg.get("command") == "BEAT":
            ts = msg["timestamp"]
            delay = ts - time.time() - LATENCY_CORRECTION
            if delay > 0:
                time.sleep(delay)
            else:
                print(f"ATTENZIONE: ritardo negativo di {-delay:.3f} s")
            print(f"Beat! ({time.time():.3f})")
            click.play()
            flash_leds()
        if msg.get("command") == "RECORD_START":
            data = stream.read(CHUNK)
            frames.append(data)
        if msg.get("command") == "RECORD_STOP":
            stream.stop_stream()
            stream.close()
            audio.terminate()

            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
    except Exception as e:
        print(f"Errore nella ricezione: {e}")
