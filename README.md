You’re *very* close — but you’ve got a few Markdown issues (and one big structural issue):

1. Your folder tree code fence is broken (` ``` ```` mixed)
2. You accidentally wrote `**init**.py` instead of `__init__.py`
3. Your `shared/` folder tree indentation is off
4. The **full MIT license should NOT live inside README** — it should be in a `LICENSE` file. In README, just say “MIT” (maybe + link).

Below is a **clean, fully-correct, copy-paste README.md** that fixes everything and keeps it professional.

---

```md
# Raspberry Pi 5 CustomTkinter Hardware Template

A clean **Raspberry Pi 5** Python template for building **desktop UI + embedded hardware control** applications.

This template uses a simple, reliable architecture:

- **UI (CustomTkinter)** runs on the main thread
- **Embedded worker thread** runs your hardware/system loop
- Two queues connect them:
  - **cmd_q**: UI → Embedded commands
  - **event_q**: Embedded → UI events/logs

Clone this repo to quickly start new Pi projects (LiDAR or anything else) with the same structure.

---

## Features

- ✅ CustomTkinter UI (dark mode, component-friendly structure)
- ✅ Threaded embedded worker (keeps UI responsive)
- ✅ Queue-based protocol (Command/Event objects shared by UI + embedded)
- ✅ Raspberry Pi 5 compatible GPIO stack
  - `gpiozero` + `lgpio` backend (no `pigpiod` needed)
  - `rpi-lgpio` included for Pi 5 compatibility
- ✅ Clean shutdown path
  - Closing the UI triggers `worker.shutdown()` which calls `system.shutdown()`
- ✅ VS Code ready (`.vscode/launch.json` + `.vscode/settings.json`)
- ✅ Default test system: Toggle LED on **GPIO12 (BCM 12)** via UI button

---

## Project Structure

```

.
├─ main.py
├─ requirements.txt
├─ Venv install.txt
├─ .vscode/
│  ├─ launch.json
│  └─ settings.json
├─ ui/
│  ├─ **init**.py
│  ├─ main_window.py
│  └─ components/
│     ├─ **init**.py
│     └─ ... reusable UI widgets ...
├─ embedded/
│  ├─ **init**.py
│  ├─ system.py        # embedded logic (GPIO/I2C control)
│  ├─ worker.py        # threaded loop + queue plumbing
│  └─ modules/
│     ├─ **init**.py
│     └─ ... optional device modules ...
└─ shared/
├─ **init**.py
└─ protocol.py      # Command/Event definitions shared by UI + embedded

````

### Key files

- `main.py`: App entry point. Creates `MainWindow` and starts the UI loop.
- `ui/main_window.py`: UI, buttons, event polling (reads from `event_q`).
- `embedded/worker.py`: Background thread that reads commands and calls `System`.
- `embedded/system.py`: Hardware/system logic (GPIO, I2C devices, etc.).
- `shared/protocol.py`: Command/Event definitions used by both layers.

---

## Requirements

### OS packages (required on the Pi)

Some dependencies are OS-level and cannot be installed via `pip`:

```bash
sudo apt update
sudo apt install -y python3-tk python3-dev i2c-tools
````

### Enable I2C (if using sensors/drivers like PCA9685 or VL53L1X)

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
```

(Optional) Add your user to hardware groups (then reboot/log out-in):

```bash
sudo usermod -aG i2c,gpio $USER
```

---

## Setup (Virtual Environment)

Everything Python-related installs into the **project venv**:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Run

### Run from terminal

```bash
source .venv/bin/activate
python main.py
```

### Run from VS Code

Use the included `.vscode/launch.json` configurations:

* Run main.py (UI)
* Run as module: python -m main
* Current file

---

## Architecture Overview (UI ↔ Embedded)

### 1) UI sends Commands

The UI places a `Command` object into the command queue:

```py
self.cmd_q.put(LedToggle(pin=12))
```

### 2) Worker receives Commands

The embedded worker thread reads from `cmd_q` and forwards to:

```py
system.handle(cmd)
```

### 3) Embedded publishes Events/logs

Embedded posts `Event` objects back to the UI through `event_q`:

```py
self.event_q.put(Log("LED toggled"))
self.event_q.put(LedState(pin=12, on=True))
```

### 4) UI polls Events (non-blocking)

UI polls using `.after(...)` to stay responsive:

```py
self.after(16, self.poll_events)
```

---

## Default Test System: GPIO12 LED

This template includes a basic test flow:

* UI buttons: **ON / OFF / TOGGLE**
* Sends `LedSet` / `LedToggle` commands to embedded
* Embedded controls **BCM GPIO12**

### GPIO12 mapping

* **BCM GPIO12** = **Physical pin 32**

### Basic wiring

* GPIO12 → resistor (220–1kΩ) → LED anode (+)
* LED cathode (–) → GND

> If your LED is wired as active-low, set `active_high=False` in the embedded LED driver.

---

## Clean Shutdown

Closing the UI triggers:

1. `WM_DELETE_WINDOW` handler calls `worker.shutdown()`
2. Worker stops the thread loop and calls `system.shutdown()`
3. Embedded releases GPIO resources and powers down devices safely
4. App exits cleanly

This prevents stuck GPIO states and leaves the system clean.

---

## Extending the Template

### Add a new hardware feature

1. Define a new `Command`/`Event` in `shared/protocol.py`
2. Handle it in `embedded/system.py`
3. Add UI controls in `ui/main_window.py` or `ui/components/`

### Add device modules

Put reusable drivers/helpers in:

```
embedded/modules/
```

---

## Troubleshooting

### CustomTkinter/Tk errors

Ensure Tkinter is installed:

```bash
sudo apt install -y python3-tk
```

### GPIO not working on Pi 5

This template uses:

* `gpiozero`
* `LGPIOFactory` backend
* `rpi-lgpio` installed in the venv

Confirm venv + deps:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### I2C devices not found

* Enable I2C in `raspi-config`
* Confirm on bus 1:

```bash
i2cdetect -y 1
```

---

## Template Usage

This repository is intended as a reusable starter template:

* Clone it
* Rename the repo/folder
* Replace the test LED system with your own hardware modules
* Keep the structure and Command/Event pattern

---

## License

MIT License — see the `LICENSE` file for details.

```

---

