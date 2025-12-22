# tab_block_server.py
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

BASE = os.path.dirname(__file__)
CFG_PATH = os.path.join(BASE, "config.json")

def load_config():
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def is_within_time(start, end):
    now = datetime.now().time()
    s = datetime.strptime(start, "%H:%M").time()
    e = datetime.strptime(end, "%H:%M").time()
    if s <= e:
        return s <= now <= e
    return now >= s or now <= e

@app.route("/check", methods=["POST"])
def check_tab():
    data = request.get_json(force=True)
    cfg = load_config()

    if not cfg.get("schedule_enabled", False):
        return jsonify({"action": "allow"})

    if not is_within_time(cfg["default_study_start"], cfg["default_study_end"]):
        return jsonify({"action": "allow"})

    url = (data.get("url") or "").lower()
    title = (data.get("title") or "").lower()
    combined = url + " " + title

    # YouTube education exception
    if "youtube.com/watch" in url:
        for kw in cfg.get("youtube_education_keywords", []):
            if kw in combined:
                return jsonify({"action": "allow"})

    # Block distractions
    for kw in cfg.get("website_keywords_block", []):
        if kw in combined:
            return jsonify({
                "action": "warn_then_close",
                "seconds": cfg.get("grace_period_seconds", 5),
                "reason": kw
            })

    return jsonify({"action": "allow"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
