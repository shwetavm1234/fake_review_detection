import pickle
import re
import string
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB


BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "fake_reviews.csv"
JSON_PATH = BASE_DIR / "fake_reviews.json"


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", text).strip()


def save_pickle(value, filename):
    path = BASE_DIR / filename

    with path.open("wb") as file:
        pickle.dump(value, file)

    print(f"Saved: {path}")


def load_datasets():

    datasets = []

    # Load CSV if available
    if CSV_PATH.exists():
        print("\nLoading CSV dataset...")

        csv_data = pd.read_csv(CSV_PATH)

        if not {"review", "label"}.issubset(csv_data.columns):
            raise ValueError(
                "CSV must contain review and label columns."
            )

        datasets.append(csv_data[["review", "label"]])

        print("CSV rows:", len(csv_data))

    # Load JSON if available
    if JSON_PATH.exists():
        print("\nLoading JSON dataset...")

        try:
            json_data = pd.read_json(JSON_PATH)
        except ValueError:
            # Support JSON Lines format as well
            json_data = pd.read_json(
                JSON_PATH,
                lines=True
            )

        if not {"review", "label"}.issubset(json_data.columns):
            raise ValueError(
                "JSON must contain review and label fields."
            )

        datasets.append(json_data[["review", "label"]])

        print("JSON rows:", len(json_data))

    if not datasets:
        raise FileNotFoundError(
            "Neither fake_reviews.csv nor fake_reviews.json was found."
        )

    # Combine CSV and JSON records
    data = pd.concat(datasets, ignore_index=True)

    return data


def prepare_data(data):

    data = data.dropna(subset=["review", "label"]).copy()

    data["review"] = data["review"].apply(clean_text)

    data["label"] = pd.to_numeric(
        data["label"],
        errors="raise"
    ).astype(int)

    data = data[data["review"].str.strip() != ""]

    # Only labels 0 and 1 are allowed
    if not set(data["label"].unique()).issubset({0, 1}):
        raise ValueError(
            "Labels must be 0 (Genuine) or 1 (Fake)."
        )

    # Remove reviews that have conflicting labels
    label_counts = data.groupby("review")["label"].nunique()

    conflicting_reviews = label_counts[
        label_counts > 1
    ].index

    if len(conflicting_reviews) > 0:
        print(
            "\nRemoving reviews with conflicting labels:",
            len(conflicting_reviews)
        )

        data = data[
            ~data["review"].isin(conflicting_reviews)
        ]

    # Remove duplicate reviews from CSV and JSON
    data = data.drop_duplicates(subset=["review"])

    if set(data["label"].unique()) != {0, 1}:
        raise ValueError(
            "Training dataset must contain both labels 0 and 1."
        )

    return data


def main():

    print("FAKE REVIEW DETECTION - ML TRAINING")

    # Load both datasets
    data = load_datasets()

    # Prepare combined dataset
    data = prepare_data(data)

    print("\nTotal unique reviews:", len(data))

    print("\nLabel distribution:")
    print(
        data["label"].value_counts().sort_index()
    )

    X = data["review"]
    y = data["label"]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # TF-IDF feature extraction
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2)
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # ML models
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000
        ),

        "Naive Bayes": MultinomialNB(),

        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            random_state=42,
            n_jobs=-1
        )
    }

    filenames = {
        "Logistic Regression": "lr_model.pkl",
        "Naive Bayes": "nb_model.pkl",
        "Random Forest": "rf_model.pkl"
    }

    trained_models = []

    # Train individual models
    for name, model in models.items():

        print(f"\nTraining {name}...")

        model.fit(X_train_vec, y_train)

        predictions = model.predict(X_test_vec)

        print(
            "Accuracy:",
            round(
                accuracy_score(y_test, predictions) * 100,
                2
            ),
            "%"
        )

        print(
            classification_report(
                y_test,
                predictions,
                labels=[0, 1],
                target_names=["Genuine", "Fake"],
                zero_division=0
            )
        )

        save_pickle(model, filenames[name])

        trained_models.append(model)

    # Combined ML soft voting
    fake_probabilities = []

    for model in trained_models:

        fake_index = list(model.classes_).index(1)

        probabilities = model.predict_proba(X_test_vec)

        fake_probabilities.append(
            probabilities[:, fake_index]
        )

    average_fake_probability = np.mean(
        fake_probabilities,
        axis=0
    )

    ensemble_predictions = (
        average_fake_probability >= 0.5
    ).astype(int)

    print("\nCOMBINED ML MODEL RESULTS")

    print(
        "Ensemble accuracy:",
        round(
            accuracy_score(
                y_test,
                ensemble_predictions
            ) * 100,
            2
        ),
        "%"
    )

    print(
        classification_report(
            y_test,
            ensemble_predictions,
            labels=[0, 1],
            target_names=["Genuine", "Fake"],
            zero_division=0
        )
    )

    # Save vectorizer
    save_pickle(vectorizer, "vectorizer.pkl")

    print("\nAll ML models trained and saved successfully.")


if __name__ == "__main__":
    main()
