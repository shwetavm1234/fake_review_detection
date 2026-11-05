
# import os
# import re
# import pickle
# import numpy as np
# import pandas as pd
# import tensorflow as tf

# from sklearn.model_selection import train_test_split
# from sklearn.metrics import (
#     accuracy_score,
#     precision_score,
#     recall_score,
#     f1_score,
#     classification_report,
# )

# # Reproducibility
# np.random.seed(42)
# tf.random.set_seed(42)

# # Paths relative to this script
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CSV_PATH = os.path.join(BASE_DIR, "fake_reviews.csv")
# MODEL_PATH = os.path.join(BASE_DIR, "lstm_model.keras")
# TOKENIZER_PATH = os.path.join(BASE_DIR, "lstm_tokenizer.pkl")

# # Model settings
# MAX_WORDS = 20000
# MAX_LENGTH = 150
# EMBEDDING_DIM = 64
# BATCH_SIZE = 32
# EPOCHS = 5


# def clean_text(text):
#     text = str(text).lower()
#     text = re.sub(r"http\S+|www\S+", " ", text)
#     text = re.sub(r"[^a-z\s]", " ", text)
#     return re.sub(r"\s+", " ", text).strip()


# def main():
#     print("Loading dataset...")
#     data = pd.read_csv(CSV_PATH)

#     if not {"review", "label"}.issubset(data.columns):
#         raise ValueError("CSV must contain 'review' and 'label' columns.")

#     data = data.dropna(subset=["review", "label"]).copy()
#     data = data.drop_duplicates(subset=["review", "label"])
#     data["review"] = data["review"].apply(clean_text)

#     # Convert labels to numeric values.
#     labels = pd.to_numeric(data["label"], errors="raise").to_numpy()
#     unique_labels = set(np.unique(labels).tolist())

#     if unique_labels != {0, 1}:
#         raise ValueError(
#             f"Expected binary labels 0 and 1, found {unique_labels}"
#         )

#     reviews = data["review"].to_numpy()

#     X_train, X_test, y_train, y_test = train_test_split(
#         reviews,
#         labels.astype("int32"),
#         test_size=0.2,
#         random_state=42,
#         stratify=labels,
#     )

#     # Learn vocabulary from training reviews only.
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

#     print("Training reviews:", len(X_train))
#     print("Testing reviews:", len(X_test))

#     # LSTM neural network
#     model = tf.keras.Sequential([
#         tf.keras.layers.Input(shape=(MAX_LENGTH,)),
#         tf.keras.layers.Embedding(
#             input_dim=MAX_WORDS,
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

#     # Evaluate on held-out test data.
#     probabilities = model.predict(X_test_pad, verbose=0).ravel()
#     predictions = (probabilities >= 0.5).astype("int32")

#     print("\nLSTM Test Results")
#     print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
#     print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
#     print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
#     print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")
#     print("\nClassification report:")
#     print(classification_report(y_test, predictions, zero_division=0))

#     # Save the trained model and matching tokenizer.
#     model.save(MODEL_PATH)
#     with open(TOKENIZER_PATH, "wb") as file:
#         pickle.dump(tokenizer, file)

#     print("\nSaved model:", MODEL_PATH)
#     print("Saved tokenizer:", TOKENIZER_PATH)
#     print("LSTM training completed.")


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


# All files are read from and saved beside this script.
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "fake_reviews.csv"
MODEL_PATH = BASE_DIR / "lstm_model.keras"
TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

# Model settings
MAX_WORDS = 20000
MAX_LENGTH = 150
EMBEDDING_DIM = 64
BATCH_SIZE = 32
EPOCHS = 5

np.random.seed(42)
tf.random.set_seed(42)


def clean_text(text):
    """Must match clean_lstm_text() in app.py."""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main():
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

    print("Loading dataset...")
    data = pd.read_csv(CSV_PATH)

    if not {"review", "label"}.issubset(data.columns):
        raise ValueError("fake_reviews.csv must contain 'review' and 'label' columns.")

    data = data.dropna(subset=["review", "label"]).copy()
    data = data.drop_duplicates(subset=["review", "label"])
    data["review"] = data["review"].apply(clean_text)
    data = data[data["review"].str.len() > 0].copy()

    labels = pd.to_numeric(data["label"], errors="raise").to_numpy()
    unique_labels = set(np.unique(labels).tolist())
    if unique_labels != {0, 1}:
        raise ValueError(
            "Labels must be numeric 0 and 1 (0 = Genuine, 1 = Fake). "
            f"Found: {unique_labels}"
        )

    if pd.Series(labels).value_counts().min() < 3:
        raise ValueError("Each label needs at least three examples for training and validation.")

    reviews = data["review"].to_numpy()
    labels = labels.astype("int32")

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

    print("Training reviews:", len(X_train))
    print("Testing reviews:", len(X_test))

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(MAX_LENGTH,)),
        tf.keras.layers.Embedding(
            input_dim=MAX_WORDS,
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

    probabilities = model.predict(X_test_pad, verbose=0).ravel()
    predictions = (probabilities >= 0.5).astype("int32")

    print("\nLSTM Test Results")
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
    print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")
    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        target_names=["Genuine (0)", "Fake (1)"],
        zero_division=0,
    ))

    model.save(MODEL_PATH)
    with TOKENIZER_PATH.open("wb") as file:
        pickle.dump(tokenizer, file)

    print("\nSaved model:", MODEL_PATH)
    print("Saved tokenizer:", TOKENIZER_PATH)
    print("LSTM training completed.")


if __name__ == "__main__":
    main()
