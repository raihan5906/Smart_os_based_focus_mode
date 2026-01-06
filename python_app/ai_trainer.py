import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Add more examples here to make the AI smarter!
data = [
    ("python programming tutorial for beginners", "study"),
    ("calculus 1 full course university", "study"),
    ("physics lecture quantum mechanics", "study"),
    ("how to build a website html css", "study"),
    ("minecraft survival let's play", "distraction"),
    ("official music video 4k pop", "distraction"),
    ("funny cat videos compilation", "distraction"),
    ("league of legends gameplay highlights", "distraction"),
    ("gta 5 modding tutorial fun", "distraction")
]

def train_model():
    texts, labels = zip(*data)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)
    with open("focus_model.pkl", "wb") as f:
        pickle.dump((vectorizer, model), f)
    print("AI 'Brain' (focus_model.pkl) created successfully!")

if __name__ == "__main__":
    train_model()