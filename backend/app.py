# # import os
# # import pickle
# # import re
# # import string
# # import numpy as np
# # import pandas as pd
# # import tensorflow as tf
# # from flask import Flask, request, jsonify, session
# # from flask_cors import CORS
# # from tensorflow.keras.models import load_model
# # from tensorflow.keras.preprocessing.sequence import pad_sequences
# # import sqlite3
# # from pathlib import Path
# # from datetime import datetime
# # from functools import wraps
# # from werkzeug.security import generate_password_hash, check_password_hash



# # # SQLite database location: same folder as app.py
# # DATABASE_PATH = Path(__file__).resolve().parent / "reviews.db"


# # def get_db_connection():
# #     conn = sqlite3.connect(DATABASE_PATH)
# #     conn.row_factory = sqlite3.Row
# #     return conn


# # def init_db():
# #     conn = get_db_connection()

# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS users (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             name TEXT NOT NULL,
# #             email TEXT NOT NULL UNIQUE COLLATE NOCASE,
# #             password_hash TEXT NOT NULL,
# #             created_at TEXT NOT NULL
# #         )
# #     """)

# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS review_history (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             user_id INTEGER,
# #             review TEXT NOT NULL,
# #             ml_prediction TEXT,
# #             ml_confidence REAL,
# #             lstm_prediction TEXT,
# #             lstm_confidence REAL,
# #             created_at TEXT NOT NULL
# #         )
# #     """)

# #     # Add user_id to an existing review_history table created by an older version.
# #     columns = {row[1] for row in conn.execute("PRAGMA table_info(review_history)").fetchall()}
# #     if "user_id" not in columns:
# #         conn.execute("ALTER TABLE review_history ADD COLUMN user_id INTEGER")

# #     conn.commit()
# #     conn.close()


# # # Create the table if it doesn't already exist
# # init_db()



# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # # Load the trained machine-learning models
# # with open(os.path.join(BASE_DIR, "lr_model.pkl"), "rb") as f:
# #     lr_model = pickle.load(f)

# # with open(os.path.join(BASE_DIR, "nb_model.pkl"), "rb") as f:
# #     nb_model = pickle.load(f)

# # # with open(os.path.join(BASE_DIR, "rf_model.pkl"), "rb") as f:
# # #     rf_model = pickle.load(f)
# # try:
# #     with open(os.path.join(BASE_DIR, "rf_model.pkl"), "rb") as f:
# #         rf_model = pickle.load(f)
# # except Exception as e:
# #     print("Random Forest model unavailable:", e)
# #     rf_model = None

# # with open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb") as f:
# #     vectorizer = pickle.load(f)


# # # CREATE FLASK SERVER
# # app = Flask(__name__)
# # app.config.update(
# #     SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-secret"),
# #     SESSION_COOKIE_HTTPONLY=True,
# #     SESSION_COOKIE_SAMESITE="Lax",
# #     SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
# #     PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
# # )
# # CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])


# # def login_required(view):
# #     @wraps(view)
# #     def wrapped(*args, **kwargs):
# #         if not session.get("user_id"):
# #             return jsonify({"error": "Please log in to continue."}), 401
# #         return view(*args, **kwargs)
# #     return wrapped


# # @app.route("/auth/register", methods=["POST"])
# # def register():
# #     data = request.get_json(silent=True) or {}
# #     name = str(data.get("name", "")).strip()
# #     email = str(data.get("email", "")).strip().lower()
# #     password = str(data.get("password", ""))
# #     if not name or not email or not password:
# #         return jsonify({"error": "Name, email and password are required."}), 400
# #     if len(name) > 80 or len(email) > 254 or "@" not in email:
# #         return jsonify({"error": "Please enter a valid name and email address."}), 400
# #     if len(password) < 8:
# #         return jsonify({"error": "Password must contain at least 8 characters."}), 400
# #     conn = get_db_connection()
# #     try:
# #         cursor = conn.execute(
# #             "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
# #             (name, email, generate_password_hash(password), datetime.now().astimezone().isoformat(timespec="seconds")),
# #         )
# #         conn.commit()
# #         user_id = cursor.lastrowid
# #     except sqlite3.IntegrityError:
# #         return jsonify({"error": "An account with this email already exists. Please log in."}), 409
# #     finally:
# #         conn.close()
# #     session.clear()
# #     session["user_id"] = user_id
# #     session["user_name"] = name
# #     session.permanent = True
# #     return jsonify({"message": "Account created successfully.", "user": {"id": user_id, "name": name, "email": email}}), 201


# # @app.route("/auth/login", methods=["POST"])
# # def login():
# #     data = request.get_json(silent=True) or {}
# #     email = str(data.get("email", "")).strip().lower()
# #     password = str(data.get("password", ""))
# #     conn = get_db_connection()
# #     try:
# #         user = conn.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)).fetchone()
# #     finally:
# #         conn.close()
# #     if not user or not check_password_hash(user["password_hash"], password):
# #         return jsonify({"error": "Incorrect email or password."}), 401
# #     session.clear()
# #     session["user_id"] = user["id"]
# #     session["user_name"] = user["name"]
# #     session.permanent = True
# #     return jsonify({"message": "Login successful.", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}), 200


# # @app.route("/auth/me", methods=["GET"])
# # def current_user():
# #     user_id = session.get("user_id")
# #     if not user_id:
# #         return jsonify({"user": None}), 200
# #     conn = get_db_connection()
# #     try:
# #         user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
# #     finally:
# #         conn.close()
# #     if not user:
# #         session.clear()
# #         return jsonify({"user": None}), 200
# #     return jsonify({"user": dict(user)}), 200


# # @app.route("/auth/logout", methods=["POST"])
# # def logout():
# #     session.clear()
# #     return jsonify({"message": "Logged out successfully."}), 200


# # # TEXT CLEANING FUNCTION
# # # IMPORTANT: This should be the same cleaning used during model training.
# # def clean_text(text):
# #     text = str(text).lower()
# #     text = re.sub(r'\d+', '', text)
# #     text = text.translate(
# #         str.maketrans('', '', string.punctuation)
# #     )
# #     return text




# # # LOAD TRAINED LSTM MODEL
# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # MODEL_PATH = os.path.join(
# #     BASE_DIR, "lstm_model.keras"
# # )

# # TOKENIZER_PATH = os.path.join(
# #     BASE_DIR, "lstm_tokenizer.pkl"
# # )

# # lstm_model = tf.keras.models.load_model(MODEL_PATH)

# # with open(TOKENIZER_PATH, "rb") as f:
# #     lstm_tokenizer = pickle.load(f)

# # MAX_LENGTH = 150
# # #print("LSTM model loaded successfully!")

# # # GET BEST PREDICTION
# # def get_best_prediction(vec):
# #     # Logistic Regression
# #     lr_pred = lr_model.predict(vec)[0]
# #     lr_proba = max(
# #         lr_model.predict_proba(vec)[0]
# #     )

# #     # Naive Bayes
# #     nb_pred = nb_model.predict(vec)[0]
# #     nb_proba = max(
# #         nb_model.predict_proba(vec)[0]
# #     )

# #     # Random Forest
# #     rf_pred = rf_model.predict(vec)[0]
# #     rf_proba = max(
# #         rf_model.predict_proba(vec)[0]
# #     )

# #     # Choose model with highest confidence
# #     best_conf = max(
# #         lr_proba,
# #         nb_proba,
# #         rf_proba
# #     )

# #     if best_conf == lr_proba:
# #         final_pred = lr_pred
        
# #     elif best_conf == nb_proba:
# #         final_pred = nb_pred

# #     else:
# #         final_pred = rf_pred

# #     return {
# #         "prediction": (
# #             "Fake"
# #             if final_pred == 1
# #             else "Genuine"
# #         ),
# #         "confidence": round(
# #             float(best_conf),
# #             2
# #         )
# #     }


# # def get_lstm_prediction(review):
# #     cleaned_review = clean_text(review)

# #     sequence = lstm_tokenizer.texts_to_sequences(
# #         [cleaned_review]
# #     )

# #     padded = pad_sequences(
# #         sequence,
# #         maxlen=MAX_LENGTH,
# #         padding="post",
# #         truncating="post"
# #     )

# #     probability = float(
# #         np.asarray(
# #             lstm_model.predict(padded, verbose=0)
# #         ).reshape(-1)[0]
# #     )

# #     # Assumes label 1 = Fake and label 0 = Genuine
# #     prediction = 1 if probability >= 0.5 else 0

# #     confidence = (
# #         probability if prediction == 1
# #         else 1 - probability
# #     )

# #     return {
# #         "prediction": "Fake" if prediction == 1 else "Genuine",
# #         "confidence": round(confidence, 2)
# #     }



# # # SINGLE REVIEW
# # @app.route("/analyze", methods=["POST"])
# # @login_required
# # def analyze():
# #     data = request.get_json(silent=True)

# #     if not data:
# #         return jsonify({"error": "Invalid JSON data"}), 400

# #     review = data.get("review")

# #     if not review or not str(review).strip():
# #         return jsonify({"error": "No review provided"}), 400

# #     # Clean the review
# #     cleaned_review = clean_text(review)

# #     # Convert cleaned text to TF-IDF numbers
# #     vec = vectorizer.transform([cleaned_review])

# #     # Get predictions from both models
# #     ml_result = get_best_prediction(vec)
# #     dl_result  = get_lstm_prediction(review)
# #  #lstm_result = get_lstm_prediction(review)

# #        # Extract ML prediction and confidence
# #     ml_label = (
# #         ml_result.get("prediction")
# #         if isinstance(ml_result, dict)
# #         else str(ml_result)
# #     )

# #     ml_confidence = (
# #         ml_result.get("confidence")
# #         if isinstance(ml_result, dict)
# #         else None
# #     )

# #     # Extract LSTM prediction and confidence
# #     lstm_label = (
# #         dl_result.get("prediction")
# #         if isinstance(dl_result, dict)
# #         else str(dl_result)
# #     )

# #     lstm_confidence = (
# #         dl_result.get("confidence")
# #         if isinstance(dl_result, dict)
# #         else None
# #     )

# #     # Save review and predictions in SQLite
# #     conn = get_db_connection()

# #     try:
# #         conn.execute(
# #             """
# #             INSERT INTO review_history (
# #                 user_id,
# #                 review,
# #                 ml_prediction,
# #                 ml_confidence,
# #                 lstm_prediction,
# #                 lstm_confidence,
# #                 created_at
# #             )
# #             VALUES (?, ?, ?, ?, ?, ?, ?)
# #             """,
# #             (
# #                 session["user_id"],
# #                 str(review),
# #                 str(ml_label) if ml_label is not None else None,
# #                 ml_confidence,
# #                 str(lstm_label) if lstm_label is not None else None,
# #                 lstm_confidence,
# #                 datetime.now().astimezone().isoformat(
# #                     timespec="seconds"
# #                 )
# #             )
# #         )
# #         conn.commit()
# #     finally:
# #         conn.close()

# #     # Return predictions to the React frontend
# #     return jsonify({
# #         "ml_prediction": ml_result,
# #         "lstm_prediction": dl_result
# #     })



# # @app.route("/history", methods=["GET"])
# # @login_required
# # def get_review_history():
# #     conn = get_db_connection()

# #     try:
# #         rows = conn.execute(
# #             """
# #             SELECT
# #                 id,
# #                 review,
# #                 ml_prediction,
# #                 ml_confidence,
# #                 lstm_prediction,
# #                 lstm_confidence,
# #                 created_at
# #             FROM review_history
# #             WHERE user_id = ?
# #             ORDER BY id DESC
# #             """
# #         , (session["user_id"],)).fetchall()

# #         history = [dict(row) for row in rows]

# #         return jsonify(history), 200

# #     except sqlite3.Error as error:
# #         return jsonify({
# #             "error": "Unable to retrieve review history",
# #             "details": str(error)
# #         }), 500

# #     finally:
# #         conn.close()


# # @app.route("/history/<int:review_id>", methods=["DELETE"])
# # @login_required
# # def delete_review_history(review_id):
# #     conn = get_db_connection()

# #     try:
# #         cursor = conn.execute(
# #             "DELETE FROM review_history WHERE id = ? AND user_id = ?",
# #             (review_id, session["user_id"])
# #         )
# #         conn.commit()

# #         if cursor.rowcount == 0:
# #             return jsonify({"error": "Review not found"}), 404

# #         return jsonify({"message": "Review deleted successfully"}), 200

# #     except sqlite3.Error as error:
# #         conn.rollback()
# #         return jsonify({
# #             "error": "Unable to delete review",
# #             "details": str(error)
# #         }), 500

# #     finally:
# #         conn.close()



# # # CSV + JSON FILE UPLOAD
# # @app.route("/upload", methods=["POST"])
# # @login_required
# # def upload():
# #     # Get uploaded file
# #     file = request.files.get("file")
# #     if not file:
# #         return jsonify({
# #             "error": "No file uploaded"
# #         }), 400

# #     # Get file name
# #     filename = file.filename.lower()

# #     # Check file type
# #     if not filename.endswith((".csv", ".json")):
# #         return jsonify({
# #             "error": "Only CSV or JSON files are allowed"
# #         }), 400

# #     # Read CSV
# #     if filename.endswith(".csv"):
# #         try:
# #             df = pd.read_csv(file)
# #         except Exception as e:
# #             return jsonify({
# #                 "error": f"Unable to read CSV file: {str(e)}"
# #             }), 400

# #     # Read JSON
# #     elif filename.endswith(".json"):
# #         try:
# #             df = pd.read_json(file)
# #         except Exception as e:
# #             return jsonify({
# #                 "error": f"Unable to read JSON file: {str(e)}"
# #             }), 400

# #     # Check review column
# #     if "review" not in df.columns:
# #         return jsonify({
# #             "error": (
# #                 "File must contain a 'review' column"
# #             )
# #         }), 400


# #     # Predict every review
# #     results = []
# #     for review in df["review"]:
# #         # Clean review
# #         cleaned_review = clean_text(review)
        
# #         # Convert to TF-IDF
# #         vec = vectorizer.transform(
# #             [cleaned_review]
# #         )

# #         # Predict
# #         result = get_best_prediction(vec)

# #         results.append({
# #             "review": review,
# #             "prediction": result["prediction"],
# #             "confidence": result["confidence"]
# #         })

# #     # Return results
# #     return jsonify(results)

# # # RUN SERVER
# # if __name__ == "__main__":
# #     app.run(debug=True)
# import os
# import pickle
# import re
# import string
# import sqlite3
# from pathlib import Path
# from datetime import datetime
# from functools import wraps

# import numpy as np
# import pandas as pd
# import tensorflow as tf

# from flask import Flask, request, jsonify, session
# from flask_cors import CORS
# from werkzeug.security import generate_password_hash, check_password_hash
# from tensorflow.keras.preprocessing.sequence import pad_sequences


# # --------------------------------------------------
# # 1. PATHS AND DATABASE
# # --------------------------------------------------

# BASE_DIR = Path(__file__).resolve().parent
# DATABASE_PATH = BASE_DIR / "reviews.db"

# def get_db_connection():
#     conn = sqlite3.connect(DATABASE_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# def init_db():
#     conn = get_db_connection()

#     try:
#         conn.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL,
#                 email TEXT NOT NULL UNIQUE COLLATE NOCASE,
#                 password_hash TEXT NOT NULL,
#                 created_at TEXT NOT NULL
#             )
#         """)

#         conn.execute("""
#             CREATE TABLE IF NOT EXISTS review_history (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER,
#                 review TEXT NOT NULL,
#                 ml_prediction TEXT,
#                 ml_confidence REAL,
#                 lstm_prediction TEXT,
#                 lstm_confidence REAL,
#                 created_at TEXT NOT NULL
#             )
#         """)

#         columns = {
#             row[1] for row in
#             conn.execute("PRAGMA table_info(review_history)").fetchall()
#         }

#         if "user_id" not in columns:
#             conn.execute(
#                 "ALTER TABLE review_history ADD COLUMN user_id INTEGER"
#             )

#         conn.commit()

#     finally:
#         conn.close()


# init_db()


# # --------------------------------------------------
# # 2. LOAD MACHINE LEARNING MODELS
# # --------------------------------------------------

# def load_pickle(filename):
#     path = BASE_DIR / filename

#     if not path.exists():
#         raise FileNotFoundError(
#             f"Required model file not found: {path}"
#         )

#     with open(path, "rb") as file:
#         return pickle.load(file)


# lr_model = load_pickle("lr_model.pkl")
# nb_model = load_pickle("nb_model.pkl")
# vectorizer = load_pickle("vectorizer.pkl")

# # Random Forest is optional.
# try:
#     rf_model = load_pickle("rf_model.pkl")
#     print("Random Forest model loaded successfully.")
# except Exception as error:
#     print("Random Forest unavailable:", error)
#     rf_model = None


# # --------------------------------------------------
# # 3. LOAD LSTM MODEL
# # --------------------------------------------------

# MODEL_PATH = BASE_DIR / "lstm_model.keras"
# TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

# if not MODEL_PATH.exists():
#     raise FileNotFoundError(f"LSTM model not found: {MODEL_PATH}")

# if not TOKENIZER_PATH.exists():
#     raise FileNotFoundError(
#         f"LSTM tokenizer not found: {TOKENIZER_PATH}"
#     )

# lstm_model = tf.keras.models.load_model(MODEL_PATH)

# with open(TOKENIZER_PATH, "rb") as file:
#     lstm_tokenizer = pickle.load(file)

# MAX_LENGTH = 150

# print("All required models loaded successfully.")


# # --------------------------------------------------
# # 4. FLASK APPLICATION
# # --------------------------------------------------

# app = Flask(__name__)

# app.config.update(
#     SECRET_KEY=os.environ.get(
#         "SECRET_KEY",
#         "development-only-change-this-secret"
#     ),
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE="Lax",
#     SESSION_COOKIE_SECURE=False,
#     PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7
# )

# CORS(
#     app,
#     supports_credentials=True,
#     origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173"
#     ]
# )


# # --------------------------------------------------
# # 5. LOGIN REQUIRED DECORATOR
# # --------------------------------------------------

# def login_required(view):

#     @wraps(view)
#     def wrapped(*args, **kwargs):

#         if not session.get("user_id"):
#             return jsonify({
#                 "error": "Please log in to continue."
#             }), 401

#         return view(*args, **kwargs)

#     return wrapped


# # --------------------------------------------------
# # 6. TEXT CLEANING
# # --------------------------------------------------

# def clean_text(text):

#     text = str(text).lower()

#     text = re.sub(r'\d+', '', text)

#     text = text.translate(
#         str.maketrans('', '', string.punctuation)
#     )

#     return text


# # --------------------------------------------------
# # 7. USER REGISTRATION
# # --------------------------------------------------

# @app.route("/auth/register", methods=["POST"])
# def register():

#     data = request.get_json(silent=True) or {}

#     name = str(data.get("name", "")).strip()
#     email = str(data.get("email", "")).strip().lower()
#     password = str(data.get("password", ""))

#     if not name or not email or not password:
#         return jsonify({
#             "error": "Name, email and password are required."
#         }), 400

#     if len(name) > 80 or len(email) > 254 or "@" not in email:
#         return jsonify({
#             "error": "Please enter a valid name and email."
#         }), 400

#     if len(password) < 8:
#         return jsonify({
#             "error": "Password must contain at least 8 characters."
#         }), 400

#     conn = get_db_connection()

#     try:
#         cursor = conn.execute(
#             """
#             INSERT INTO users
#             (name, email, password_hash, created_at)
#             VALUES (?, ?, ?, ?)
#             """,
#             (
#                 name,
#                 email,
#                 generate_password_hash(password),
#                 datetime.now().astimezone().isoformat(
#                     timespec="seconds"
#                 )
#             )
#         )

#         conn.commit()
#         user_id = cursor.lastrowid

#     except sqlite3.IntegrityError:
#         return jsonify({
#             "error": "Email already registered. Please log in."
#         }), 409

#     finally:
#         conn.close()

#     session.clear()
#     session["user_id"] = user_id
#     session["user_name"] = name
#     session.permanent = True

#     return jsonify({
#         "message": "Registration successful.",
#         "user": {
#             "id": user_id,
#             "name": name,
#             "email": email
#         }
#     }), 201


# # --------------------------------------------------
# # 8. USER LOGIN
# # --------------------------------------------------

# @app.route("/auth/login", methods=["POST"])
# def login():

#     data = request.get_json(silent=True) or {}

#     email = str(data.get("email", "")).strip().lower()
#     password = str(data.get("password", ""))

#     conn = get_db_connection()

#     try:
#         user = conn.execute(
#             """
#             SELECT id, name, email, password_hash
#             FROM users
#             WHERE email = ?
#             """,
#             (email,)
#         ).fetchone()

#     finally:
#         conn.close()

#     if not user or not check_password_hash(
#         user["password_hash"], password
#     ):
#         return jsonify({
#             "error": "Incorrect email or password."
#         }), 401

#     session.clear()

#     session["user_id"] = user["id"]
#     session["user_name"] = user["name"]
#     session.permanent = True

#     return jsonify({
#         "message": "Login successful.",
#         "user": {
#             "id": user["id"],
#             "name": user["name"],
#             "email": user["email"]
#         }
#     }), 200


# # --------------------------------------------------
# # 9. CHECK CURRENT USER
# # --------------------------------------------------

# @app.route("/auth/me", methods=["GET"])
# def current_user():

#     user_id = session.get("user_id")

#     if not user_id:
#         return jsonify({"user": None}), 200

#     conn = get_db_connection()

#     try:
#         user = conn.execute(
#             """
#             SELECT id, name, email
#             FROM users
#             WHERE id = ?
#             """,
#             (user_id,)
#         ).fetchone()

#     finally:
#         conn.close()

#     if not user:
#         session.clear()
#         return jsonify({"user": None}), 200

#     return jsonify({
#         "user": dict(user)
#     }), 200


# # --------------------------------------------------
# # 10. LOGOUT
# # --------------------------------------------------

# @app.route("/auth/logout", methods=["POST"])
# def logout():

#     session.clear()

#     return jsonify({
#         "message": "Logged out successfully."
#     }), 200


# # --------------------------------------------------
# # 11. MACHINE LEARNING PREDICTION
# # --------------------------------------------------

# def get_best_prediction(vec):

#     models = [
#         lr_model,
#         nb_model
#     ]

#     if rf_model is not None:
#         models.append(rf_model)

#     predictions = []

#     for model in models:

#         prediction = model.predict(vec)[0]

#         probabilities = model.predict_proba(vec)[0]

#         confidence = float(np.max(probabilities))

#         predictions.append({
#             "prediction": prediction,
#             "confidence": confidence
#         })

#     best_result = max(
#         predictions,
#         key=lambda item: item["confidence"]
#     )

#     final_pred = best_result["prediction"]

#     label = (
#         "Fake"
#         if str(final_pred) in ("1", "Fake")
#         else "Genuine"
#     )

#     return {
#         "prediction": label,
#         "confidence": round(
#             best_result["confidence"], 2
#         )
#     }


# # --------------------------------------------------
# # 12. LSTM PREDICTION
# # --------------------------------------------------

# def get_lstm_prediction(review):

#     cleaned_review = clean_text(review)

#     sequence = lstm_tokenizer.texts_to_sequences(
#         [cleaned_review]
#     )

#     padded = pad_sequences(
#         sequence,
#         maxlen=MAX_LENGTH,
#         padding="post",
#         truncating="post"
#     )

#     probability = float(
#         np.asarray(
#             lstm_model.predict(
#                 padded,
#                 verbose=0
#             )
#         ).reshape(-1)[0]
#     )

#     # Assumes label 1 = Fake and label 0 = Genuine.

#     prediction = 1 if probability >= 0.5 else 0

#     confidence = (
#         probability
#         if prediction == 1
#         else 1 - probability
#     )

#     return {
#         "prediction": (
#             "Fake" if prediction == 1 else "Genuine"
#         ),
#         "confidence": round(confidence, 2)
#     }


# # --------------------------------------------------
# # 13. ANALYZE SINGLE REVIEW
# # --------------------------------------------------

# @app.route("/analyze", methods=["POST"])
# @login_required
# def analyze():

#     data = request.get_json(silent=True)

#     if not data:
#         return jsonify({
#             "error": "Invalid JSON data."
#         }), 400

#     review = data.get("review")

#     if not review or not str(review).strip():
#         return jsonify({
#             "error": "Please enter a review."
#         }), 400

#     try:

#         cleaned_review = clean_text(review)

#         vec = vectorizer.transform(
#             [cleaned_review]
#         )

#         ml_result = get_best_prediction(vec)

#         lstm_result = get_lstm_prediction(review)

#         conn = get_db_connection()

#         try:

#             conn.execute(
#                 """
#                 INSERT INTO review_history (
#                     user_id,
#                     review,
#                     ml_prediction,
#                     ml_confidence,
#                     lstm_prediction,
#                     lstm_confidence,
#                     created_at
#                 )
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#                 """,
#                 (
#                     session["user_id"],
#                     str(review),
#                     ml_result["prediction"],
#                     ml_result["confidence"],
#                     lstm_result["prediction"],
#                     lstm_result["confidence"],
#                     datetime.now().astimezone().isoformat(
#                         timespec="seconds"
#                     )
#                 )
#             )

#             conn.commit()

#         finally:
#             conn.close()

#         return jsonify({
#             "ml_prediction": ml_result,
#             "lstm_prediction": lstm_result
#         }), 200

#     except Exception as error:

#         app.logger.exception("Review analysis failed")

#         return jsonify({
#             "error": "Review analysis failed.",
#             "details": str(error)
#         }), 500


# # --------------------------------------------------
# # 14. GET REVIEW HISTORY
# # --------------------------------------------------

# @app.route("/history", methods=["GET"])
# @login_required
# def get_review_history():

#     conn = get_db_connection()

#     try:

#         rows = conn.execute(
#             """
#             SELECT
#                 id,
#                 review,
#                 ml_prediction,
#                 ml_confidence,
#                 lstm_prediction,
#                 lstm_confidence,
#                 created_at
#             FROM review_history
#             WHERE user_id = ?
#             ORDER BY id DESC
#             """,
#             (session["user_id"],)
#         ).fetchall()

#         return jsonify([
#             dict(row) for row in rows
#         ]), 200

#     except sqlite3.Error as error:

#         return jsonify({
#             "error": "Unable to retrieve review history.",
#             "details": str(error)
#         }), 500

#     finally:
#         conn.close()


# # --------------------------------------------------
# # 15. DELETE REVIEW HISTORY
# # --------------------------------------------------

# @app.route("/history/<int:review_id>", methods=["DELETE"])
# @login_required
# def delete_review_history(review_id):

#     conn = get_db_connection()

#     try:

#         cursor = conn.execute(
#             """
#             DELETE FROM review_history
#             WHERE id = ? AND user_id = ?
#             """,
#             (
#                 review_id,
#                 session["user_id"]
#             )
#         )

#         conn.commit()

#         if cursor.rowcount == 0:
#             return jsonify({
#                 "error": "Review not found."
#             }), 404

#         return jsonify({
#             "message": "Review deleted successfully."
#         }), 200

#     except sqlite3.Error as error:

#         conn.rollback()

#         return jsonify({
#             "error": "Unable to delete review.",
#             "details": str(error)
#         }), 500

#     finally:
#         conn.close()


# # --------------------------------------------------
# # 16. CSV AND JSON FILE UPLOAD
# # --------------------------------------------------

# @app.route("/upload", methods=["POST"])
# @login_required
# def upload():

#     file = request.files.get("file")

#     if not file or not file.filename:
#         return jsonify({
#             "error": "No file uploaded."
#         }), 400

#     filename = file.filename.lower()

#     if not filename.endswith((".csv", ".json")):
#         return jsonify({
#             "error": "Only CSV or JSON files are allowed."
#         }), 400

#     try:

#         if filename.endswith(".csv"):
#             df = pd.read_csv(file)

#         else:
#             df = pd.read_json(file)

#         if "review" not in df.columns:
#             return jsonify({
#                 "error": "File must contain a 'review' column."
#             }), 400

#         results = []

#         for review in df["review"]:

#             if pd.isna(review) or not str(review).strip():
#                 results.append({
#                     "review": review if not pd.isna(review) else "",
#                     "prediction": "Invalid",
#                     "confidence": 0
#                 })
#                 continue

#             cleaned_review = clean_text(review)

#             vec = vectorizer.transform(
#                 [cleaned_review]
#             )

#             result = get_best_prediction(vec)

#             results.append({
#                 "review": str(review),
#                 "prediction": result["prediction"],
#                 "confidence": result["confidence"]
#             })

#         return jsonify(results), 200

#     except Exception as error:

#         app.logger.exception("File upload failed")

#         return jsonify({
#             "error": "Unable to process uploaded file.",
#             "details": str(error)
#         }), 400


# # --------------------------------------------------
# # 17. HOME / TEST ROUTE
# # --------------------------------------------------

# @app.route("/", methods=["GET"])
# def home():

#     return jsonify({
#         "message": "Fake Review Detection Backend is running."
#     }), 200


# # --------------------------------------------------
# # 18. RUN FLASK SERVER
# # --------------------------------------------------

# if __name__ == "__main__":

#     app.run(
#         host="127.0.0.1",
#         port=5000,
#         debug=True,
#         use_reloader=False
#     )





import os
import re
import string
import pickle
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import wraps

import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.preprocessing.sequence import pad_sequences


# --------------------------------------------------
# 1. PATHS AND DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "reviews.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                review TEXT NOT NULL,
                ml_prediction TEXT,
                ml_confidence REAL,
                lstm_prediction TEXT,
                lstm_confidence REAL,
                created_at TEXT NOT NULL
            )
        """)
        columns = {
            row[1] for row in
            conn.execute("PRAGMA table_info(review_history)").fetchall()
        }
        if "user_id" not in columns:
            conn.execute("ALTER TABLE review_history ADD COLUMN user_id INTEGER")
        conn.commit()
    finally:
        conn.close()


init_db()


# --------------------------------------------------
# 2. LOAD TRAINED MACHINE-LEARNING MODELS
# --------------------------------------------------

def load_pickle(filename):
    path = BASE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Required file is missing: {path}. Run train_model.py first."
        )
    with path.open("rb") as file:
        return pickle.load(file)


lr_model = load_pickle("lr_model.pkl")
nb_model = load_pickle("nb_model.pkl")
vectorizer = load_pickle("vectorizer.pkl")

# Random Forest is optional. If its file is unavailable, LR and NB still run.
try:
    rf_model = load_pickle("rf_model.pkl")
    print("Random Forest model loaded successfully.")
except Exception as error:
    print(f"Random Forest unavailable: {error}")
    rf_model = None


# --------------------------------------------------
# 3. LOAD TRAINED LSTM MODEL AND TOKENIZER
# --------------------------------------------------

MODEL_PATH = BASE_DIR / "lstm_model.keras"
TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"

if not MODEL_PATH.is_file():
    raise FileNotFoundError(
        f"Required file is missing: {MODEL_PATH}. Run train_dl_model.py first."
    )
if not TOKENIZER_PATH.is_file():
    raise FileNotFoundError(
        f"Required file is missing: {TOKENIZER_PATH}. Run train_dl_model.py first."
    )

lstm_model = tf.keras.models.load_model(MODEL_PATH)
with TOKENIZER_PATH.open("rb") as file:
    lstm_tokenizer = pickle.load(file)

MAX_LENGTH = 150


# --------------------------------------------------
# 4. FLASK APPLICATION AND CORS
# --------------------------------------------------

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-secret"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
)

CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)


# --------------------------------------------------
# 5. AUTHENTICATION HELPER
# --------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Please log in to continue."}), 401
        return view(*args, **kwargs)
    return wrapped


# --------------------------------------------------
# 6. TEXT CLEANING
# Keep these functions consistent with the two training scripts.
# --------------------------------------------------

def clean_ml_text(text):
    """Cleaning used by train_model.py (TF-IDF models)."""
    text = str(text).lower()
    text = re.sub(r"\d+", "", text)
    return text.translate(str.maketrans("", "", string.punctuation))


def clean_lstm_text(text):
    """Cleaning used by train_dl_model.py (LSTM model)."""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def label_name(value):
    """Project convention: 1 = Fake and 0 = Genuine."""
    try:
        return "Fake" if int(value) == 1 else "Genuine"
    except (TypeError, ValueError):
        normalized = str(value).strip().lower()
        if normalized in {"fake", "deceptive", "false", "1"}:
            return "Fake"
        return "Genuine"


# --------------------------------------------------
# 7. USER REGISTRATION
# --------------------------------------------------

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required."}), 400
    if len(name) > 80 or len(email) > 254 or "@" not in email:
        return jsonify({"error": "Please enter a valid name and email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must contain at least 8 characters."}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO users (name, email, password_hash, created_at)
               VALUES (?, ?, ?, ?)""",
            (
                name,
                email,
                generate_password_hash(password),
                datetime.now().astimezone().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with this email already exists. Please log in."}), 409
    finally:
        conn.close()

    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name
    session.permanent = True
    return jsonify({
        "message": "Account created successfully.",
        "user": {"id": user_id, "name": name, "email": email},
    }), 201


# --------------------------------------------------
# 8. USER LOGIN
# --------------------------------------------------

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect email or password."}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session.permanent = True
    return jsonify({
        "message": "Login successful.",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }), 200


# --------------------------------------------------
# 9. CHECK CURRENT USER
# --------------------------------------------------

@app.route("/auth/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None}), 200

    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if not user:
        session.clear()
        return jsonify({"user": None}), 200
    return jsonify({"user": dict(user)}), 200


# --------------------------------------------------
# 10. LOGOUT
# --------------------------------------------------

@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


# --------------------------------------------------
# 11. MACHINE-LEARNING PREDICTION
# --------------------------------------------------

def get_best_prediction(vectorized_review):
    models = [lr_model, nb_model]
    if rf_model is not None:
        models.append(rf_model)

    results = []
    for model in models:
        predicted_class = model.predict(vectorized_review)[0]
        probabilities = model.predict_proba(vectorized_review)[0]
        confidence = float(np.max(probabilities))
        results.append({
            "prediction": label_name(predicted_class),
            "confidence": confidence,
        })

    best = max(results, key=lambda item: item["confidence"])
    return {
        "prediction": best["prediction"],
        "confidence": round(best["confidence"], 2),
    }


# --------------------------------------------------
# 12. LSTM PREDICTION
# --------------------------------------------------

def get_lstm_prediction(review):
    cleaned_review = clean_lstm_text(review)
    sequence = lstm_tokenizer.texts_to_sequences([cleaned_review])
    padded = pad_sequences(
        sequence,
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post",
    )

    probability = float(
        np.asarray(lstm_model.predict(padded, verbose=0)).reshape(-1)[0]
    )
    # The training script requires label 1 = Fake and label 0 = Genuine.
    predicted_class = 1 if probability >= 0.5 else 0
    confidence = probability if predicted_class == 1 else 1.0 - probability

    return {
        "prediction": "Fake" if predicted_class == 1 else "Genuine",
        "confidence": round(confidence, 2),
    }


# --------------------------------------------------
# 13. ANALYZE ONE REVIEW
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    data = request.get_json(silent=True) or {}
    review = data.get("review")

    if not review or not str(review).strip():
        return jsonify({"error": "Please enter a review."}), 400

    try:
        cleaned_review = clean_ml_text(review)
        vectorized_review = vectorizer.transform([cleaned_review])

        ml_result = get_best_prediction(vectorized_review)
        lstm_result = get_lstm_prediction(review)

        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO review_history
                   (user_id, review, ml_prediction, ml_confidence,
                    lstm_prediction, lstm_confidence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    session["user_id"],
                    str(review),
                    ml_result["prediction"],
                    ml_result["confidence"],
                    lstm_result["prediction"],
                    lstm_result["confidence"],
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return jsonify({
            "ml_prediction": ml_result,
            "lstm_prediction": lstm_result,
        }), 200

    except Exception as error:
        app.logger.exception("Review analysis failed")
        return jsonify({
            "error": "Review analysis failed.",
            "details": str(error),
        }), 500


# --------------------------------------------------
# 14. GET REVIEW HISTORY
# --------------------------------------------------

@app.route("/history", methods=["GET"])
@login_required
def get_review_history():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, review, ml_prediction, ml_confidence,
                      lstm_prediction, lstm_confidence, created_at
               FROM review_history
               WHERE user_id = ?
               ORDER BY id DESC""",
            (session["user_id"],),
        ).fetchall()
        return jsonify([dict(row) for row in rows]), 200
    except sqlite3.Error as error:
        return jsonify({
            "error": "Unable to retrieve review history.",
            "details": str(error),
        }), 500
    finally:
        conn.close()


# --------------------------------------------------
# 15. DELETE ONE REVIEW FROM HISTORY
# --------------------------------------------------

@app.route("/history/<int:review_id>", methods=["DELETE"])
@login_required
def delete_review_history(review_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM review_history WHERE id = ? AND user_id = ?",
            (review_id, session["user_id"]),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Review not found."}), 404
        return jsonify({"message": "Review deleted successfully."}), 200
    except sqlite3.Error as error:
        conn.rollback()
        return jsonify({
            "error": "Unable to delete review.",
            "details": str(error),
        }), 500
    finally:
        conn.close()


# --------------------------------------------------
# 16. CSV OR JSON REVIEW FILE UPLOAD
# --------------------------------------------------

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "No file uploaded."}), 400

    filename = uploaded_file.filename.lower()
    if filename.endswith(".csv"):
        try:
            dataframe = pd.read_csv(uploaded_file)
        except Exception as error:
            return jsonify({"error": f"Unable to read CSV file: {error}"}), 400
    elif filename.endswith(".json"):
        try:
            dataframe = pd.read_json(uploaded_file)
        except Exception as error:
            return jsonify({"error": f"Unable to read JSON file: {error}"}), 400
    else:
        return jsonify({"error": "Only CSV or JSON files are allowed."}), 400

    if "review" not in dataframe.columns:
        return jsonify({"error": "File must contain a 'review' column."}), 400

    results = []
    try:
        for review in dataframe["review"]:
            if pd.isna(review) or not str(review).strip():
                results.append({
                    "review": "" if pd.isna(review) else str(review),
                    "prediction": "Invalid",
                    "confidence": 0,
                })
                continue

            cleaned_review = clean_ml_text(review)
            vectorized_review = vectorizer.transform([cleaned_review])
            prediction = get_best_prediction(vectorized_review)
            results.append({
                "review": str(review),
                "prediction": prediction["prediction"],
                "confidence": prediction["confidence"],
            })
        return jsonify(results), 200
    except Exception as error:
        app.logger.exception("File prediction failed")
        return jsonify({
            "error": "Unable to process uploaded file.",
            "details": str(error),
        }), 400


# --------------------------------------------------
# 17. HOME / HEALTH CHECK
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Fake Review Detection Backend is running."
    }), 200


# --------------------------------------------------
# 18. RUN FLASK SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False,
    )
