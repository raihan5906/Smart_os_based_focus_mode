import json
import os

CFG = os.path.join(os.path.dirname(__file__), "config.json")

class Classifier:
    def __init__(self):
        with open(CFG, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        self.study = set(a.lower() for a in cfg.get("study_whitelist", []))
        self.block = set(a.lower() for a in cfg.get("distraction_blacklist", []))
        self.keywords = [k.lower() for k in cfg.get("keyword_distraction", [])]

    def rule_classify(self, proc_name, window_title=""):
        name = (proc_name or "").lower()
        title = (window_title or "").lower()

        if name in self.study:
            return "study"

        if name in self.block:
            return "distraction"

        for kw in self.keywords:
            if kw and (kw in name or kw in title):
                return "distraction"

        return "unknown"
