from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
from utils import is_within_time

BASE = os.path.dirname(__file__)
CFG_PATH = os.path.join(BASE, "config.json")
LOG_PATH = os.path.join(BASE, "browser.log")

app = Flask(__name__)


def load_cfg():
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def check_tab_block(title, url, cfg):
    title_l = (title or "").lower()
    url_l = (url or "").lower()

    # ===== YOUTUBE LOGIC =====
    if "youtube.com" in url_l:
        if "watch" in url_l:
            for edu in cfg.get("youtube_education_keywords", []):
                if edu.lower() in title_l:
                    return False, None

            for bad in cfg.get("keyword_distraction", []):
                if bad.lower() in title_l:
                    return True, bad

        return False, None

    # ===== OTHER WEBSITES =====
    combined = f"{title_l} {url_l}"
    for kw in cfg.get("website_keywords_block", []):
        if kw.lower() in combined:
            return True, kw

    return False, None


@app.route("/check", methods=["POST"])
def check():
    data = request.get_json(force=True)
    title = data.get("title", "")
    url = data.get("url", "")

    cfg = load_cfg()

    if not cfg.get("schedule_enabled"):
        return jsonify({"action": "allow"})

    if not is_within_time(cfg.get("default_study_start"), cfg.get("default_study_end")):
        return jsonify({"action": "allow"})

    blocked, keyword = check_tab_block(title, url, cfg)

    if blocked:
        site = url.split("/")[2] if "://" in url else url
        write_log(f"Blocked tab: {site} ({keyword})")

        return jsonify({
            "action": "warn_then_close",
            "keyword": site,
            "seconds": cfg.get("grace_period_seconds", 5)
        })

    return jsonify({"action": "allow"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
