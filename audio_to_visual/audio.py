import numpy as np
import sounddevice as sd

class AudioInput:

    def __init__(self, device="hw:0,0", rate=44100, block=1024):
        self.device = device
        self.rate = rate
        self.block = block
        self.energy = [0,0,0]

    def callback(self, indata, frames, time_info, status):
        samples = indata[:,0]

        fft = np.abs(np.fft.rfft(samples))
        freqs = np.fft.rfftfreq(len(samples), 1/self.rate)

        bass = np.mean(fft[(freqs > 20) & (freqs < 250)])
        mid  = np.mean(fft[(freqs >= 250) & (freqs < 2000)])
        high = np.mean(fft[(freqs >= 2000) & (freqs < 8000)])

        self.energy = [bass, mid, high]

    def start(self):
        self.stream = sd.InputStream(
            device=self.device,
            channels=1,
            samplerate=self.rate,
            blocksize=self.block,
            callback=self.callback
        )
        self.stream.start()

        
