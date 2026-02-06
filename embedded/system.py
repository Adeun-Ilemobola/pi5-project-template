# embedded/system.py
from __future__ import annotations

from queue import Queue
from typing import Dict

from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory

from shared.Timer import Time  
from shared.protocol import (
    Command, Event, Log,
    testEvent, testCommand,
    LedSet, LedToggle, LedState,
)

# Use LGPIO for Pi 5 / Bookworm setups
Device.pin_factory = LGPIOFactory()


class System:
    def __init__(self, event_q: "Queue[Event]"):
        self.event_q = event_q

        # Cache LEDs here (BCM pin -> LED object)
        self._leds: Dict[int, LED] = {}

        # ---- Timer setup ----
        # Runs every 300ms by default; change as needed.
        # repeat=True means it keeps firing forever.
        # done() auto-consumes so it returns True only once per period.
        self.blink_timer = Time(duration_ms=300, tick_ms=20, repeat=True)

        # Example: pick a “heartbeat” LED pin
        self.heartbeat_pin = 12

        self.configure_all()

    def configure_all(self) -> None:
        """Home the system on startup."""
        self.event_q.put(Log("System configured."))

        led = self.get_led(self.heartbeat_pin)
        led.off()

        self.event_q.put(
            Log(
                f"System configured. LED test ready on GPIO{self.heartbeat_pin} "
                f"(BCM {self.heartbeat_pin})."
            )
        )

    def get_led(self, pin: int) -> LED:
        """Create/cache LED devices by BCM pin."""
        if pin not in self._leds:
            # If your LED wiring is active-low, set active_high=False
            self._leds[pin] = LED(pin, initial_value=False)
        return self._leds[pin]

    def handle(self, cmd: Command) -> None:
        """Handle an incoming command from the UI."""
        if isinstance(cmd, testCommand):
            self.event_q.put(testEvent())
            return

        if isinstance(cmd, LedSet):
            led = self.get_led(cmd.pin)
            led.on() if cmd.on else led.off()
            self.event_q.put(LedState(cmd.pin, led.value == 1))
            self.event_q.put(Log(f"LED on GPIO{cmd.pin} set to {'ON' if cmd.on else 'OFF'}"))
            return

        if isinstance(cmd, LedToggle):
            led = self.get_led(cmd.pin)
            led.toggle()
            self.event_q.put(LedState(cmd.pin, led.value == 1))
            self.event_q.put(Log(f"LED on GPIO{cmd.pin} toggled to {'ON' if led.value else 'OFF'}"))
            return

        self.event_q.put(Log(f"Unknown command: {cmd!r}"))

    def tick(self) -> None:
        """
        Called repeatedly by the worker thread.
        Use timers here to run periodic tasks without blocking.
        """

        # Advance timer using perf_counter (inside Timer.Time.tick())
        self.blink_timer.tick()

      
        if self.blink_timer.done():
            # Example periodic activity: blink heartbeat LED + log
            led = self.get_led(self.heartbeat_pin)
            led.toggle()

            self.event_q.put(Log(f"[timer] Heartbeat toggle on GPIO{self.heartbeat_pin}"))

        # You can still publish other periodic tick info if you want:
        # self.publish_test("tick")

    def publish_test(self, msg: str) -> None:
        """Publish info to the UI log."""
        self.event_q.put(Log(f"Test published: {msg}"))

    def shutdown(self) -> None:
        """Called by worker on application close."""
        for pin, led in self._leds.items():
            try:
                led.off()
                led.close()
            except Exception:
                pass

        self.event_q.put(Log("System shutdown complete."))
