import pickle

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

def predict_review(text):
    vec = vectorizer.transform([text])
    prediction = model.predict(vec)[0]

    return {
        "prediction": "Fake" if prediction == 1 else "Genuine"
    }