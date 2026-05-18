import socket
import simpleaudio as sa
import time
import board
import neopixel
import json
import pyaudio
import wave
import time
import threading
import numpy as np
import sounddevice as sd
from audio_to_visual import AudioVisualEngine

# Configurazione
AUDIO_RATE = 44100
AUDIO_BLOCK = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16


NUM_LEDS = 64
LED_PIN = board.D18
UDP_PORT = 5006
UDP_SERVER_IP = "192.168.178.10"
UDP_SERVER_PORT = 9000

LATENCY_CORRECTION = 0.0  # aggiusta qui se noti ritardi

sequence = 0

# Setup
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=0.5, auto_write=False)
engine = AudioVisualEngine(NUM_LEDS)

click = sa.WaveObject.from_wave_file("click.wav")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))


audio_energy = [0, 0, 0]  # bass, mid, high
lock = threading.Lock()

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

# ================= AUDIO FFT & STREAMING =================
def audio_callback(indata, frames, time_info, status):
    global audio_energy
    global sequence

    # STREAMING PART

    timestamp = time.time()

    pcm = indata.tobytes()

    header = struct.pack(
        "IdH",
        sequence,
        timestamp,
        len(pcm)
    )

    packet = header + pcm

    sock.sendto(packet, (UDP_SERVER_IP, UDP_SERVER_PORT))

    sequence += 1
    # FFT PART
    samples = indata[:, 0]
    fft = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1 / AUDIO_RATE)

    bass = np.mean(fft[(freqs > 20) & (freqs < 250)])
    mid  = np.mean(fft[(freqs > 250) & (freqs < 2000)])
    high = np.mean(fft[(freqs > 2000) & (freqs < 8000)])

    with lock:
        audio_energy = [bass, mid, high]

def start_audio_stream():
    with sd.InputStream(
	channels=1,
        samplerate=AUDIO_RATE,
        blocksize=AUDIO_BLOCK,
        callback=audio_callback
    ):
         while True:
             audio_reactive_leds()

# ================= LED EFFECT =================
def audio_reactive_leds():
    engine.start()
    while True:
        frame, beat, mode = engine.get_frame()

        for i, c in enumerate(frame):
            pixels[i] = c

        pixels.show()
        print(mode, beat)

        time.sleep(0.03)

# ================= BEAT EFFECT =================
def flash_leds():
    pixels.fill((255, 255, 255))
    pixels.show()
    time.sleep(0.05)

# ================= THREAD START =================
engine.start()
#audio_reactive_leds()

print("Client in ascolto con timestamp...")

while True:
    data, addr = sock.recvfrom(1024)
    #flash_leds()
    #audio_reactive_leds()
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
