print("MONITOR.PY LOADED")

import threading
import time
from datetime import datetime
import tkinter as tk
import json, os

from utils import get_active_window_info, terminate_process
from classifier import Classifier

CFG = os.path.join(os.path.dirname(__file__), "config.json")

SAFE_PROCESSES = {
    "chrome.exe",
    "msedge.exe",
    "brave.exe",
    "explorer.exe"
}

class Monitor:
    def __init__(self, app):
        self.app = app
        self.running = True
        self.handling = False
        self.classifier = Classifier()

    def start(self):
        threading.Thread(target=self.loop, daemon=True).start()

    def is_within_schedule(self, cfg):
        if not cfg.get("schedule_enabled"):
            return False

        now = datetime.now().time()
        start = datetime.strptime(cfg["default_study_start"], "%H:%M").time()
        end = datetime.strptime(cfg["default_study_end"], "%H:%M").time()

        if start <= end:
            return start <= now <= end
        return now >= start or now <= end

    def loop(self):
        while self.running:
            with open(CFG, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            if not self.is_within_schedule(cfg):
                time.sleep(1)
                continue

            info = get_active_window_info()
            if not info:
                time.sleep(1)
                continue

            name = info["name"]
            title = info["title"] or name

            if name in SAFE_PROCESSES:
                time.sleep(1)
                continue

            classification = self.classifier.rule_classify(name, title)

            if classification == "distraction" and not self.handling:
                self.handling = True
                self.app.root.after(0, lambda i=info: self.countdown_and_close(i))

            time.sleep(1)

    def countdown_and_close(self, info):
        pid = info["pid"]
        title = info["title"] or info["name"]

        popup = tk.Toplevel(self.app.root)
        popup.title("Warning")
        popup.attributes("-topmost", True)

        label = tk.Label(popup, font=("Segoe UI", 10), padx=20, pady=20)
        label.pack()

        def tick(sec):
            if sec == 0:
                popup.destroy()
                terminate_process(pid)
                self.app.append_log(f"{title} closed by Smart OS-Based Focus Manager")
                self.handling = False
                return

            label.config(
                text=f"{title}\nbeing closed by Smart OS-Based Focus Manager in {sec} seconds"
            )
            self.app.root.after(1000, lambda: tick(sec - 1))

        tick(5)
