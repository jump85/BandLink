import random

class AIEngine:

    def __init__(self):
        self.mode = "ambient"

    def update(self, energy, beat):
        avg = sum(energy)/3

        if avg < 0.3:
            self.mode = "ambient"
        elif avg < 0.6:
            self.mode = "groove"
        else:
            self.mode = "aggressive"

        if beat and random.random() < 0.2:
            self.mode = random.choice(["ambient","groove","aggressive"])

        return self.mode