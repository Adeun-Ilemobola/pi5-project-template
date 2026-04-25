# Raspberry Pi 5 CustomTkinter Hardware Template

A reusable **Raspberry Pi 5 desktop + hardware-control template** for building clean Python applications that combine a modern GUI with embedded system logic.

This starter gives you a reliable project structure where the interface stays responsive while hardware work runs safely in the background.

---

## ⟡ What This Template Gives You

This project is built around a simple but powerful idea:

> Keep the UI clean, keep hardware control isolated, and let both sides communicate through queues.

The architecture separates the application into three main layers:

| Layer       | Purpose                                                       |
| ----------- | ------------------------------------------------------------- |
| `ui/`       | CustomTkinter desktop interface                               |
| `embedded/` | Hardware logic, GPIO control, device modules, and worker loop |
| `shared/`   | Command/Event protocol shared between UI and embedded code    |

The result is a Raspberry Pi application that is easier to expand, debug, and reuse across future hardware projects.

---

## ⚙️ Core Features

* **CustomTkinter UI** with a clean dark-mode friendly structure
* **Threaded embedded worker** so the UI does not freeze during hardware/system tasks
* **Queue-based communication** between UI and embedded logic
* **Command/Event protocol** shared across the whole app
* **Raspberry Pi 5 GPIO compatibility** using `gpiozero`, `lgpio`, and `rpi-lgpio`
* **No `pigpiod` requirement** for the default GPIO setup
* **Clean shutdown path** for safely releasing GPIO and system resources
* **VS Code ready** with included launch and settings files
* **Default test system** for controlling an LED on **BCM GPIO12**

---

## 🧭 Architecture Overview

The application uses two queues:

```text
UI Thread                         Embedded Worker Thread
─────────                         ──────────────────────
CustomTkinter UI                  Hardware/System Loop
     │                                      │
     │  Command objects                     │
     ├────────────── cmd_q ───────────────▶ │
     │                                      │
     │  Event / Log objects                 │
     ◀──────────── event_q ────────────────┤
     │                                      │
UI updates safely                 GPIO / I2C / Modules run here
```

### How the flow works

1. The UI sends a `Command` into `cmd_q`.
2. The embedded worker reads the command.
3. The worker forwards it to the system layer.
4. The system performs the hardware action.
5. The embedded layer sends `Event` or `Log` objects back through `event_q`.
6. The UI polls events using `.after(...)` so the interface stays responsive.

---

## 🗂️ Project Structure

```text
.
├─ main.py
├─ requirements.txt
├─ Venv install.txt
├─ .vscode/
│  ├─ launch.json
│  └─ settings.json
├─ ui/
│  ├─ __init__.py
│  ├─ main_window.py
│  └─ components/
│     ├─ __init__.py
│     └─ ... reusable UI widgets ...
├─ embedded/
│  ├─ __init__.py
│  ├─ system.py        # Embedded logic: GPIO, I2C, device control
│  ├─ worker.py        # Threaded loop + queue plumbing
│  └─ modules/
│     ├─ __init__.py
│     └─ ... optional hardware/device modules ...
└─ shared/
   ├─ __init__.py
   └─ protocol.py      # Command/Event definitions shared by UI + embedded
```

---

## 🔩 Important Files

| File                 | Role                                                               |
| -------------------- | ------------------------------------------------------------------ |
| `main.py`            | App entry point. Creates the UI and starts the main loop.          |
| `ui/main_window.py`  | Main CustomTkinter window, button handlers, and event polling.     |
| `embedded/worker.py` | Background thread that reads commands and sends events back.       |
| `embedded/system.py` | Hardware/system logic such as GPIO, I2C, sensors, motors, or LEDs. |
| `shared/protocol.py` | Shared command and event objects used by both layers.              |

---

## 🧱 Requirements

### Raspberry Pi OS packages

Some dependencies must be installed at the OS level, not through `pip`:

```bash
sudo apt update
sudo apt install -y python3-tk python3-dev i2c-tools
```

### Enable I2C if needed

Enable I2C if your project uses sensors or drivers such as PCA9685, VL53L1X, OLED displays, IMUs, or other I2C hardware.

```bash
sudo raspi-config
```

Then go to:

```text
Interface Options → I2C → Enable
```

Optional hardware group setup:

```bash
sudo usermod -aG i2c,gpio $USER
```

After changing groups, reboot or log out and back in.

---

## 🧪 Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade the Python tooling:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

### Run from terminal

```bash
source .venv/bin/activate
python main.py
```

### Run from VS Code

The project includes VS Code launch configurations for:

* `Run main.py`
* `Run as module: python -m main`
* `Current file`

Open the Run and Debug panel in VS Code and choose the configuration you want.

---

## 🛰️ Command/Event Protocol

The UI and embedded side communicate using shared protocol objects from `shared/protocol.py`.

### UI sends commands

Example: sending a command from the UI to toggle an LED.

```python
self.cmd_q.put(LedToggle(pin=12))
```

### Worker receives commands

The embedded worker reads from `cmd_q` and passes the command into the system layer.

```python
system.handle(cmd)
```

### Embedded publishes events

The embedded system can report logs, state changes, sensor updates, or status messages back to the UI.

```python
self.event_q.put(Log("LED toggled"))
self.event_q.put(LedState(pin=12, on=True))
```

### UI polls events safely

The UI polls `event_q` using CustomTkinter/Tkinter’s `.after(...)` method.

```python
self.after(16, self.poll_events)
```

This avoids blocking the UI thread.

---

## 💡 Default Test System: GPIO12 LED

The template includes a small hardware test using an LED connected to **BCM GPIO12**.

### Included UI controls

* `ON`
* `OFF`
* `TOGGLE`

These buttons send `LedSet` and `LedToggle` commands to the embedded layer.

### GPIO12 pin mapping

| GPIO Mode  | Pin             |
| ---------- | --------------- |
| BCM GPIO12 | Physical pin 32 |

### Basic wiring

```text
GPIO12 ── resistor 220Ω–1kΩ ── LED anode (+)
LED cathode (-) ────────────── GND
```

If your LED is wired as active-low, set the LED driver to:

```python
active_high=False
```

---

## 🧯 Clean Shutdown

The app includes a safe shutdown path so hardware resources are released properly.

When the UI closes:

1. The `WM_DELETE_WINDOW` handler runs.
2. The UI calls `worker.shutdown()`.
3. The worker exits its loop.
4. The worker calls `system.shutdown()`.
5. GPIO/device resources are released.
6. The application exits cleanly.

This helps prevent stuck GPIO states, locked resources, and messy exits.

---

## 🛠️ Extending the Template

### Add a new hardware feature

1. Define a new `Command` and/or `Event` in `shared/protocol.py`.
2. Handle the command inside `embedded/system.py`.
3. Add UI controls in `ui/main_window.py` or inside `ui/components/`.
4. Send events back to the UI when the hardware state changes.

### Add reusable device modules

Place drivers, wrappers, and hardware helpers inside:

```text
embedded/modules/
```

Good examples of modules:

* LED controller
* Servo controller
* LiDAR reader
* I2C sensor wrapper
* Motor driver
* Display driver
* GPIO utility helpers

---

## 🩺 Troubleshooting

### CustomTkinter or Tkinter errors

If the UI fails because Tkinter is missing, install it with:

```bash
sudo apt install -y python3-tk
```

### GPIO not working on Raspberry Pi 5

This template is designed for Pi 5 GPIO compatibility using:

* `gpiozero`
* `LGPIOFactory`
* `rpi-lgpio`

Confirm your virtual environment is active and dependencies are installed:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### I2C devices not detected

First confirm I2C is enabled:

```bash
sudo raspi-config
```

Then scan bus 1:

```bash
i2cdetect -y 1
```

If nothing appears, check:

* SDA/SCL wiring
* 3.3V vs 5V compatibility
* Ground connection
* Device address
* Pull-up requirements
* Whether the sensor/module is powered correctly

---

## ♻️ Template Usage

This repo is meant to be reused as a starter base for future Raspberry Pi hardware applications.

Typical workflow:

1. Clone the repo.
2. Rename the folder/repository.
3. Keep the UI ↔ worker ↔ system pattern.
4. Replace the default LED test with your real hardware modules.
5. Expand `shared/protocol.py` as your command/event language grows.

---

## 🧬 Good Project Fit

This template works well for projects such as:

* Raspberry Pi control panels
* Sensor dashboards
* LiDAR test rigs
* Motor or servo controllers
* GPIO testing tools
* Embedded desktop utilities
* Hardware debugging interfaces
* Small lab/robotics control apps

---

## 📜 License

MIT License — see the `LICENSE` file for details.
