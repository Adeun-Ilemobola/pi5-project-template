import time

class Time:
    """Simple timer utility for periodic events."""
    __slots__ = ("tick_sec", "target", "repeat", "last", "acc")

    def __init__(self, duration_ms, tick_ms=15, repeat=True):
        self.tick_sec = tick_ms / 1000.0
        self.target = float(duration_ms) / 1000.0  # seconds
        self.repeat = repeat

        self.last = time.perf_counter()
        self.acc = 0.0  # accumulated seconds

    def tick(self):
        """Call once per outer loop."""
        now = time.perf_counter()
        self.acc += (now - self.last)
        self.last = now

    def done(self):
        """
        Auto-consume:
        - If not reached target: False
        - If reached: True (and consumes the event)
          * repeat=True  -> subtract target and keep running
          * repeat=False -> latch at target (fires once)
        """
        if self.acc < self.target:
            return False

        if self.repeat:
            # consume exactly one trigger (event). Keep remainder for accuracy.
            self.acc -= self.target
            return True
        else:
            # one-shot: consume once, then latch so it won't fire again
            self.acc = -1e30
            return True

    def reset(self):
        self.last = time.perf_counter()
        self.acc = 0.0
