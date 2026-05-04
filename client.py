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

# Configurazione
AUDIO_RATE = 44100
AUDIO_BLOCK = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16

NUM_LEDS = 64
LED_PIN = board.D18
UDP_PORT = 5006
LATENCY_CORRECTION = 0.0  # aggiusta qui se noti ritardi

# =========================
# GLOBAL STATE
# =========================
audio_energy = [0, 0, 0]
max_vals = [1, 1, 1]
rgb_prev = [0, 0, 0]
beat_prev = 0
last_beat = 0

# Setup
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=0.5, auto_write=False)
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

# ================= AUDIO FFT =================
def audio_callback(indata, frames, time_info, status):
    print("start audio callback")
    global audio_energy

    samples = indata[:, 0]
    fft = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1 / AUDIO_RATE)

    bass = np.mean(fft[(freqs > 20) & (freqs < 250)])
    mid  = np.mean(fft[(freqs > 250) & (freqs < 2000)])
    high = np.mean(fft[(freqs > 2000) & (freqs < 8000)])

    with lock:
        audio_energy = [bass, mid, high]

def start_audio_stream():
    print(sd.query_devices())
    with sd.InputStream(
	channels=1,
        samplerate=AUDIO_RATE,
        blocksize=AUDIO_BLOCK,
        device="hw:0,0",
        callback=audio_callback
    ):
        while True:
            time.sleep(0.1)    

# ============== AUDIO NORMALIZATION =============
def normalize_dynamic(bass, mid, high):
    global max_vals, rgb_prev

    vals = [bass, mid, high]
    rgb = []

    for i,v in enumerate(vals):
        max_vals[i] = max(max_vals[i]*0.97, v)

        x = np.log1p(v) / np.log1p(max_vals[i])
        x = min(max(x,0),1)

        val = int(x * 255)

        # smoothing
        val = int(rgb_prev[i]*0.7 + val*0.3)

        rgb_prev[i] = val
        rgb.append(val)

    return tuple(rgb)

# =========================
# RGB TO PALETTE
# =========================
def palette_from_energy(r, g, b, mode="neon"):
    if mode == "neon":
        return (
            min(255, r),
            min(255, g),
            min(255, b)
        )

    elif mode == "fire":
        return (
            min(255, r),
            min(180, int(r * 0.6)),
            0
        )

    elif mode == "ice":
        return (
            0,
            min(255, g),
            min(255, b)
        )

    return (r, g, b)
# ================= LED EFFECT =================
def audio_reactive_leds():
    print("init reactive leds")
    while True:
        with lock:
            bass, mid, high = audio_energy
        print(bass)
        # normalizzazione semplice
        #r = min(int(bass / 5000), 255)
        #g = min(int(mid / 3000), 255)
        #b = min(int(high / 2000), 255)

        # normalizzazione dinamica
        r,g,b = normalize_dynamic(bass, mid, high)
        
        
        beat = detect_beat(bass)
        color = palette_from_energy(r, g, b, mode="neon")

        frame = []
        
        print("rgb values:")
        print(r)
        print(g)
        print(b)
        for i in range(NUM_LEDS):
            brightness = 1.0 - (i / NUM_LEDS) * 0.4

            rr = int(color[0] * brightness)
            gg = int(color[1] * brightness)
            bb = int(color[2] * brightness)

            if beat:
                rr = min(255, rr + 80)
                gg = min(255, gg + 80)
                bb = min(255, bb + 80)

            pixels[i] = (rr, gg, bb)

        pixels.show()
        time.sleep(0.03)
# =========================
# BEAT DETECTION
# =========================
def detect_beat(bass):
    global beat_prev, last_beat

    now = time.time()

    threshold = beat_prev * 1.4

    beat = False

    if bass > threshold and (now - last_beat) > 0.25:
        beat = True
        last_beat = now

    beat_prev = bass * 0.2 + beat_prev * 0.8

    return beat

# ================= BEAT EFFECT =================
def flash_leds():
    pixels.fill((0, 255, 0))
    pixels.show()
    print("pixel 0:")
    print(pixels[0])
    time.sleep(0.2)
    pixels.fill((255, 0, 0))
    pixels.show()
    print("pixel 1:")
    print(pixels[0])

# ================= THREAD START =================
#start_audio_stream()
threading.Thread(target=start_audio_stream, daemon=True).start()
threading.Thread(target=audio_reactive_leds, daemon=True).start()

print("Client in ascolto con timestamp...")
audio_reactive_leds()

while True:
    data, addr = sock.recvfrom(1024)
    #flash_leds()
    audio_reactive_leds()
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
