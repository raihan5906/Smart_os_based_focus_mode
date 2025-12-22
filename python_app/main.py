import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json
from datetime import datetime
import monitor
import sys
import os
import subprocess
import time

# ================= EXE DETECTION =================
IS_EXE = getattr(sys, "frozen", False)
TAB_SERVER_STARTED = False

print("MAIN.PY STARTED")
print("WORKING DIR:", os.getcwd())
print("ARGV:", sys.argv)

# ================= RESOURCE PATH =================
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

CFG_PATH = resource_path("config.json")

# ================= TAB SERVER ENTRY MODE =================
# When EXE is launched with --run-tab-server, ONLY run Flask server
if "--run-tab-server" in sys.argv:
    from tab_block_server import app
    app.run(host="127.0.0.1", port=5000)
    sys.exit(0)


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart OS-Based Focus Manager")
        self.root.geometry("820x520")
        self.root.configure(bg="#f4f7fb")

        self.load_config()

        # ================= HEADER =================
        header = tk.Frame(root, bg="#2b6cb0", height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Smart OS-Based Focus Manager",
            fg="white",
            bg="#2b6cb0",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=16)

        # ================= CENTER =================
        center = tk.Frame(root, bg="#f4f7fb")
        center.pack(expand=True)

        tk.Label(
            center,
            text="Smart OS-Based Focus Manager",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f7fb"
        ).pack(pady=25)

        # ================= TIMER CARD =================
        card = tk.Frame(center, bg="white", padx=30, pady=20, bd=1, relief="groove")
        card.pack()

        tk.Label(
            card,
            text="Study Timer",
            font=("Segoe UI", 14, "bold"),
            bg="white"
        ).grid(row=0, column=0, columnspan=4, pady=(0, 15))

        self.start_var = tk.StringVar(value=self.cfg.get("default_study_start", "--:--"))
        self.end_var = tk.StringVar(value=self.cfg.get("default_study_end", "--:--"))

        tk.Label(card, text="Start Time", bg="white").grid(row=1, column=0, padx=10)
        tk.Label(
            card,
            textvariable=self.start_var,
            bg="white",
            font=("Segoe UI", 12, "bold")
        ).grid(row=1, column=1)

        tk.Label(card, text="End Time", bg="white").grid(row=1, column=2, padx=10)
        tk.Label(
            card,
            textvariable=self.end_var,
            bg="white",
            font=("Segoe UI", 12, "bold")
        ).grid(row=1, column=3)

        tk.Button(
            card,
            text="Edit Start Time",
            command=lambda: self.open_time_popup("start")
        ).grid(row=2, column=0, columnspan=2, pady=8)

        tk.Button(
            card,
            text="Edit End Time",
            command=lambda: self.open_time_popup("end")
        ).grid(row=2, column=2, columnspan=2, pady=8)

        tk.Button(
            card,
            text="Set Timer",
            bg="#2b6cb0",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=22,
            pady=6,
            command=self.save_timer
        ).grid(row=3, column=0, columnspan=4, pady=14)

        # ================= STATUS BAR =================
        status_frame = tk.Frame(root, bg="#edf2f7")
        status_frame.pack(fill="x")

        self.status_var = tk.StringVar()
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg="#edf2f7",
            font=("Segoe UI", 11),
            anchor="w"
        ).pack(side="left", padx=12)

        tk.Button(
            status_frame,
            text="Show Logs",
            command=self.toggle_logs
        ).pack(side="right", padx=12)

        # ================= LOGS =================
        self.log_box = ScrolledText(root, height=8, state="disabled")
        self.logs_visible = False
        self.log_store = []

        # ================= START TAB SERVER (SAFE) =================
        self.start_tab_server()

        # ================= MONITOR =================
        self.monitor = monitor.Monitor(self)
        self.monitor.start()

        self.update_status_loop()

    # ================= TAB SERVER START (NO RECURSION) =================
    def start_tab_server(self):
        global TAB_SERVER_STARTED

        if TAB_SERVER_STARTED:
            return

        try:
            if IS_EXE:
                # EXE mode: relaunch same EXE with special flag
                subprocess.Popen(
                    [sys.executable, "--run-tab-server"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Python mode
                subprocess.Popen(
                    ["python", "tab_block_server.py"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            TAB_SERVER_STARTED = True
            self.append_log("Tab block server started")

        except Exception as e:
            self.append_log(f"Tab server failed: {e}")

    # ================= TIME POPUP =================
    def open_time_popup(self, which):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Start Time" if which == "start" else "Edit End Time")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(
            popup,
            text=popup.title(),
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)

        current = self.start_var.get() if which == "start" else self.end_var.get()
        try:
            h, m = map(int, current.split(":"))
        except:
            h, m = 0, 0

        frame = tk.Frame(popup)
        frame.pack(pady=8)

        hour = tk.IntVar(value=h)
        minute = tk.IntVar(value=m)

        tk.Spinbox(frame, from_=0, to=23, width=4,
                   textvariable=hour, font=("Segoe UI", 16)).grid(row=0, column=0)
        tk.Label(frame, text=":", font=("Segoe UI", 16)).grid(row=0, column=1)
        tk.Spinbox(frame, from_=0, to=59, width=4,
                   textvariable=minute, font=("Segoe UI", 16)).grid(row=0, column=2)

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
            bg="#2b6cb0",
            fg="white",
            padx=16,
            pady=4,
            command=set_time
        ).pack(pady=10)

    # ================= CONFIG =================
    def load_config(self):
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)

    def save_config(self):
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, indent=4)

    # ================= TIMER =================
    def save_timer(self):
        self.cfg["default_study_start"] = self.start_var.get()
        self.cfg["default_study_end"] = self.end_var.get()
        self.cfg["schedule_enabled"] = True
        self.save_config()
        self.append_log("Study timer updated")

    # ================= STATUS =================
    def update_status_loop(self):
        self.load_config()
        try:
            now = datetime.now().time()
            start = datetime.strptime(self.cfg["default_study_start"], "%H:%M").time()
            end = datetime.strptime(self.cfg["default_study_end"], "%H:%M").time()

            active = start <= now <= end if start <= end else (now >= start or now <= end)

            self.status_var.set(
                "Smart OS-Based Focus Manager Active"
                if active else
                f"Status: Scheduled — Starts at {self.cfg['default_study_start']}"
            )
        except:
            self.status_var.set("Status: Idle — Waiting for schedule")

        self.root.after(1000, self.update_status_loop)

    # ================= LOGS =================
    def append_log(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_store.append(f"[{ts}] {text}")

    def toggle_logs(self):
        if self.logs_visible:
            self.log_box.pack_forget()
            self.logs_visible = False
        else:
            self.log_box.pack(fill="both", padx=12, pady=12)
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
