import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json
from datetime import datetime
import monitor
import sys
import os
import subprocess
import time

print("MAIN.PY STARTED")

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

CFG_PATH = resource_path("config.json")

# ---------------- APP ---------------- #
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart OS-Based Focus Manager")
        self.root.geometry("960x560")
        self.root.configure(bg="#eef1f7")

        self.load_config()

        # ================= HEADER =================
        header = tk.Frame(root, bg="#3b6edc", height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Smart Focus Manager",
            fg="white",
            bg="#3b6edc",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=20)

        self.active_badge = tk.Label(
            header,
            text="ACTIVE",
            fg="#1b7f2a",
            bg="#d6f5df",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=4
        )
        self.active_badge.pack(side="right", padx=20)

        # ================= MAIN AREA =================
        body = tk.Frame(root, bg="#eef1f7")
        body.pack(expand=True, fill="both")

        # ================= CARD =================
        card = tk.Frame(
            body,
            bg="white",
            padx=35,
            pady=25,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d9dbe1"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="Study Timer",
            bg="white",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 18))

        # Time values
        self.start_var = tk.StringVar(value=self.cfg.get("default_study_start", "--:--"))
        self.end_var = tk.StringVar(value=self.cfg.get("default_study_end", "--:--"))

        time_frame = tk.Frame(card, bg="white")
        time_frame.pack(pady=10)

        # Start time
        tk.Label(time_frame, text="Start time", bg="white").grid(row=0, column=0, padx=10)
        tk.Label(
            time_frame,
            textvariable=self.start_var,
            bg="#f3f6fb",
            width=8,
            font=("Segoe UI", 11, "bold"),
            relief="groove"
        ).grid(row=1, column=0, pady=4)

        tk.Button(
            time_frame,
            text="Edit Start",
            command=lambda: self.open_time_popup("start"),
            bg="#e9edf5",
            relief="flat"
        ).grid(row=2, column=0, pady=6)

        # End time
        tk.Label(time_frame, text="End time", bg="white").grid(row=0, column=1, padx=20)
        tk.Label(
            time_frame,
            textvariable=self.end_var,
            bg="#f3f6fb",
            width=8,
            font=("Segoe UI", 11, "bold"),
            relief="groove"
        ).grid(row=1, column=1, pady=4)

        tk.Button(
            time_frame,
            text="Edit End",
            command=lambda: self.open_time_popup("end"),
            bg="#e9edf5",
            relief="flat"
        ).grid(row=2, column=1, pady=6)

        # Set timer
        tk.Button(
            card,
            text="Set Timer",
            bg="#3b6edc",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=40,
            pady=8,
            relief="flat",
            command=self.save_timer
        ).pack(pady=20)

        # ================= FOOTER =================
        footer = tk.Frame(root, bg="#eef1f7")
        footer.pack(fill="x", pady=6)

        self.status_var = tk.StringVar(value="Focus Mode Active")

        tk.Label(
            footer,
            textvariable=self.status_var,
            bg="#eef1f7",
            fg="#1b7f2a",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=15)

        tk.Button(
            footer,
            text="View Logs",
            command=self.toggle_logs,
            relief="flat",
            bg="#eef1f7",
            fg="#3b6edc"
        ).pack(side="right", padx=15)

        # ================= LOGS =================
        self.log_box = ScrolledText(root, height=8, state="disabled")
        self.logs_visible = False
        self.log_store = []

        # ================= SERVICES =================
        self.start_tab_server()
        self.monitor = monitor.Monitor(self)
        self.monitor.start()

        self.update_status_loop()

    # ---------------- TAB SERVER ---------------- #
    def start_tab_server(self):
        try:
            subprocess.Popen(
                [sys.executable, resource_path("tab_block_server.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.append_log("Tab block server started")
        except Exception as e:
            self.append_log(f"Tab server error: {e}")

    # ---------------- TIME POPUP ---------------- #
    def open_time_popup(self, which):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Time")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(
            popup,
            text="Edit Start Time" if which == "start" else "Edit End Time",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)

        frame = tk.Frame(popup)
        frame.pack(pady=10)

        hour = tk.IntVar()
        minute = tk.IntVar()

        tk.Spinbox(frame, from_=0, to=23, width=4, textvariable=hour,
                   font=("Segoe UI", 14)).grid(row=0, column=0)
        tk.Label(frame, text=":", font=("Segoe UI", 14)).grid(row=0, column=1)
        tk.Spinbox(frame, from_=0, to=59, width=4, textvariable=minute,
                   font=("Segoe UI", 14)).grid(row=0, column=2)

        def set_time():
            val = f"{hour.get():02d}:{minute.get():02d}"
            if which == "start":
                self.start_var.set(val)
            else:
                self.end_var.set(val)
            popup.destroy()

        tk.Button(
            popup,
            text="Set Time",
            bg="#3b6edc",
            fg="white",
            padx=20,
            pady=6,
            command=set_time
        ).pack(pady=12)

    # ---------------- CONFIG ---------------- #
    def load_config(self):
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)

    def save_config(self):
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, indent=4)

    # ---------------- TIMER ---------------- #
    def save_timer(self):
        self.cfg["default_study_start"] = self.start_var.get()
        self.cfg["default_study_end"] = self.end_var.get()
        self.cfg["schedule_enabled"] = True
        self.save_config()
        self.append_log("Study timer updated")

    # ---------------- STATUS ---------------- #
    def update_status_loop(self):
        try:
            now = datetime.now().time()
            start = datetime.strptime(self.cfg["default_study_start"], "%H:%M").time()
            end = datetime.strptime(self.cfg["default_study_end"], "%H:%M").time()

            active = start <= now <= end if start <= end else (now >= start or now <= end)
            self.status_var.set(
                "Focus Mode Active" if active else "Waiting for scheduled time"
            )
        except:
            self.status_var.set("Waiting for schedule")

        self.root.after(1000, self.update_status_loop)

    # ---------------- LOGS ---------------- #
    def append_log(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_store.append(f"[{ts}] {text}")

    def toggle_logs(self):
        if self.logs_visible:
            self.log_box.pack_forget()
            self.logs_visible = False
        else:
            self.log_box.pack(fill="both", padx=15, pady=10)
            self.log_box.config(state="normal")
            self.log_box.delete("1.0", "end")
            for line in self.log_store:
                self.log_box.insert("end", line + "\n")
            self.log_box.config(state="disabled")
            self.logs_visible = True


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
