import threading, time, json, os
from datetime import datetime
from utils import get_active_window_info, terminate_process
from classifier import Classifier
from notifier import show_info_popup

BASE = os.path.dirname(__file__)
CFG_PATH = os.path.join(BASE, "config.json")
BROWSERS = {"chrome.exe", "msedge.exe", "brave.exe", "opera.exe"}

class Monitor:
    def __init__(self, app):
        self.app = app
        self.classifier = Classifier()
        self.running = True

    def start(self):
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while self.running:
            with open(CFG_PATH) as f:
                cfg = json.load(f)

            if not cfg.get("schedule_enabled"):
                time.sleep(1); continue

            now = datetime.now().time()
            s = datetime.strptime(cfg["default_study_start"], "%H:%M").time()
            e = datetime.strptime(cfg["default_study_end"], "%H:%M").time()
            active = s <= now <= e if s <= e else (now >= s or now <= e)
            if not active:
                time.sleep(1); continue

            info = get_active_window_info()
            if not info or info["name"] in BROWSERS:
                time.sleep(1); continue

            if self.classifier.rule_classify(info["name"], "", info["title"]) == "distraction":
                self.countdown_close(info)
                time.sleep(6)

            time.sleep(1)

    def countdown_close(self, info):
        title = info["title"] or info["name"]
        pid = info["pid"]

        def tick(sec):
            if sec == 0:
                terminate_process(pid)
                self.app.append_log(f"{title} closed")
                return
            self.app.root.after(
                0,
                lambda: show_info_popup(
                    self.app.root, "Warning",
                    f"{title}\nbeing closed by Smart OS-Based Focus Manager in {sec} seconds",
                    timeout_ms=1000
                )
            )
            self.app.root.after(1000, lambda: tick(sec - 1))

        tick(5)
