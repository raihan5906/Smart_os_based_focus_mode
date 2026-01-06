from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os
from datetime import datetime
from classifier import Classifier

app = Flask(__name__)
CORS(app) # Prevents browser blocking the request
classifier = Classifier()

def is_study_time():
    cfg = classifier.cfg
    if not cfg.get("schedule_enabled", True): return False
    now = datetime.now().time()
    s = datetime.strptime(cfg["default_study_start"], "%H:%M").time()
    e = datetime.strptime(cfg["default_study_end"], "%H:%M").time()
    return s <= now <= e if s <= e else now >= s or now <= e

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    if not is_study_time():
        return jsonify(action="allow")

    # AI Classification for YouTube
    if "youtube.com/watch" in data.get("url", ""):
        verdict = classifier.ai_classify(data)
        if verdict == "distraction":
            return jsonify(action="warn_then_close", 
                           seconds=classifier.cfg.get("grace_period_seconds", 5),
                           reason="AI: Distracting Content")

    # Keyword check for other sites
    for k in classifier.cfg.get("website_keywords_block", []):
        if k.lower() in data.get("url", "").lower() or k.lower() in data.get("title", "").lower():
            return jsonify(action="warn_then_close", 
                           seconds=classifier.cfg.get("grace_period_seconds", 5),
                           reason=f"Blocked site: {k}")

    return jsonify(action="allow")

if __name__ == "__main__":
    app.run(port=5000, debug=False, threaded=True)