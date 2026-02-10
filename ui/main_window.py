"""Main application window. Ui/main_window.py """
# import queue
import random
import queue
import customtkinter as ctk

from embedded.worker import HardwareWorker
from shared.protocol import LedToggle, Log, testCommand ,testEvent , Command, LedSet




class MainWindow(ctk.CTk):
    def __init__(self, title="Pi Control Panel", size=(1000, 900)):
        super().__init__()
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")

        # Queues
        self.cmd_q: "queue.Queue" = queue.Queue()
        self.event_q: "queue.Queue" = queue.Queue()

        # Worker thread
        self.worker = HardwareWorker(self.cmd_q, self.event_q)
        self.worker.start()


          # --- Test LED UI ---
        test_frame = ctk.CTkFrame(self)
        test_frame.pack(padx=12, pady=12, fill="x")

        ctk.CTkLabel(test_frame, text="Test LED (GPIO12 / BCM 12)").pack(anchor="w", padx=12, pady=(12, 6))

        row = ctk.CTkFrame(test_frame)
        row.pack(padx=12, pady=(0, 12), fill="x")

        ctk.CTkButton(row, text="ON", command=lambda: self.send_cmd(LedSet(12, True))).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="OFF", command=lambda: self.send_cmd(LedSet(12, False))).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="TOGGLE", command=lambda: self.send_cmd(LedToggle(12))).pack(side="left")


    

        # Start polling events
        self.after(15,self.poll_events)

        # Proper close handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    

    def send_cmd(self, cmd:Command):
        self.cmd_q.put(cmd)

    def poll_events(self):
        while True:
            try:
                ev = self.event_q.get_nowait()
            except queue.Empty:
                print("No more events.")
                break

            if isinstance(ev, Log):
                print(ev.message)
            else:
                print(f"Unknown event: {ev!r}")

        # Schedule next poll
        self.after(16, self.poll_events)

    def on_close(self):
        try:
            self.worker.shutdown()
        except Exception:
            pass
        self.destroy()
