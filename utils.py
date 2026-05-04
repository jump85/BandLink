import numpy as np
import time

class SignalProcessor:

    def __init__(self):
        self.max_vals = [1,1,1]
        self.prev = [0,0,0]
        self.beat_prev = 0
        self.last_beat = 0

    def normalize(self, vals):
        out = []

        for i,v in enumerate(vals):
            self.max_vals[i] = max(self.max_vals[i]*0.97, v)

            x = np.log1p(v)/np.log1p(self.max_vals[i])
            x = np.clip(x,0,1)

            val = int(self.prev[i]*0.7 + x*255*0.3)
            self.prev[i] = val

            out.append(val)

        return out

    def detect_beat(self, bass):
        now = time.time()
        threshold = self.beat_prev * 1.4

        beat = False
        if bass > threshold and (now - self.last_beat) > 0.25:
            beat = True
            self.last_beat = now

        self.beat_prev = bass*0.2 + self.beat_prev*0.8

        return beat