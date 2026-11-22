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
    # data["label"] = pd.to_numeric(
    #     data["label"], errors="raise"
    # ).astype("int32")


    data["label"] = pd.to_numeric(
        data["label"], errors="raise"
    )

    if not data["label"].isin([0, 1]).all():
        raise ValueError("Labels must be exactly 0 or 1.")
    data["label"] = data["label"].astype("int32")
    
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


# # # Save trained files beside this script.
# # BASE_DIR = Path(__file__).resolve().parent

# # CSV_PATH = BASE_DIR / "fake_reviews.csv"
# # JSON_PATH = BASE_DIR / "fake_reviews.json"

# # MODEL_PATH = BASE_DIR / "lstm_model.keras"
# # TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

# # # Keep MAX_LENGTH identical to app.py.
# # MAX_WORDS = 20000
# # MAX_LENGTH = 150

# # # Training settings.
# # EMBEDDING_DIM = 100
# # LSTM_UNITS = 64
# # BATCH_SIZE = 64
# # EPOCHS = 15
# # LEARNING_RATE = 0.0005
# # RANDOM_STATE = 42

# # np.random.seed(RANDOM_STATE)
# # tf.random.set_seed(RANDOM_STATE)


# # def clean_text(text):
# #     """Must match clean_lstm_text() in app.py exactly."""
# #     text = str(text).lower()
# #     text = re.sub(r"http\S+|www\S+", " ", text)
# #     text = re.sub(r"[^a-z\s]", " ", text)
# #     return re.sub(r"\s+", " ", text).strip()


# # def load_datasets():
# #     """Load CSV, JSON, or both."""
# #     datasets = []

# #     if CSV_PATH.is_file():
# #         print(f"\nLoading CSV: {CSV_PATH}")
# #         csv_data = pd.read_csv(CSV_PATH)

# #         if not {"review", "label"}.issubset(csv_data.columns):
# #             raise ValueError(
# #                 "fake_reviews.csv must contain 'review' and 'label' columns."
# #             )

# #         datasets.append(csv_data[["review", "label"]])
# #         print("CSV rows:", len(csv_data))

# #     if JSON_PATH.is_file():
# #         print(f"\nLoading JSON: {JSON_PATH}")

# #         try:
# #             json_data = pd.read_json(JSON_PATH)
# #         except ValueError:
# #             json_data = pd.read_json(JSON_PATH, lines=True)

# #         if not {"review", "label"}.issubset(json_data.columns):
# #             raise ValueError(
# #                 "fake_reviews.json must contain 'review' and 'label' fields."
# #             )

# #         datasets.append(json_data[["review", "label"]])
# #         print("JSON rows:", len(json_data))

# #     if not datasets:
# #         raise FileNotFoundError(
# #             "No dataset found. Add fake_reviews.csv and/or fake_reviews.json "
# #             "beside train_dl_model.py."
# #         )

# #     return pd.concat(datasets, ignore_index=True)


# # def prepare_data(data):
# #     data = data.dropna(subset=["review", "label"]).copy()

# #     data["review"] = data["review"].apply(clean_text)
# #     data["label"] = pd.to_numeric(data["label"], errors="raise")

# #     if not data["label"].isin([0, 1]).all():
# #         raise ValueError("Labels must be exactly 0 or 1.")

# #     data["label"] = data["label"].astype("int32")
# #     data = data[data["review"].str.len() > 0].copy()

# #     # Remove normalized reviews that have conflicting labels.
# #     label_counts = data.groupby("review")["label"].nunique()
# #     conflicting_reviews = label_counts[label_counts > 1].index

# #     if len(conflicting_reviews):
# #         print(
# #             "Removing reviews with conflicting labels:",
# #             len(conflicting_reviews),
# #         )
# #         data = data[~data["review"].isin(conflicting_reviews)].copy()

# #     # CSV and JSON may be two copies of the same dataset.
# #     data = data.drop_duplicates(subset=["review"]).reset_index(drop=True)

# #     if set(data["label"].unique()) != {0, 1}:
# #         raise ValueError(
# #             "Training data must contain both labels: "
# #             "0 = Genuine and 1 = Fake."
# #         )

# #     if data["label"].value_counts().min() < 5:
# #         raise ValueError(
# #             "Each class needs at least five unique reviews for "
# #             "stratified train, validation, and test splits."
# #         )

# #     return data


# # def make_padded_sequences(tokenizer, reviews):
# #     sequences = tokenizer.texts_to_sequences(reviews)

# #     return tf.keras.utils.pad_sequences(
# #         sequences,
# #         maxlen=MAX_LENGTH,
# #         padding="post",
# #         truncating="post",
# #     )


# # def build_model(vocabulary_size):
# #     """
# #     Bidirectional LSTM: still an LSTM-based model.
# #     The output remains one sigmoid probability for the Fake class.
# #     """
# #     inputs = tf.keras.layers.Input(shape=(MAX_LENGTH,))

# #     x = tf.keras.layers.Embedding(
# #         input_dim=vocabulary_size,
# #         output_dim=EMBEDDING_DIM,
# #         mask_zero=True,
# #     )(inputs)

# #     x = tf.keras.layers.Bidirectional(
# #         tf.keras.layers.LSTM(
# #             LSTM_UNITS,
# #             dropout=0.25,
# #             recurrent_dropout=0.0,
# #         )
# #     )(x)

# #     x = tf.keras.layers.Dropout(0.4)(x)

# #     x = tf.keras.layers.Dense(
# #         32,
# #         activation="relu",
# #         kernel_regularizer=tf.keras.regularizers.l2(0.001),
# #     )(x)

# #     x = tf.keras.layers.Dropout(0.3)(x)

# #     outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

# #     model = tf.keras.Model(inputs=inputs, outputs=outputs)

# #     optimizer = tf.keras.optimizers.Adam(
# #         learning_rate=LEARNING_RATE,
# #     )

# #     model.compile(
# #         optimizer=optimizer,
# #         loss="binary_crossentropy",
# #         metrics=[
# #             "accuracy",
# #             tf.keras.metrics.Precision(name="precision"),
# #             tf.keras.metrics.Recall(name="recall"),
# #         ],
# #     )

# #     return model


# # def main():
# #     print("FAKE REVIEW DETECTION - IMPROVED LSTM TRAINING")
# #     print("Labels: 0 = Genuine, 1 = Fake")

# #     data = prepare_data(load_datasets())

# #     reviews = data["review"].to_numpy()
# #     labels = data["label"].to_numpy(dtype="int32")

# #     print("\nTotal cleaned unique reviews:", len(data))
# #     print("Label distribution:")
# #     print(data["label"].value_counts().sort_index())

# #     # First reserve the final test set.
# #     X_train_full, X_test, y_train_full, y_test = train_test_split(
# #         reviews,
# #         labels,
# #         test_size=0.2,
# #         random_state=RANDOM_STATE,
# #         stratify=labels,
# #     )

# #     # Create a separate stratified validation set from training data.
# #     X_train, X_val, y_train, y_val = train_test_split(
# #         X_train_full,
# #         y_train_full,
# #         test_size=0.125,
# #         random_state=RANDOM_STATE,
# #         stratify=y_train_full,
# #     )

# #     tokenizer = tf.keras.preprocessing.text.Tokenizer(
# #         num_words=MAX_WORDS,
# #         oov_token="<OOV>",
# #     )

# #     # Fit tokenizer only on training reviews.
# #     tokenizer.fit_on_texts(X_train)

# #     X_train_pad = make_padded_sequences(tokenizer, X_train)
# #     X_val_pad = make_padded_sequences(tokenizer, X_val)
# #     X_test_pad = make_padded_sequences(tokenizer, X_test)

# #     vocabulary_size = min(len(tokenizer.word_index) + 1, MAX_WORDS)
# #     vocabulary_size = max(vocabulary_size, 2)

# #     print("\nTraining reviews:", len(X_train))
# #     print("Validation reviews:", len(X_val))
# #     print("Testing reviews:", len(X_test))
# #     print("Vocabulary size:", vocabulary_size)
# #     print("Maximum sequence length:", MAX_LENGTH)

# #     model = build_model(vocabulary_size)
# #     model.summary()

# #     callbacks = [
# #         tf.keras.callbacks.EarlyStopping(
# #             monitor="val_loss",
# #             patience=4,
# #             restore_best_weights=True,
# #             verbose=1,
# #         ),
# #         tf.keras.callbacks.ReduceLROnPlateau(
# #             monitor="val_loss",
# #             factor=0.5,
# #             patience=2,
# #             min_lr=0.00001,
# #             verbose=1,
# #         ),
# #     ]

# #     history = model.fit(
# #         X_train_pad,
# #         y_train,
# #         validation_data=(X_val_pad, y_val),
# #         epochs=EPOCHS,
# #         batch_size=BATCH_SIZE,
# #         callbacks=callbacks,
# #         verbose=1,
# #         shuffle=True,
# #     )

# #     # Evaluate only once on the untouched test set.
# #     test_results = model.evaluate(X_test_pad, y_test, verbose=0)
# #     print("\nTest loss:", round(float(test_results[0]), 4))
# #     print("Test accuracy:", round(float(test_results[1]), 4))

# #     fake_probabilities = model.predict(
# #         X_test_pad,
# #         verbose=0,
# #     ).ravel()

# #     predictions = (fake_probabilities >= 0.5).astype("int32")

# #     print("\nLSTM Test Results")
# #     print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
# #     print(
# #         f"Precision: "
# #         f"{precision_score(y_test, predictions, zero_division=0):.4f}"
# #     )
# #     print(
# #         f"Recall:    "
# #         f"{recall_score(y_test, predictions, zero_division=0):.4f}"
# #     )
# #     print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")

# #     print("\nClassification report:")
# #     print(
# #         classification_report(
# #             y_test,
# #             predictions,
# #             labels=[0, 1],
# #             target_names=["Genuine (0)", "Fake (1)"],
# #             zero_division=0,
# #         )
# #     )

# #     model.save(MODEL_PATH)

# #     with TOKENIZER_PATH.open("wb") as file:
# #         pickle.dump(tokenizer, file)

# #     print("\nSaved model:", MODEL_PATH)
# #     print("Saved tokenizer:", TOKENIZER_PATH)
# #     print("LSTM training completed.")
# #     print(
# #         "\nThe model output is still a sigmoid probability for the Fake class. "
# #         "The existing app.py can continue using predict() and its 0.5 threshold."
# #     )


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
#     confusion_matrix,
#     precision_score,
#     recall_score,
#     f1_score,
# )
# from sklearn.model_selection import train_test_split


# # ---------------------------------------------------------
# # PATHS
# # ---------------------------------------------------------
# BASE_DIR = Path(__file__).resolve().parent

# CSV_PATH = BASE_DIR / "fake_reviews.csv"
# JSON_PATH = BASE_DIR / "fake_reviews.json"

# MODEL_PATH = BASE_DIR / "lstm_model.keras"
# TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"


# # ---------------------------------------------------------
# # EXPERIMENT SETTINGS
# # Keep MAX_LENGTH and text cleaning compatible with app.py.
# # ---------------------------------------------------------
# MAX_WORDS = 20000
# MAX_LENGTH = 150

# EMBEDDING_DIM = 64
# LSTM_UNITS = 32
# BATCH_SIZE = 32
# EPOCHS = 18
# LEARNING_RATE = 0.0003

# RANDOM_STATE = 42

# np.random.seed(RANDOM_STATE)
# tf.keras.utils.set_random_seed(RANDOM_STATE)


# def clean_text(text):
#     """Must match clean_lstm_text() in app.py exactly."""
#     text = str(text).lower()
#     text = re.sub(r"http\S+|www\S+", " ", text)
#     text = re.sub(r"[^a-z\s]", " ", text)
#     return re.sub(r"\s+", " ", text).strip()


# def load_datasets():
#     datasets = []

#     if CSV_PATH.is_file():
#         print(f"\nLoading CSV: {CSV_PATH}")
#         csv_data = pd.read_csv(CSV_PATH)

#         if not {"review", "label"}.issubset(csv_data.columns):
#             raise ValueError(
#                 "fake_reviews.csv must contain 'review' and 'label' columns."
#             )

#         datasets.append(csv_data[["review", "label"]])
#         print("CSV rows:", len(csv_data))

#     if JSON_PATH.is_file():
#         print(f"\nLoading JSON: {JSON_PATH}")

#         try:
#             json_data = pd.read_json(JSON_PATH)
#         except ValueError:
#             json_data = pd.read_json(JSON_PATH, lines=True)

#         if not {"review", "label"}.issubset(json_data.columns):
#             raise ValueError(
#                 "fake_reviews.json must contain 'review' and 'label' fields."
#             )

#         datasets.append(json_data[["review", "label"]])
#         print("JSON rows:", len(json_data))

#     if not datasets:
#         raise FileNotFoundError(
#             "No dataset found. Add fake_reviews.csv and/or fake_reviews.json "
#             "beside train_dl_model.py."
#         )

#     return pd.concat(datasets, ignore_index=True)


# def prepare_data(data):
#     data = data.dropna(subset=["review", "label"]).copy()

#     data["review"] = data["review"].apply(clean_text)
#     data["label"] = pd.to_numeric(data["label"], errors="raise")

#     if not data["label"].isin([0, 1]).all():
#         raise ValueError("Labels must be exactly 0 or 1.")

#     data["label"] = data["label"].astype("int32")
#     data = data[data["review"].str.len() > 0].copy()

#     # Remove normalized reviews that have conflicting labels.
#     label_counts = data.groupby("review")["label"].nunique()
#     conflicting_reviews = label_counts[label_counts > 1].index

#     if len(conflicting_reviews):
#         print(
#             "Removing reviews with conflicting labels:",
#             len(conflicting_reviews),
#         )
#         data = data[~data["review"].isin(conflicting_reviews)].copy()

#     # CSV and JSON may be duplicate exports of the same data.
#     data = data.drop_duplicates(subset=["review"]).reset_index(drop=True)

#     if set(data["label"].unique()) != {0, 1}:
#         raise ValueError("Both labels must be present: 0 = Genuine, 1 = Fake.")

#     if data["label"].value_counts().min() < 5:
#         raise ValueError(
#             "Each class needs at least five unique reviews for "
#             "stratified train, validation, and test splits."
#         )

#     return data


# def pad_reviews(tokenizer, reviews):
#     sequences = tokenizer.texts_to_sequences(reviews)

#     return tf.keras.utils.pad_sequences(
#         sequences,
#         maxlen=MAX_LENGTH,
#         padding="post",
#         truncating="post",
#     )


# def build_model(vocabulary_size):
#     """
#     Regularized, unidirectional LSTM experiment.
#     The model still outputs one sigmoid probability for Fake (label 1).
#     """
#     model = tf.keras.Sequential([
#         tf.keras.layers.Input(shape=(MAX_LENGTH,)),

#         tf.keras.layers.Embedding(
#             input_dim=vocabulary_size,
#             output_dim=EMBEDDING_DIM,
#             mask_zero=True,
#         ),

#         # Drop some embedding activations to reduce memorization.
#         tf.keras.layers.SpatialDropout1D(0.20),

#         tf.keras.layers.LSTM(
#             LSTM_UNITS,
#             dropout=0.25,
#             recurrent_dropout=0.0,
#         ),

#         tf.keras.layers.Dropout(0.40),

#         tf.keras.layers.Dense(
#             16,
#             activation="relu",
#             kernel_regularizer=tf.keras.regularizers.l2(0.001),
#         ),

#         tf.keras.layers.Dropout(0.30),

#         tf.keras.layers.Dense(1, activation="sigmoid"),
#     ])

#     optimizer = tf.keras.optimizers.Adam(
#         learning_rate=LEARNING_RATE,
#         clipnorm=1.0,
#     )

#     model.compile(
#         optimizer=optimizer,
#         loss="binary_crossentropy",
#         metrics=[
#             tf.keras.metrics.BinaryAccuracy(name="accuracy"),
#             tf.keras.metrics.Precision(name="precision"),
#             tf.keras.metrics.Recall(name="recall"),
#         ],
#     )

#     return model


# def main():
#     print("FAKE REVIEW DETECTION - LSTM EXPERIMENT 2")
#     print("Algorithm: LSTM")
#     print("Labels: 0 = Genuine, 1 = Fake")

#     data = prepare_data(load_datasets())

#     reviews = data["review"].to_numpy()
#     labels = data["label"].to_numpy(dtype="int32")

#     print("\nTotal cleaned unique reviews:", len(data))
#     print("Label distribution:")
#     print(data["label"].value_counts().sort_index())

#     # Keep the same held-out test split for comparison with the prior run.
#     X_train_full, X_test, y_train_full, y_test = train_test_split(
#         reviews,
#         labels,
#         test_size=0.2,
#         random_state=RANDOM_STATE,
#         stratify=labels,
#     )

#     # Use a separate stratified validation set.
#     X_train, X_val, y_train, y_val = train_test_split(
#         X_train_full,
#         y_train_full,
#         test_size=0.125,
#         random_state=RANDOM_STATE,
#         stratify=y_train_full,
#     )

#     tokenizer = tf.keras.preprocessing.text.Tokenizer(
#         num_words=MAX_WORDS,
#         oov_token="<OOV>",
#     )

#     # Fit tokenizer only on training reviews to avoid validation/test leakage.
#     tokenizer.fit_on_texts(X_train)

#     X_train_pad = pad_reviews(tokenizer, X_train)
#     X_val_pad = pad_reviews(tokenizer, X_val)
#     X_test_pad = pad_reviews(tokenizer, X_test)

#     vocabulary_size = min(len(tokenizer.word_index) + 1, MAX_WORDS)
#     vocabulary_size = max(vocabulary_size, 2)

#     print("\nTraining reviews:", len(X_train))
#     print("Validation reviews:", len(X_val))
#     print("Testing reviews:", len(X_test))
#     print("Vocabulary size:", vocabulary_size)
#     print("Maximum sequence length:", MAX_LENGTH)

#     model = build_model(vocabulary_size)
#     model.summary()

#     callbacks = [
#         tf.keras.callbacks.EarlyStopping(
#             monitor="val_loss",
#             mode="min",
#             patience=4,
#             min_delta=0.001,
#             restore_best_weights=True,
#             verbose=1,
#         ),
#         tf.keras.callbacks.ReduceLROnPlateau(
#             monitor="val_loss",
#             mode="min",
#             factor=0.5,
#             patience=2,
#             min_lr=0.00001,
#             verbose=1,
#         ),
#     ]

#     model.fit(
#         X_train_pad,
#         y_train,
#         validation_data=(X_val_pad, y_val),
#         epochs=EPOCHS,
#         batch_size=BATCH_SIZE,
#         callbacks=callbacks,
#         shuffle=True,
#         verbose=1,
#     )

#     # Evaluate the untouched test set using the same 0.5 threshold as app.py.
#     test_results = model.evaluate(X_test_pad, y_test, verbose=0)
#     probabilities = model.predict(X_test_pad, verbose=0).ravel()
#     predictions = (probabilities >= 0.5).astype("int32")

#     print("\nLSTM TEST RESULTS (threshold = 0.50)")
#     print(f"Test loss:  {float(test_results[0]):.4f}")
#     print(f"Accuracy:   {accuracy_score(y_test, predictions):.4f}")
#     print(
#         f"Precision:  "
#         f"{precision_score(y_test, predictions, zero_division=0):.4f}"
#     )
#     print(
#         f"Recall:     "
#         f"{recall_score(y_test, predictions, zero_division=0):.4f}"
#     )
#     print(f"F1-score:   {f1_score(y_test, predictions, zero_division=0):.4f}")

#     print("\nConfusion matrix (rows=actual, columns=predicted):")
#     print(confusion_matrix(y_test, predictions, labels=[0, 1]))

#     print("\nClassification report:")
#     print(
#         classification_report(
#             y_test,
#             predictions,
#             labels=[0, 1],
#             target_names=["Genuine (0)", "Fake (1)"],
#             zero_division=0,
#         )
#     )

#     model.save(MODEL_PATH)

#     with TOKENIZER_PATH.open("wb") as file:
#         pickle.dump(tokenizer, file)

#     print("\nSaved model:", MODEL_PATH)
#     print("Saved tokenizer:", TOKENIZER_PATH)
#     print("LSTM experiment 2 completed.")
#     print(
#         "\nThe output remains a sigmoid probability for Fake (label 1). "
#         "The existing app.py can continue using its 0.5 threshold."
#     )


# if __name__ == "__main__":
#     main()
