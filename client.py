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
CHANNELS = 1
FORMAT = pyaudio.paInt16

NUM_LEDS = 64
LED_PIN = board.D18
UDP_PORT = 5005
LATENCY_CORRECTION = 0.0  # aggiusta qui se noti ritardi

# Setup
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS)
click = sa.WaveObject.from_wave_file("click.wav")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))

# Setup audio record
#audio = pyaudio.PyAudio()
#for i in range(audio.get_device_count()):
#    info = audio.get_device_info_by_index(i)
#    print(i, info.get('name'), "in:", info.get('maxInputChannels'))
#p.terminate()
#stream = audio.open(
#    format=FORMAT,
#    channels=CHANNELS,
#    rate=RATE,
#    input=True,
#    frames_per_buffer=CHUNK,
#    input_device_index=0   # Sabrent
#)
timestamp = time.strftime("%Y%m%d_%H%M%S")
filename = f"audio/recording_{timestamp}.wav"

frames = []

def flash_leds():
    #time.sleep(0.2)
    pixels.fill((0, 255, 0))
    pixels.show()
    print("pixel 0:")
    print(pixels[0])
    time.sleep(0.2)
    pixels.fill((255, 0, 0))
    pixels.show()
    print("pixel 1:")
    print(pixels[0])

print("Client in ascolto con timestamp...")

while True:
    data, addr = sock.recvfrom(1024)
    #flash_leds()
    try:
        msg = json.loads(data.decode())
        if msg.get("command") == "BEAT":
            flash_leds()
            ts = msg["timestamp"]
            delay = ts - time.time() - LATENCY_CORRECTION
            if delay > 0:
                time.sleep(delay)
            else:
                print(f"ATTENZIONE: ritardo negativo di {-delay:.3f} s")
            print(f"Beat! ({time.time():.3f})")
            #click.play()
            #flash_leds()
        if msg.get("command") == "RECORD_START":
            data = stream.read(CHUNK)
            frames.append(data)
            print("Start recording...")
        if msg.get("command") == "RECORD_STOP":
            print("Stop recording...")
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
