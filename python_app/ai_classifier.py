import json, os, pickle

class Classifier:
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.load_config()
        self.vectorizer = None
        self.model = None
        self.load_ai_model()

    def load_config(self):
        cfg_path = os.path.join(self.base_path, "config.json")
        with open(cfg_path, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.whitelist = set(a.lower() for a in self.cfg.get("study_whitelist", []))
        self.blacklist = set(a.lower() for a in self.cfg.get("distraction_blacklist", []))

    def load_ai_model(self):
        model_path = os.path.join(self.base_path, "focus_model.pkl")
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.vectorizer, self.model = pickle.load(f)

    def rule_classify(self, proc, title):
        p = (proc or "").lower()
        t = (title or "").lower()
        if p in self.whitelist: return "study"
        if p in self.blacklist: return "distraction"
        # Quick keyword check for non-browser apps
        for k in self.cfg.get("keyword_distraction", []):
            if k.lower() in p or k.lower() in t: return "distraction"
        return "allow"

    def ai_classify(self, metadata):
        if not self.model or not self.vectorizer:
            return "allow" # Fallback if AI isn't trained
        
        text = f"{metadata.get('title','')} {metadata.get('channel','')} {metadata.get('description','')}".lower()
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]