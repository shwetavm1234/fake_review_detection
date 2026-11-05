# import pandas as pd
# import re
# import string
# import pickle
# import json

# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score


# # TEXT CLEANING FUNCTION
# def clean_text(text):
#     text = str(text).lower()
#     text = re.sub(r'\d+', '', text)
#     text = text.translate(str.maketrans('', '', string.punctuation))
#     return text

# # csv - 
# csv_data = pd.read_csv("fake_reviews.csv")
# if "review" not in csv_data.columns or "label" not in csv_data.columns:
#     raise ValueError(
#         "CSV must contain 'review' and 'label' columns"
#     )

# # json - 
# # json_data = pd.read_json("reviews.json")
# with open("fake_reviews.json", "r", encoding="utf-8") as f:
#     json_data = pd.DataFrame(json.load(f))

# if "review" not in json_data.columns or "label" not in json_data.columns:
#     raise ValueError(
#         "JSON must contain 'review' and 'label' columns"
#     )


# data = pd.concat(
#     [csv_data, json_data],
#     ignore_index=True
# )

# data = data.dropna(subset=["review", "label"])

# data = data.drop_duplicates(subset=["review", "label"])

# print("CSV rows:", len(csv_data))
# print("JSON rows:", len(json_data))
# print("Combined rows:", len(data))

# print("\nLabel distribution:")
# print(data["label"].value_counts())
# print("\nSample reviews for each label:")
# print(data.groupby("label")["review"].first())


# data["review"] = data["review"].apply(clean_text)
# X = data["review"]
# y = data["label"]

# X_train, X_test, y_train, y_test = train_test_split(
#     X,
#     y,
#     test_size=0.2,
#     random_state=42,
#     stratify=y
# )

# vectorizer = TfidfVectorizer(
#     stop_words="english",
#     max_features=5000,
#     ngram_range=(1, 2)
# )

# X_train_vec = vectorizer.fit_transform(X_train)
# X_test_vec = vectorizer.transform(X_test)

# lr_model = LogisticRegression(max_iter=1000)
# lr_model.fit(X_train_vec, y_train)

# nb_model = MultinomialNB()
# nb_model.fit(X_train_vec, y_train)

# rf_model = RandomForestClassifier(
#     n_estimators=100,
#     random_state=42
# )

# rf_model.fit(X_train_vec, y_train)


# # EVALUATE ALL MODELS
# lr_acc = accuracy_score(
#     y_test,
#     lr_model.predict(X_test_vec)
# )

# nb_acc = accuracy_score(
#     y_test,
#     nb_model.predict(X_test_vec)
# )

# rf_acc = accuracy_score(
#     y_test,
#     rf_model.predict(X_test_vec)
# )


# # DISPLAY ACCURACY
# print("\nModel Accuracy:")

# print(
#     f"Logistic Regression Accuracy: "
#     f"{lr_acc * 100:.2f}%"
# )

# print(
#     f"Naive Bayes Accuracy: "
#     f"{nb_acc * 100:.2f}%"
# )

# print(
#     f"Random Forest Accuracy: "
#     f"{rf_acc * 100:.2f}%"
# )


# # SAVE MODELS
# pickle.dump(
#     lr_model,
#     open("lr_model.pkl", "wb")
# )

# pickle.dump(
#     nb_model,
#     open("nb_model.pkl", "wb")
# )

# pickle.dump(
#     rf_model,
#     open("rf_model.pkl", "wb")
# )

# pickle.dump(
#     vectorizer,
#     open("vectorizer.pkl", "wb")
# )

# print("\nAll models trained and saved successfully!")


import json
import pickle
import re
import string
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB


# All files are read from and saved beside this script.
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "fake_reviews.csv"
JSON_PATH = BASE_DIR / "fake_reviews.json"


def clean_text(text):
    """Must match clean_ml_text() in app.py."""
    text = str(text).lower()
    text = re.sub(r"\d+", "", text)
    return text.translate(str.maketrans("", "", string.punctuation))


def load_datasets():
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")
    if not JSON_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: {JSON_PATH}")

    csv_data = pd.read_csv(CSV_PATH)
    with JSON_PATH.open("r", encoding="utf-8") as file:
        json_data = pd.DataFrame(json.load(file))

    required_columns = {"review", "label"}
    for filename, dataframe in (
        ("fake_reviews.csv", csv_data),
        ("fake_reviews.json", json_data),
    ):
        if not required_columns.issubset(dataframe.columns):
            raise ValueError(
                f"{filename} must contain 'review' and 'label' columns."
            )

    data = pd.concat([csv_data, json_data], ignore_index=True)
    data = data.dropna(subset=["review", "label"]).copy()
    data = data.drop_duplicates(subset=["review", "label"])
    data["review"] = data["review"].apply(clean_text)

    # Both training scripts and app.py use 0 = Genuine, 1 = Fake.
    data["label"] = pd.to_numeric(data["label"], errors="raise").astype("int32")
    labels_found = set(data["label"].unique().tolist())
    if labels_found != {0, 1}:
        raise ValueError(
            "Labels must be numeric 0 and 1 (0 = Genuine, 1 = Fake). "
            f"Found: {labels_found}"
        )

    if data["label"].value_counts().min() < 2:
        raise ValueError("Each label needs at least two examples for stratified splitting.")

    return data


def save_pickle(value, filename):
    path = BASE_DIR / filename
    with path.open("wb") as file:
        pickle.dump(value, file)
    print(f"Saved: {path}")


def main():
    print("Loading CSV and JSON datasets...")
    data = load_datasets()

    print(f"CSV rows: {len(pd.read_csv(CSV_PATH))}")
    with JSON_PATH.open("r", encoding="utf-8") as file:
        json_rows = len(json.load(file))
    print(f"JSON rows: {json_rows}")
    print(f"Combined cleaned rows: {len(data)}")
    print("\nLabel distribution:")
    print(data["label"].value_counts().sort_index())

    X = data["review"]
    y = data["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Naive Bayes": MultinomialNB(),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
        ),
    }

    filenames = {
        "Logistic Regression": "lr_model.pkl",
        "Naive Bayes": "nb_model.pkl",
        "Random Forest": "rf_model.pkl",
    }

    print(f"\nTraining reviews: {len(X_train)}")
    print(f"Testing reviews: {len(X_test)}")

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train_vec, y_train)
        predictions = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, predictions)
        print(f"{name} accuracy: {accuracy * 100:.2f}%")
        print(classification_report(
            y_test,
            predictions,
            target_names=["Genuine (0)", "Fake (1)"],
            zero_division=0,
        ))
        save_pickle(model, filenames[name])

    save_pickle(vectorizer, "vectorizer.pkl")
    print("\nAll machine-learning models and vectorizer trained and saved.")


if __name__ == "__main__":
    main()
