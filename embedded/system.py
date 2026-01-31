# embedded/system.py
from __future__ import annotations
import random
from typing import Dict, List
from queue import Queue

from shared.protocol import (
    Command, Event, Log,
    testEvent, testCommand,
    LedSet, LedToggle, LedState,
)

from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()
class System:
    def __init__(self, event_q: "Queue[Event]"):
        self.event_Queue = event_q
        self.leds: Dict[int, LED] = {}
        self.configure_all()

    def configure_all(self) -> None:
        """Home the system on startup."""
        self.event_Queue.put(Log("System configured."))
        led = self.get_led(12)
        led.off()
        self.event_Queue.put(Log("System configured. LED test ready on GPIO12 (BCM 12)."))

        
    def get_led(self, pin: int) -> LED:
        """Create/cache LED devices by BCM pin."""
        if pin not in self._leds:
            # If your LED wiring is active-low, set active_high=False
            self._leds[pin] = LED(pin, initial_value=False)
        return self._leds[pin]

    def handle(self, cmd: Command) -> None:
        """Handle an incoming command from the UI."""
        if isinstance(cmd, testCommand):
            self.event_Queue.put(testEvent())



        elif isinstance(cmd, LedSet):
            led = self.get_led(cmd.pin)
            led.on() if cmd.on else led.off()
            self.event_Queue.put(LedState(cmd.pin, led.value == 1))
            self.event_Queue.put(Log(f"LED on GPIO{cmd.pin} set to {'ON' if cmd.on else 'OFF'}"))
            

        elif isinstance(cmd, LedToggle):
            led = self.get_led(cmd.pin)
            led.toggle()
            self.event_Queue.put(LedState(cmd.pin, led.value == 1))
            self.event_Queue.put(Log(f"LED on GPIO{cmd.pin} toggled to {'ON' if led.value else 'OFF'}"))
            

        elif isinstance(cmd, LedToggle):
            led = self.get_led(cmd.pin)
            led.toggle()
            self.event_Queue.put(LedState(cmd.pin, led.value == 1))

        else:
            self.event_Queue.put(Log(f"Unknown command: {cmd!r}"))

    def tick(self) -> None:
        """Called repeatedly by the worker thread."""
        self.publish_Test("tick")

  
    def publish_Test(self, something: str) -> None:
        """Publish  info to the UI log."""
        self.event_Queue.put(Log(f"Test published: {something}"))

    def shutdown(self) -> None:
        """Called by worker on application close."""
        for pin, led in self._leds.items():
            try:
                led.off()
                led.close()
            except Exception:
                pass
        self.event_q.put(Log("System shutdown complete."))
   
    

