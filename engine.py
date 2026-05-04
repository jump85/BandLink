from .audio import AudioInput
from .ai import AIEngine
from .visual import VisualEngine
from .utils import SignalProcessor

class AudioVisualEngine:

    def __init__(self, num_leds=10, device="plughw:0,0"):
        self.audio = AudioInput(device=device)
        self.ai = AIEngine()
        self.visual = VisualEngine(num_leds)
        self.proc = SignalProcessor()

    def start(self):
        self.audio.start()

    def get_frame(self):
        energy = self.audio.energy

        norm = self.proc.normalize(energy)
        beat = self.proc.detect_beat(energy[0])

        r,g,b = norm
        color = (r,g,b)

        mode = self.ai.update([x/255 for x in norm], beat)

        frame = self.visual.render(mode, color, beat)

        return frame, beat, mode