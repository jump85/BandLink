import socket
import simpleaudio as sa
import time
import board
import neopixel
import json

# Configurazione
NUM_LEDS = 10
LED_PIN = board.D18
UDP_PORT = 5005
LATENCY_CORRECTION = 0.0  # aggiusta qui se noti ritardi

# Setup
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=0.5, auto_write=False)
click = sa.WaveObject.from_wave_file("click.wav")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))

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
    except Exception as e:
        print(f"Errore nella ricezione: {e}")
