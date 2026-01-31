# shared/protocol.py
from __future__ import annotations
from dataclasses import dataclass, fields
from typing import List, Literal, Union, Optional



# ---------- Commands (UI -> embedded) ----------
@dataclass(frozen=True, slots=True)
class testCommand:
    pass

@dataclass(frozen=True)
class LedSet:
    pin: int       
    on: bool

@dataclass(frozen=True)
class LedToggle:
    pin: int



Command = Union[testCommand, LedSet, LedToggle]

# ---------- Events (embedded -> UI) ----------

@dataclass(frozen=True)
class LedState:
    pin: int
    on: bool

@dataclass(frozen=True, slots=True)
class testEvent:
    pass

@dataclass(frozen=True, slots=True)
class Log:
    message: str

Event = Union[testEvent, LedState, Log]


# ---------- universal types ----------


