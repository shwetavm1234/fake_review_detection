# # import pickle
# # import re
# # from pathlib import Path

# # import numpy as np
# # import pandas as pd
# # import tensorflow as tf
# # from sklearn.metrics import (
# #     accuracy_score,
# #     classification_report,
# #     f1_score,
# #     precision_score,
# #     recall_score,
# # )
# # from sklearn.model_selection import train_test_split


# # # All files are read from and saved beside this script.
# # BASE_DIR = Path(__file__).resolve().parent
# # CSV_PATH = BASE_DIR / "fake_reviews.csv"
# # MODEL_PATH = BASE_DIR / "lstm_model.keras"
# # TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

# # # Model settings
# # MAX_WORDS = 20000
# # MAX_LENGTH = 150
# # EMBEDDING_DIM = 64
# # BATCH_SIZE = 32
# # EPOCHS = 5

# # np.random.seed(42)
# # tf.random.set_seed(42)


# # def clean_text(text):
# #     """Must match clean_lstm_text() in app.py."""
# #     text = str(text).lower()
# #     text = re.sub(r"http\S+|www\S+", " ", text)
# #     text = re.sub(r"[^a-z\s]", " ", text)
# #     return re.sub(r"\s+", " ", text).strip()


# # def main():
# #     if not CSV_PATH.is_file():
# #         raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

# #     print("Loading dataset...")
# #     data = pd.read_csv(CSV_PATH)

# #     if not {"review", "label"}.issubset(data.columns):
# #         raise ValueError("fake_reviews.csv must contain 'review' and 'label' columns.")

# #     data = data.dropna(subset=["review", "label"]).copy()
# #     data = data.drop_duplicates(subset=["review", "label"])
# #     data["review"] = data["review"].apply(clean_text)
# #     data = data[data["review"].str.len() > 0].copy()

# #     labels = pd.to_numeric(data["label"], errors="raise").to_numpy()
# #     unique_labels = set(np.unique(labels).tolist())
# #     if unique_labels != {0, 1}:
# #         raise ValueError(
# #             "Labels must be numeric 0 and 1 (0 = Genuine, 1 = Fake). "
# #             f"Found: {unique_labels}"
# #         )

# #     if pd.Series(labels).value_counts().min() < 3:
# #         raise ValueError("Each label needs at least three examples for training and validation.")

# #     reviews = data["review"].to_numpy()
# #     labels = labels.astype("int32")

# #     X_train, X_test, y_train, y_test = train_test_split(
# #         reviews,
# #         labels,
# #         test_size=0.2,
# #         random_state=42,
# #         stratify=labels,
# #     )

# #     tokenizer = tf.keras.preprocessing.text.Tokenizer(
# #         num_words=MAX_WORDS,
# #         oov_token="<OOV>",
# #     )
# #     tokenizer.fit_on_texts(X_train)

# #     X_train_seq = tokenizer.texts_to_sequences(X_train)
# #     X_test_seq = tokenizer.texts_to_sequences(X_test)

# #     X_train_pad = tf.keras.utils.pad_sequences(
# #         X_train_seq,
# #         maxlen=MAX_LENGTH,
# #         padding="post",
# #         truncating="post",
# #     )
# #     X_test_pad = tf.keras.utils.pad_sequences(
# #         X_test_seq,
# #         maxlen=MAX_LENGTH,
# #         padding="post",
# #         truncating="post",
# #     )

# #     print("Training reviews:", len(X_train))
# #     print("Testing reviews:", len(X_test))

# #     model = tf.keras.Sequential([
# #         tf.keras.layers.Input(shape=(MAX_LENGTH,)),
# #         tf.keras.layers.Embedding(
# #             input_dim=MAX_WORDS,
# #             output_dim=EMBEDDING_DIM,
# #             mask_zero=True,
# #         ),
# #         tf.keras.layers.LSTM(32),
# #         tf.keras.layers.Dropout(0.3),
# #         tf.keras.layers.Dense(16, activation="relu"),
# #         tf.keras.layers.Dropout(0.2),
# #         tf.keras.layers.Dense(1, activation="sigmoid"),
# #     ])

# #     model.compile(
# #         optimizer="adam",
# #         loss="binary_crossentropy",
# #         metrics=["accuracy"],
# #     )
# #     model.summary()

# #     early_stopping = tf.keras.callbacks.EarlyStopping(
# #         monitor="val_loss",
# #         patience=2,
# #         restore_best_weights=True,
# #     )

# #     model.fit(
# #         X_train_pad,
# #         y_train,
# #         validation_split=0.1,
# #         epochs=EPOCHS,
# #         batch_size=BATCH_SIZE,
# #         callbacks=[early_stopping],
# #         verbose=1,
# #     )

# #     probabilities = model.predict(X_test_pad, verbose=0).ravel()
# #     predictions = (probabilities >= 0.5).astype("int32")

# #     print("\nLSTM Test Results")
# #     print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
# #     print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
# #     print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
# #     print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")
# #     print("\nClassification report:")
# #     print(classification_report(
# #         y_test,
# #         predictions,
# #         target_names=["Genuine (0)", "Fake (1)"],
# #         zero_division=0,
# #     ))

# #     model.save(MODEL_PATH)
# #     with TOKENIZER_PATH.open("wb") as file:
# #         pickle.dump(tokenizer, file)

# #     print("\nSaved model:", MODEL_PATH)
# #     print("Saved tokenizer:", TOKENIZER_PATH)
# #     print("LSTM training completed.")


# # if __name__ == "__main__":
# #     main()




# import pickle
# import re
# from pathlib import Path

# import numpy as np
# import pandas as pd
# import tensorflow as tf

# from sklearn.metrics import (
#     accuracy_score,
#     classification_report,
#     f1_score,
#     precision_score,
#     recall_score,
# )
# from sklearn.model_selection import train_test_split


# # All files are read from and saved beside this script.
# BASE_DIR = Path(__file__).resolve().parent
# CSV_PATH = BASE_DIR / "fake_reviews.csv"
# MODEL_PATH = BASE_DIR / "lstm_model.keras"
# TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

# # Model settings
# MAX_WORDS = 20000
# MAX_LENGTH = 150
# EMBEDDING_DIM = 64
# BATCH_SIZE = 32
# EPOCHS = 10

# np.random.seed(42)
# tf.random.set_seed(42)


# def clean_text(text):
#     """Keep this identical to clean_lstm_text() in app.py."""
#     text = str(text).lower()
#     text = re.sub(r"http\S+|www\S+", " ", text)
#     text = re.sub(r"[^a-z\s]", " ", text)
#     return re.sub(r"\s+", " ", text).strip()


# def main():
#     if not CSV_PATH.is_file():
#         raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

#     print("Loading dataset...")
#     data = pd.read_csv(CSV_PATH)

#     required_columns = {"review", "label"}
#     if not required_columns.issubset(data.columns):
#         raise ValueError(
#             "fake_reviews.csv must contain exactly/at least "
#             "'review' and 'label' columns."
#         )

#     data = data.dropna(subset=["review", "label"]).copy()
#     data["review"] = data["review"].apply(clean_text)
#     data["label"] = pd.to_numeric(data["label"], errors="raise").astype("int32")
#     data = data[data["review"].str.strip().ne("")].copy()

#     # Remove reviews that have contradictory labels.
#     label_counts = data.groupby("review")["label"].nunique()
#     conflicting_reviews = label_counts[label_counts > 1].index
#     if len(conflicting_reviews):
#         print(f"Removing {len(conflicting_reviews)} reviews with conflicting labels.")
#         data = data[~data["review"].isin(conflicting_reviews)].copy()

#     # Each review should appear only once.
#     data = data.drop_duplicates(subset=["review"]).reset_index(drop=True)

#     labels_found = set(data["label"].unique().tolist())
#     if labels_found != {0, 1}:
#         raise ValueError(
#             "Labels must be numeric 0 and 1 (0 = Genuine, 1 = Fake). "
#             f"Found: {labels_found}"
#         )

#     if data["label"].value_counts().min() < 3:
#         raise ValueError(
#             "Each class needs at least three unique reviews for "
#             "stratified training and testing."
#         )

#     reviews = data["review"].to_numpy()
#     labels = data["label"].to_numpy(dtype="int32")

#     print("Total cleaned reviews:", len(data))
#     print("Label distribution (0=Genuine, 1=Fake):")
#     print(data["label"].value_counts().sort_index())

#     X_train, X_test, y_train, y_test = train_test_split(
#         reviews,
#         labels,
#         test_size=0.2,
#         random_state=42,
#         stratify=labels,
#     )

#     tokenizer = tf.keras.preprocessing.text.Tokenizer(
#         num_words=MAX_WORDS,
#         oov_token="<OOV>",
#     )
#     tokenizer.fit_on_texts(X_train)

#     X_train_seq = tokenizer.texts_to_sequences(X_train)
#     X_test_seq = tokenizer.texts_to_sequences(X_test)

#     X_train_pad = tf.keras.utils.pad_sequences(
#         X_train_seq,
#         maxlen=MAX_LENGTH,
#         padding="post",
#         truncating="post",
#     )
#     X_test_pad = tf.keras.utils.pad_sequences(
#         X_test_seq,
#         maxlen=MAX_LENGTH,
#         padding="post",
#         truncating="post",
#     )

#     # Use the actual tokenizer vocabulary size, capped at MAX_WORDS.
#     vocabulary_size = min(len(tokenizer.word_index) + 1, MAX_WORDS)

#     print("Training reviews:", len(X_train))
#     print("Testing reviews:", len(X_test))
#     print("Vocabulary size:", vocabulary_size)

#     model = tf.keras.Sequential([
#         tf.keras.layers.Input(shape=(MAX_LENGTH,)),
#         tf.keras.layers.Embedding(
#             input_dim=vocabulary_size,
#             output_dim=EMBEDDING_DIM,
#             mask_zero=True,
#         ),
#         tf.keras.layers.LSTM(32),
#         tf.keras.layers.Dropout(0.3),
#         tf.keras.layers.Dense(16, activation="relu"),
#         tf.keras.layers.Dropout(0.2),
#         tf.keras.layers.Dense(1, activation="sigmoid"),
#     ])

#     model.compile(
#         optimizer="adam",
#         loss="binary_crossentropy",
#         metrics=["accuracy"],
#     )

#     model.summary()

#     early_stopping = tf.keras.callbacks.EarlyStopping(
#         monitor="val_loss",
#         patience=2,
#         restore_best_weights=True,
#     )

#     model.fit(
#         X_train_pad,
#         y_train,
#         validation_split=0.1,
#         epochs=EPOCHS,
#         batch_size=BATCH_SIZE,
#         callbacks=[early_stopping],
#         verbose=1,
#     )

#     # Evaluate only on the held-out test set.
#     fake_probabilities = model.predict(X_test_pad, verbose=0).ravel()
#     predictions = (fake_probabilities >= 0.5).astype("int32")

#     print("\nLSTM Test Results")
#     print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
#     print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
#     print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
#     print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")
#     print("\nClassification report:")
#     print(classification_report(
#         y_test,
#         predictions,
#         labels=[0, 1],
#         target_names=["Genuine (0)", "Fake (1)"],
#         zero_division=0,
#     ))

#     model.save(MODEL_PATH)
#     with TOKENIZER_PATH.open("wb") as file:
#         pickle.dump(tokenizer, file)

#     print("\nSaved model:", MODEL_PATH)
#     print("Saved tokenizer:", TOKENIZER_PATH)
#     print("LSTM training completed.")
#     print(
#         "\nNote: This script trains the LSTM model only. "
#         "Option B (combining ML + LSTM probabilities) must be implemented "
#         "in app.py at prediction time."
#     )


# if __name__ == "__main__":
#     main()





import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


# Read datasets and save trained files beside this script.
BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "fake_reviews.csv"
JSON_PATH = BASE_DIR / "fake_reviews.json"

MODEL_PATH = BASE_DIR / "lstm_model.keras"
TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

# Model settings
MAX_WORDS = 20000
MAX_LENGTH = 150
EMBEDDING_DIM = 64
BATCH_SIZE = 32
EPOCHS = 10

np.random.seed(42)
tf.random.set_seed(42)


def clean_text(text):
    """Keep this identical to clean_lstm_text() in app.py."""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_datasets():
    """Load whichever of the CSV and JSON datasets are present."""
    datasets = []

    if CSV_PATH.is_file():
        print(f"\nLoading CSV: {CSV_PATH}")
        csv_data = pd.read_csv(CSV_PATH)

        if not {"review", "label"}.issubset(csv_data.columns):
            raise ValueError(
                "fake_reviews.csv must contain 'review' and 'label' columns."
            )

        datasets.append(csv_data[["review", "label"]])
        print("CSV rows:", len(csv_data))

    if JSON_PATH.is_file():
        print(f"\nLoading JSON: {JSON_PATH}")

        try:
            json_data = pd.read_json(JSON_PATH)
        except ValueError:
            # Also support JSON Lines files (one JSON object per line).
            json_data = pd.read_json(JSON_PATH, lines=True)

        if not {"review", "label"}.issubset(json_data.columns):
            raise ValueError(
                "fake_reviews.json must contain 'review' and 'label' fields."
            )

        datasets.append(json_data[["review", "label"]])
        print("JSON rows:", len(json_data))

    if not datasets:
        raise FileNotFoundError(
            "No dataset found. Add fake_reviews.csv and/or fake_reviews.json "
            "beside train_dl_model.py."
        )

    # If both files are present, combine them. Duplicate rows are removed below.
    return pd.concat(datasets, ignore_index=True)


def prepare_data(data):
    data = data.dropna(subset=["review", "label"]).copy()

    data["review"] = data["review"].apply(clean_text)
    data["label"] = pd.to_numeric(
        data["label"], errors="raise"
    ).astype("int32")

    data = data[data["review"].str.len() > 0].copy()

    labels_found = set(data["label"].unique().tolist())
    if not labels_found.issubset({0, 1}):
        raise ValueError(
            "Labels must be numeric 0 and 1 (0 = Genuine, 1 = Fake). "
            f"Found: {labels_found}"
        )

    # Remove any normalized review that appears with both labels.
    label_counts = data.groupby("review")["label"].nunique()
    conflicting_reviews = label_counts[label_counts > 1].index

    if len(conflicting_reviews):
        print(
            "Removing reviews with conflicting labels:",
            len(conflicting_reviews)
        )
        data = data[~data["review"].isin(conflicting_reviews)].copy()

    # CSV and JSON may contain the same exported dataset.
    data = data.drop_duplicates(subset=["review"]).reset_index(drop=True)

    labels_found = set(data["label"].unique().tolist())
    if labels_found != {0, 1}:
        raise ValueError(
            "Training data must contain both labels: "
            "0 = Genuine and 1 = Fake. "
            f"Found: {labels_found}"
        )

    if data["label"].value_counts().min() < 3:
        raise ValueError(
            "Each class needs at least three unique reviews for "
            "stratified training and testing."
        )

    return data


def main():
    print("FAKE REVIEW DETECTION - LSTM TRAINING")

    # Load CSV, JSON, or both.
    data = load_datasets()
    data = prepare_data(data)

    reviews = data["review"].to_numpy()
    labels = data["label"].to_numpy(dtype="int32")

    print("\nTotal cleaned unique reviews:", len(data))
    print("Label distribution (0=Genuine, 1=Fake):")
    print(data["label"].value_counts().sort_index())

    X_train, X_test, y_train, y_test = train_test_split(
        reviews,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    tokenizer = tf.keras.preprocessing.text.Tokenizer(
        num_words=MAX_WORDS,
        oov_token="<OOV>",
    )
    tokenizer.fit_on_texts(X_train)

    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_test_seq = tokenizer.texts_to_sequences(X_test)

    X_train_pad = tf.keras.utils.pad_sequences(
        X_train_seq,
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post",
    )
    X_test_pad = tf.keras.utils.pad_sequences(
        X_test_seq,
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post",
    )

    # Ensure the embedding input dimension matches the fitted vocabulary.
    vocabulary_size = min(len(tokenizer.word_index) + 1, MAX_WORDS)
    vocabulary_size = max(vocabulary_size, 2)

    print("\nTraining reviews:", len(X_train))
    print("Testing reviews:", len(X_test))
    print("Vocabulary size:", vocabulary_size)

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(MAX_LENGTH,)),
        tf.keras.layers.Embedding(
            input_dim=vocabulary_size,
            output_dim=EMBEDDING_DIM,
            mask_zero=True,
        ),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=2,
        restore_best_weights=True,
    )

    model.fit(
        X_train_pad,
        y_train,
        validation_split=0.1,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[early_stopping],
        verbose=1,
    )

    # Evaluate on the held-out test set.
    fake_probabilities = model.predict(
        X_test_pad, verbose=0
    ).ravel()
    predictions = (fake_probabilities >= 0.5).astype("int32")

    print("\nLSTM Test Results")
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
    print(
        f"Precision: "
        f"{precision_score(y_test, predictions, zero_division=0):.4f}"
    )
    print(
        f"Recall:    "
        f"{recall_score(y_test, predictions, zero_division=0):.4f}"
    )
    print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Genuine (0)", "Fake (1)"],
        zero_division=0,
    ))

    model.save(MODEL_PATH)

    with TOKENIZER_PATH.open("wb") as file:
        pickle.dump(tokenizer, file)

    print("\nSaved model:", MODEL_PATH)
    print("Saved tokenizer:", TOKENIZER_PATH)
    print("LSTM training completed.")
    print(
        "\nNote: This script trains the LSTM model only. "
        "Combining ML + LSTM probabilities (Option B) is done in app.py."
    )


if __name__ == "__main__":
    main()
