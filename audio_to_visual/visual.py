import numpy as np

class VisualEngine:

    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.phase = 0

    def palette(self, r,g,b):
        return (r,g,b)

    def ambient(self, frame, color):
        for i in range(len(frame)):
            brightness = 0.2 + 0.2*np.sin(self.phase + i*0.5)
            frame[i] = tuple(int(c*brightness) for c in color)

    def groove(self, frame, color):
        for i in range(len(frame)):
            frame[i] = color if i % 2 == int(self.phase)%2 else (0,0,0)

    def aggressive(self, frame, color, beat):
        for i in range(len(frame)):
            if beat:
                frame[i] = (255,255,255)
            else:
                frame[i] = tuple(int(c*0.5) for c in color)

    def render(self, mode, color, beat):
        frame = [(0,0,0)] * self.num_leds

        if mode == "ambient":
            self.ambient(frame, color)

        elif mode == "groove":
            self.groove(frame, color)

        elif mode == "aggressive":
            self.aggressive(frame, color, beat)

        self.phase += 0.2

        return frame