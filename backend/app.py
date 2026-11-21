# # # import os
# # # import re
# # # import string
# # # import pickle
# # # import sqlite3
# # # from pathlib import Path
# # # from datetime import datetime
# # # from functools import wraps
# # # import numpy as np
# # # import pandas as pd
# # # import tensorflow as tf
# # # from flask import Flask, request, jsonify, session
# # # from flask_cors import CORS
# # # from werkzeug.security import generate_password_hash, check_password_hash
# # # from tensorflow.keras.preprocessing.sequence import pad_sequences
# # # # --------------------------------------------------
# # # # 1. PATHS AND DATABASE
# # # # --------------------------------------------------
# # # print("RUNNING APP FROM:", __file__)
# # # print("USING SOFT VOTING PREDICTION")
# # # BASE_DIR = Path(__file__).resolve().parent
# # # DATABASE_PATH = BASE_DIR / "reviews.db"
# # # def get_db_connection():
# # #     conn = sqlite3.connect(DATABASE_PATH)
# # #     conn.row_factory = sqlite3.Row
# # #     return conn
# # # def init_db():
# # #     conn = get_db_connection()
# # #     try:
# # #         conn.execute("""
# # #             CREATE TABLE IF NOT EXISTS users (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 name TEXT NOT NULL,
# # #                 email TEXT NOT NULL UNIQUE COLLATE NOCASE,
# # #                 password_hash TEXT NOT NULL,
# # #                 created_at TEXT NOT NULL
# # #             )
# # #         """)
# # #         conn.execute("""
# # #             CREATE TABLE IF NOT EXISTS review_history (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 user_id INTEGER,
# # #                 review TEXT NOT NULL,
# # #                 ml_prediction TEXT,
# # #                 ml_confidence REAL,
# # #                 lstm_prediction TEXT,
# # #                 lstm_confidence REAL,
# # #                 created_at TEXT NOT NULL
# # #             )
# # #         """)
# # #         columns = {
# # #             row[1] for row in
# # #             conn.execute("PRAGMA table_info(review_history)").fetchall()
# # #         }
# # #         if "user_id" not in columns:
# # #             conn.execute("ALTER TABLE review_history ADD COLUMN user_id INTEGER")
# # #         conn.commit()
# # #     finally:
# # #         conn.close()
# # # init_db()
# # # # --------------------------------------------------
# # # # 2. LOAD TRAINED MACHINE-LEARNING MODELS
# # # # --------------------------------------------------
# # # def load_pickle(filename):
# # #     path = BASE_DIR / filename
# # #     if not path.is_file():
# # #         raise FileNotFoundError(
# # #             f"Required file is missing: {path}. Run train_model.py first."
# # #         )
# # #     with path.open("rb") as file:
# # #         return pickle.load(file)
# # # lr_model = load_pickle("lr_model.pkl")
# # # nb_model = load_pickle("nb_model.pkl")
# # # vectorizer = load_pickle("vectorizer.pkl")
# # # # Random Forest is optional. If its file is unavailable, LR and NB still run.
# # # try:
# # #     rf_model = load_pickle("rf_model.pkl")
# # #     print("Random Forest model loaded successfully.")
# # # except Exception as error:
# # #     print(f"Random Forest unavailable: {error}")
# # #     rf_model = None
# # # # --------------------------------------------------
# # # # 3. LOAD TRAINED LSTM MODEL AND TOKENIZER
# # # # --------------------------------------------------
# # # MODEL_PATH = BASE_DIR / "lstm_model.keras"
# # # TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"
# # # if not MODEL_PATH.is_file():
# # #     raise FileNotFoundError(
# # #         f"Required file is missing: {MODEL_PATH}. Run train_dl_model.py first."
# # #     )
# # # if not TOKENIZER_PATH.is_file():
# # #     raise FileNotFoundError(
# # #         f"Required file is missing: {TOKENIZER_PATH}. Run train_dl_model.py first."
# # #     )
# # # lstm_model = tf.keras.models.load_model(MODEL_PATH)
# # # with TOKENIZER_PATH.open("rb") as file:
# # #     lstm_tokenizer = pickle.load(file)
# # # MAX_LENGTH = 150
# # # # --------------------------------------------------
# # # # 4. FLASK APPLICATION AND CORS
# # # # --------------------------------------------------
# # # app = Flask(__name__)
# # # app.config.update(
# # #     SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-secret"),
# # #     SESSION_COOKIE_HTTPONLY=True,
# # #     SESSION_COOKIE_SAMESITE="Lax",
# # #     SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
# # #     PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
# # # )
# # # CORS(
# # #     app,
# # #     supports_credentials=True,
# # #     origins=[
# # #         "http://localhost:5173",
# # #         "http://127.0.0.1:5173",
# # #     ],
# # # )
# # # # --------------------------------------------------
# # # # 5. AUTHENTICATION HELPER
# # # # --------------------------------------------------
# # # def login_required(view):
# # #     @wraps(view)
# # #     def wrapped(*args, **kwargs):
# # #         if not session.get("user_id"):
# # #             return jsonify({"error": "Please log in to continue."}), 401
# # #         return view(*args, **kwargs)
# # #     return wrapped
# # # # --------------------------------------------------
# # # # 6. TEXT CLEANING
# # # # Keep these functions consistent with the two training scripts.
# # # # --------------------------------------------------
# # # def clean_ml_text(text):
# # #     """Cleaning used by train_model.py (TF-IDF models)."""
# # #     text = str(text).lower()
# # #     text = re.sub(r"\d+", "", text)
# # #     return text.translate(str.maketrans("", "", string.punctuation))
# # # def clean_lstm_text(text):
# # #     """Cleaning used by train_dl_model.py (LSTM model)."""
# # #     text = str(text).lower()
# # #     text = re.sub(r"http\S+|www\S+", " ", text)
# # #     text = re.sub(r"[^a-z\s]", " ", text)
# # #     return re.sub(r"\s+", " ", text).strip()
# # # def label_name(value):
# # #     """Project convention: 1 = Fake and 0 = Genuine."""
# # #     try:
# # #         return "Fake" if int(value) == 1 else "Genuine"
# # #     except (TypeError, ValueError):
# # #         normalized = str(value).strip().lower()
# # #         if normalized in {"fake", "deceptive", "false", "1"}:
# # #             return "Fake"
# # #         return "Genuine"
# # # # --------------------------------------------------
# # # # 7. USER REGISTRATION
# # # # --------------------------------------------------
# # # @app.route("/auth/register", methods=["POST"])
# # # def register():
# # #     data = request.get_json(silent=True) or {}
# # #     name = str(data.get("name", "")).strip()
# # #     email = str(data.get("email", "")).strip().lower()
# # #     password = str(data.get("password", ""))
# # #     if not name or not email or not password:
# # #         return jsonify({"error": "Name, email and password are required."}), 400
# # #     if len(name) > 80 or len(email) > 254 or "@" not in email:
# # #         return jsonify({"error": "Please enter a valid name and email address."}), 400
# # #     if len(password) < 8:
# # #         return jsonify({"error": "Password must contain at least 8 characters."}), 400
# # #     conn = get_db_connection()
# # #     try:
# # #         cursor = conn.execute(
# # #             """INSERT INTO users (name, email, password_hash, created_at)
# # #                VALUES (?, ?, ?, ?)""",
# # #             (
# # #                 name,
# # #                 email,
# # #                 generate_password_hash(password),
# # #                 datetime.now().astimezone().isoformat(timespec="seconds"),
# # #             ),
# # #         )
# # #         conn.commit()
# # #         user_id = cursor.lastrowid
# # #     except sqlite3.IntegrityError:
# # #         return jsonify({"error": "An account with this email already exists. Please log in."}), 409
# # #     finally:
# # #         conn.close()
# # #     session.clear()
# # #     session["user_id"] = user_id
# # #     session["user_name"] = name
# # #     session.permanent = True
# # #     return jsonify({
# # #         "message": "Account created successfully.",
# # #         "user": {"id": user_id, "name": name, "email": email},
# # #     }), 201
# # # # --------------------------------------------------
# # # # 8. USER LOGIN
# # # # --------------------------------------------------
# # # @app.route("/auth/login", methods=["POST"])
# # # def login():
# # #     data = request.get_json(silent=True) or {}
# # #     email = str(data.get("email", "")).strip().lower()
# # #     password = str(data.get("password", ""))
# # #     conn = get_db_connection()
# # #     try:
# # #         user = conn.execute(
# # #             "SELECT id, name, email, password_hash FROM users WHERE email = ?",
# # #             (email,),
# # #         ).fetchone()
# # #     finally:
# # #         conn.close()
# # #     if not user or not check_password_hash(user["password_hash"], password):
# # #         return jsonify({"error": "Incorrect email or password."}), 401
# # #     session.clear()
# # #     session["user_id"] = user["id"]
# # #     session["user_name"] = user["name"]
# # #     session.permanent = True
# # #     return jsonify({
# # #         "message": "Login successful.",
# # #         "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
# # #     }), 200
# # # # --------------------------------------------------
# # # # 9. CHECK CURRENT USER
# # # # --------------------------------------------------
# # # @app.route("/auth/me", methods=["GET"])
# # # def current_user():
# # #     user_id = session.get("user_id")
# # #     if not user_id:
# # #         return jsonify({"user": None}), 200
# # #     conn = get_db_connection()
# # #     try:
# # #         user = conn.execute(
# # #             "SELECT id, name, email FROM users WHERE id = ?",
# # #             (user_id,),
# # #         ).fetchone()
# # #     finally:
# # #         conn.close()
# # #     if not user:
# # #         session.clear()
# # #         return jsonify({"user": None}), 200
# # #     return jsonify({"user": dict(user)}), 200
# # # # --------------------------------------------------
# # # # 10. LOGOUT
# # # # --------------------------------------------------
# # # @app.route("/auth/logout", methods=["POST"])
# # # def logout():
# # #     session.clear()
# # #     return jsonify({"message": "Logged out successfully."}), 200
# # # # --------------------------------------------------
# # # # 11. MACHINE-LEARNING PREDICTION
# # # # --------------------------------------------------
# # # # def get_best_prediction(vectorized_review):
# # # #     models = [lr_model, nb_model]
# # # #     if rf_model is not None:
# # # #         models.append(rf_model)
# # # #     results = []
# # # #     for model in models:
# # # #         predicted_class = model.predict(vectorized_review)[0]
# # # #         probabilities = model.predict_proba(vectorized_review)[0]
# # # #         confidence = float(np.max(probabilities))
# # # #         results.append({
# # # #             "prediction": label_name(predicted_class),
# # # #             "confidence": confidence,
# # # #         })
# # # #     best = max(results, key=lambda item: item["confidence"])
# # # #     return {
# # # #         "prediction": best["prediction"],
# # # #         "confidence": round(best["confidence"], 2),
# # # #     }
# # # def get_best_prediction(vectorized_review):
# # #     print("MODEL PROBABILITIES:", fake_probabilities)
# # #     print("AVERAGE FAKE PROBABILITY:", avg_fake_probability)
# # #     print("FINAL PREDICTION:", prediction)
# # #     models = [lr_model, nb_model]
# # #     if rf_model is not None:
# # #         models.append(rf_model)
# # #     fake_probabilities = []
# # #     for model in models:
# # #         probabilities = model.predict_proba(vectorized_review)[0]
# # #         # Find the probability corresponding to label 1 (Fake)
# # #         fake_index = list(model.classes_).index(1)
# # #         fake_probabilities.append(float(probabilities[fake_index]))
# # #     # Average the Fake probabilities across models
# # #     avg_fake_probability = sum(fake_probabilities) / len(fake_probabilities)
# # #     prediction = (
# # #         "Fake" if avg_fake_probability >= 0.5
# # #         else "Genuine"
# # #     )
# # #     confidence = max(
# # #         avg_fake_probability,
# # #         1 - avg_fake_probability
# # #     )
# # #     return {
# # #         "prediction": prediction,
# # #         "confidence": round(confidence, 2)
# # #     }
# # # # --------------------------------------------------
# # # # 12. LSTM PREDICTION
# # # # --------------------------------------------------
# # # def get_lstm_prediction(review):
# # #     cleaned_review = clean_lstm_text(review)
# # #     sequence = lstm_tokenizer.texts_to_sequences([cleaned_review])
# # #     padded = pad_sequences(
# # #         sequence,
# # #         maxlen=MAX_LENGTH,
# # #         padding="post",
# # #         truncating="post",
# # #     )
# # #     probability = float(
# # #         np.asarray(lstm_model.predict(padded, verbose=0)).reshape(-1)[0]
# # #     )
# # #     # The training script requires label 1 = Fake and label 0 = Genuine.
# # #     predicted_class = 1 if probability >= 0.5 else 0
# # #     confidence = probability if predicted_class == 1 else 1.0 - probability
# # #     return {
# # #         "prediction": "Fake" if predicted_class == 1 else "Genuine",
# # #         "confidence": round(confidence, 2),
# # #     }
# # # # --------------------------------------------------
# # # # 13. ANALYZE ONE REVIEW
# # # # --------------------------------------------------
# # # @app.route("/analyze", methods=["POST"])
# # # @login_required
# # # def analyze():
# # #     data = request.get_json(silent=True) or {}
# # #     review = data.get("review")
# # #     if not review or not str(review).strip():
# # #         return jsonify({"error": "Please enter a review."}), 400
# # #     try:
# # #         cleaned_review = clean_ml_text(review)
# # #         vectorized_review = vectorizer.transform([cleaned_review])
# # #         ml_result = get_best_prediction(vectorized_review)
# # #         lstm_result = get_lstm_prediction(review)
# # #         conn = get_db_connection()
# # #         try:
# # #             conn.execute(
# # #                 """INSERT INTO review_history
# # #                    (user_id, review, ml_prediction, ml_confidence,
# # #                     lstm_prediction, lstm_confidence, created_at)
# # #                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
# # #                 (
# # #                     session["user_id"],
# # #                     str(review),
# # #                     ml_result["prediction"],
# # #                     ml_result["confidence"],
# # #                     lstm_result["prediction"],
# # #                     lstm_result["confidence"],
# # #                     datetime.now().astimezone().isoformat(timespec="seconds"),
# # #                 ),
# # #             )
# # #             conn.commit()
# # #         finally:
# # #             conn.close()
# # #         return jsonify({
# # #             "ml_prediction": ml_result,
# # #             "lstm_prediction": lstm_result,
# # #         }), 200
# # #     except Exception as error:
# # #         app.logger.exception("Review analysis failed")
# # #         return jsonify({
# # #             "error": "Review analysis failed.",
# # #             "details": str(error),
# # #         }), 500
# # # # --------------------------------------------------
# # # # 14. GET REVIEW HISTORY
# # # # --------------------------------------------------
# # # @app.route("/history", methods=["GET"])
# # # @login_required
# # # def get_review_history():
# # #     conn = get_db_connection()
# # #     try:
# # #         rows = conn.execute(
# # #             """SELECT id, review, ml_prediction, ml_confidence,
# # #                       lstm_prediction, lstm_confidence, created_at
# # #                FROM review_history
# # #                WHERE user_id = ?
# # #                ORDER BY id DESC""",
# # #             (session["user_id"],),
# # #         ).fetchall()
# # #         return jsonify([dict(row) for row in rows]), 200
# # #     except sqlite3.Error as error:
# # #         return jsonify({
# # #             "error": "Unable to retrieve review history.",
# # #             "details": str(error),
# # #         }), 500
# # #     finally:
# # #         conn.close()
# # # # --------------------------------------------------
# # # # 15. DELETE ONE REVIEW FROM HISTORY
# # # # --------------------------------------------------
# # # @app.route("/history/<int:review_id>", methods=["DELETE"])
# # # @login_required
# # # def delete_review_history(review_id):
# # #     conn = get_db_connection()
# # #     try:
# # #         cursor = conn.execute(
# # #             "DELETE FROM review_history WHERE id = ? AND user_id = ?",
# # #             (review_id, session["user_id"]),
# # #         )
# # #         conn.commit()
# # #         if cursor.rowcount == 0:
# # #             return jsonify({"error": "Review not found."}), 404
# # #         return jsonify({"message": "Review deleted successfully."}), 200
# # #     except sqlite3.Error as error:
# # #         conn.rollback()
# # #         return jsonify({
# # #             "error": "Unable to delete review.",
# # #             "details": str(error),
# # #         }), 500
# # #     finally:
# # #         conn.close()
# # # # --------------------------------------------------
# # # # 16. CSV OR JSON REVIEW FILE UPLOAD
# # # # --------------------------------------------------
# # # @app.route("/upload", methods=["POST"])
# # # @login_required
# # # def upload():
# # #     uploaded_file = request.files.get("file")
# # #     if not uploaded_file or not uploaded_file.filename:
# # #         return jsonify({"error": "No file uploaded."}), 400
# # #     filename = uploaded_file.filename.lower()
# # #     if filename.endswith(".csv"):
# # #         try:
# # #             dataframe = pd.read_csv(uploaded_file)
# # #         except Exception as error:
# # #             return jsonify({"error": f"Unable to read CSV file: {error}"}), 400
# # #     elif filename.endswith(".json"):
# # #         try:
# # #             dataframe = pd.read_json(uploaded_file)
# # #         except Exception as error:
# # #             return jsonify({"error": f"Unable to read JSON file: {error}"}), 400
# # #     else:
# # #         return jsonify({"error": "Only CSV or JSON files are allowed."}), 400
# # #     if "review" not in dataframe.columns:
# # #         return jsonify({"error": "File must contain a 'review' column."}), 400
# # #     results = []
# # #     try:
# # #         for review in dataframe["review"]:
# # #             if pd.isna(review) or not str(review).strip():
# # #                 results.append({
# # #                     "review": "" if pd.isna(review) else str(review),
# # #                     "prediction": "Invalid",
# # #                     "confidence": 0,
# # #                 })
# # #                 continue
# # #             cleaned_review = clean_ml_text(review)
# # #             vectorized_review = vectorizer.transform([cleaned_review])
# # #             prediction = get_best_prediction(vectorized_review)
# # #             results.append({
# # #                 "review": str(review),
# # #                 "prediction": prediction["prediction"],
# # #                 "confidence": prediction["confidence"],
# # #             })
# # #         return jsonify(results), 200
# # #     except Exception as error:
# # #         app.logger.exception("File prediction failed")
# # #         return jsonify({
# # #             "error": "Unable to process uploaded file.",
# # #             "details": str(error),
# # #         }), 400
# # # # --------------------------------------------------
# # # # 17. HOME / HEALTH CHECK
# # # # --------------------------------------------------
# # # @app.route("/", methods=["GET"])
# # # def home():
# # #     return jsonify({
# # #         "message": "Fake Review Detection Backend is running."
# # #     }), 200
# # # # --------------------------------------------------
# # # # 18. RUN FLASK SERVER
# # # # --------------------------------------------------
# # # if __name__ == "__main__":
# # #     app.run(
# # #         host="127.0.0.1",
# # #         port=5000,
# # #         debug=True,
# # #         use_reloader=False,
# # #     )
# # import os
# # import re
# # import string
# # import pickle
# # import sqlite3
# # from pathlib import Path
# # from datetime import datetime
# # from functools import wraps
# # import numpy as np
# # import pandas as pd
# # import tensorflow as tf
# # from flask import Flask, request, jsonify, session
# # from flask_cors import CORS
# # from werkzeug.security import generate_password_hash, check_password_hash
# # from tensorflow.keras.preprocessing.sequence import pad_sequences
# # # --------------------------------------------------
# # # 1. PATHS AND DATABASE
# # # --------------------------------------------------
# # print("RUNNING APP FROM:", __file__)
# # print("USING SOFT VOTING PREDICTION")
# # BASE_DIR = Path(__file__).resolve().parent
# # DATABASE_PATH = BASE_DIR / "reviews.db"
# # def get_db_connection():
# #     conn = sqlite3.connect(DATABASE_PATH)
# #     conn.row_factory = sqlite3.Row
# #     return conn
# # def init_db():
# #     conn = get_db_connection()
# #     try:
# #         conn.execute("""
# #             CREATE TABLE IF NOT EXISTS users (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 name TEXT NOT NULL,
# #                 email TEXT NOT NULL UNIQUE COLLATE NOCASE,
# #                 password_hash TEXT NOT NULL,
# #                 created_at TEXT NOT NULL
# #             )
# #         """)
# #         conn.execute("""
# #             CREATE TABLE IF NOT EXISTS review_history (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 user_id INTEGER,
# #                 review TEXT NOT NULL,
# #                 ml_prediction TEXT,
# #                 ml_confidence REAL,
# #                 lstm_prediction TEXT,
# #                 lstm_confidence REAL,
# #                 created_at TEXT NOT NULL
# #             )
# #         """)
# #         columns = {
# #             row[1] for row in
# #             conn.execute("PRAGMA table_info(review_history)").fetchall()
# #         }
# #         if "user_id" not in columns:
# #             conn.execute("ALTER TABLE review_history ADD COLUMN user_id INTEGER")
# #         conn.commit()
# #     finally:
# #         conn.close()
# # init_db()
# # # --------------------------------------------------
# # # 2. LOAD TRAINED MACHINE-LEARNING MODELS
# # # --------------------------------------------------
# # def load_pickle(filename):
# #     path = BASE_DIR / filename
# #     if not path.is_file():
# #         raise FileNotFoundError(
# #             f"Required file is missing: {path}. Run train_model.py first."
# #         )
# #     with path.open("rb") as file:
# #         return pickle.load(file)
# # lr_model = load_pickle("lr_model.pkl")
# # nb_model = load_pickle("nb_model.pkl")
# # vectorizer = load_pickle("vectorizer.pkl")
# # # Random Forest is optional. If its file is unavailable, LR and NB still run.
# # try:
# #     rf_model = load_pickle("rf_model.pkl")
# #     print("Random Forest model loaded successfully.")
# # except Exception as error:
# #     print(f"Random Forest unavailable: {error}")
# #     rf_model = None
# # # --------------------------------------------------
# # # 3. LOAD TRAINED LSTM MODEL AND TOKENIZER
# # # --------------------------------------------------
# # MODEL_PATH = BASE_DIR / "lstm_model.keras"
# # TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"
# # if not MODEL_PATH.is_file():
# #     raise FileNotFoundError(
# #         f"Required file is missing: {MODEL_PATH}. Run train_dl_model.py first."
# #     )
# # if not TOKENIZER_PATH.is_file():
# #     raise FileNotFoundError(
# #         f"Required file is missing: {TOKENIZER_PATH}. Run train_dl_model.py first."
# #     )
# # lstm_model = tf.keras.models.load_model(MODEL_PATH)
# # with TOKENIZER_PATH.open("rb") as file:
# #     lstm_tokenizer = pickle.load(file)
# # MAX_LENGTH = 150
# # # --------------------------------------------------
# # # 4. FLASK APPLICATION AND CORS
# # # --------------------------------------------------
# # app = Flask(__name__)
# # app.config.update(
# #     SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-secret"),
# #     SESSION_COOKIE_HTTPONLY=True,
# #     SESSION_COOKIE_SAMESITE="Lax",
# #     SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
# #     PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
# # )
# # CORS(
# #     app,
# #     supports_credentials=True,
# #     origins=[
# #         "http://localhost:5173",
# #         "http://127.0.0.1:5173",
# #     ],
# # )
# # # --------------------------------------------------
# # # 5. AUTHENTICATION HELPER
# # # --------------------------------------------------
# # def login_required(view):
# #     @wraps(view)
# #     def wrapped(*args, **kwargs):
# #         if not session.get("user_id"):
# #             return jsonify({"error": "Please log in to continue."}), 401
# #         return view(*args, **kwargs)
# #     return wrapped
# # # --------------------------------------------------
# # # 6. TEXT CLEANING
# # # Keep these functions consistent with the two training scripts.
# # # --------------------------------------------------
# # def clean_ml_text(text):
# #     """Cleaning used by train_model.py (TF-IDF models)."""
# #     text = str(text).lower()
# #     text = re.sub(r"\d+", "", text)
# #     return text.translate(str.maketrans("", "", string.punctuation))
# # def clean_lstm_text(text):
# #     """Cleaning used by train_dl_model.py (LSTM model)."""
# #     text = str(text).lower()
# #     text = re.sub(r"http\S+|www\S+", " ", text)
# #     text = re.sub(r"[^a-z\s]", " ", text)
# #     return re.sub(r"\s+", " ", text).strip()
# # def label_name(value):
# #     """Project convention: 1 = Fake and 0 = Genuine."""
# #     try:
# #         return "Fake" if int(value) == 1 else "Genuine"
# #     except (TypeError, ValueError):
# #         normalized = str(value).strip().lower()
# #         if normalized in {"fake", "deceptive", "false", "1"}:
# #             return "Fake"
# #         return "Genuine"
# # # --------------------------------------------------
# # # 7. USER REGISTRATION
# # # --------------------------------------------------
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
# #             """INSERT INTO users (name, email, password_hash, created_at)
# #                VALUES (?, ?, ?, ?)""",
# #             (
# #                 name,
# #                 email,
# #                 generate_password_hash(password),
# #                 datetime.now().astimezone().isoformat(timespec="seconds"),
# #             ),
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
# #     return jsonify({
# #         "message": "Account created successfully.",
# #         "user": {"id": user_id, "name": name, "email": email},
# #     }), 201
# # # --------------------------------------------------
# # # 8. USER LOGIN
# # # --------------------------------------------------
# # @app.route("/auth/login", methods=["POST"])
# # def login():
# #     data = request.get_json(silent=True) or {}
# #     email = str(data.get("email", "")).strip().lower()
# #     password = str(data.get("password", ""))
# #     conn = get_db_connection()
# #     try:
# #         user = conn.execute(
# #             "SELECT id, name, email, password_hash FROM users WHERE email = ?",
# #             (email,),
# #         ).fetchone()
# #     finally:
# #         conn.close()
# #     if not user or not check_password_hash(user["password_hash"], password):
# #         return jsonify({"error": "Incorrect email or password."}), 401
# #     session.clear()
# #     session["user_id"] = user["id"]
# #     session["user_name"] = user["name"]
# #     session.permanent = True
# #     return jsonify({
# #         "message": "Login successful.",
# #         "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
# #     }), 200
# # # --------------------------------------------------
# # # 9. CHECK CURRENT USER
# # # --------------------------------------------------
# # @app.route("/auth/me", methods=["GET"])
# # def current_user():
# #     user_id = session.get("user_id")
# #     if not user_id:
# #         return jsonify({"user": None}), 200
# #     conn = get_db_connection()
# #     try:
# #         user = conn.execute(
# #             "SELECT id, name, email FROM users WHERE id = ?",
# #             (user_id,),
# #         ).fetchone()
# #     finally:
# #         conn.close()
# #     if not user:
# #         session.clear()
# #         return jsonify({"user": None}), 200
# #     return jsonify({"user": dict(user)}), 200
# # # --------------------------------------------------
# # # 10. LOGOUT
# # # --------------------------------------------------
# # @app.route("/auth/logout", methods=["POST"])
# # def logout():
# #     session.clear()
# #     return jsonify({"message": "Logged out successfully."}), 200
# # # --------------------------------------------------
# # # 11. MACHINE-LEARNING PREDICTION
# # # --------------------------------------------------
# # # def get_best_prediction(vectorized_review):
# #     """Return the soft-voting ML prediction and fake probability."""
# #     models = [lr_model, nb_model]
# #     if rf_model is not None:
# #         models.append(rf_model)
# #     fake_probabilities = []
# #     for model in models:
# #         probabilities = model.predict_proba(vectorized_review)[0]
# #         fake_index = list(model.classes_).index(1)
# #         fake_probabilities.append(float(probabilities[fake_index]))
# #     avg_fake_probability = float(sum(fake_probabilities) / len(fake_probabilities))
# #     prediction = "Fake" if avg_fake_probability >= 0.5 else "Genuine"
# #     confidence = avg_fake_probability if prediction == "Fake" else 1.0 - avg_fake_probability
# #     return {
# #         "prediction": prediction,
# #         "confidence": round(float(confidence), 2),
# #         "fake_probability": avg_fake_probability,
# #     }
# # # 12. LSTM PREDICTION
# # # --------------------------------------------------
# # def get_lstm_prediction(review):
# #     cleaned_review = clean_lstm_text(review)
# #     sequence = lstm_tokenizer.texts_to_sequences([cleaned_review])
# #     padded = pad_sequences(
# #         sequence,
# #         maxlen=MAX_LENGTH,
# #         padding="post",
# #         truncating="post",
# #     )
# #     probability = float(
# #         np.asarray(lstm_model.predict(padded, verbose=0)).reshape(-1)[0]
# #     )
# #     # The training script requires label 1 = Fake and label 0 = Genuine.
# #     predicted_class = 1 if probability >= 0.5 else 0
# #     confidence = probability if predicted_class == 1 else 1.0 - probability
# #     return {
# #         "prediction": "Fake" if predicted_class == 1 else "Genuine",
# #         "confidence": round(confidence, 2),
# #         "fake_probability": probability,
# #     }
# # # --------------------------------------------------
# # def get_combined_prediction(review):
# #     """Combine ML and LSTM fake probabilities for uploaded-file predictions."""
# #     cleaned_ml_review = clean_ml_text(review)
# #     vectorized_review = vectorizer.transform([cleaned_ml_review])
# #     ml_result = get_best_prediction(vectorized_review)
# #     lstm_result = get_lstm_prediction(review)
# #     combined_fake_probability = (
# #         0.5 * ml_result["fake_probability"]
# #         + 0.5 * lstm_result["fake_probability"]
# #     )
# #     prediction = "Fake" if combined_fake_probability >= 0.5 else "Genuine"
# #     confidence = (
# #         combined_fake_probability
# #         if prediction == "Fake"
# #         else 1.0 - combined_fake_probability
# #     )
# #     return {
# #         "prediction": prediction,
# #         "confidence": round(float(confidence), 4),
# #     }
# # # 13. ANALYZE ONE REVIEW
# # # --------------------------------------------------
# # @app.route("/analyze", methods=["POST"])
# # @login_required
# # def analyze():
# #     data = request.get_json(silent=True) or {}
# #     review = data.get("review")
# #     if not review or not str(review).strip():
# #         return jsonify({"error": "Please enter a review."}), 400
# #     try:
# #         cleaned_review = clean_ml_text(review)
# #         vectorized_review = vectorizer.transform([cleaned_review])
# #         ml_result = get_best_prediction(vectorized_review)
# #         lstm_result = get_lstm_prediction(review)
# #         conn = get_db_connection()
# #         try:
# #             conn.execute(
# #                 """INSERT INTO review_history
# #                    (user_id, review, ml_prediction, ml_confidence,
# #                     lstm_prediction, lstm_confidence, created_at)
# #                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
# #                 (
# #                     session["user_id"],
# #                     str(review),
# #                     ml_result["prediction"],
# #                     ml_result["confidence"],
# #                     lstm_result["prediction"],
# #                     lstm_result["confidence"],
# #                     datetime.now().astimezone().isoformat(timespec="seconds"),
# #                 ),
# #             )
# #             conn.commit()
# #         finally:
# #             conn.close()
# #         return jsonify({
# #             "ml_prediction": ml_result,
# #             "lstm_prediction": lstm_result,
# #         }), 200
# #     except Exception as error:
# #         app.logger.exception("Review analysis failed")
# #         return jsonify({
# #             "error": "Review analysis failed.",
# #             "details": str(error),
# #         }), 500
# # # --------------------------------------------------
# # # 14. GET REVIEW HISTORY
# # # --------------------------------------------------
# # @app.route("/history", methods=["GET"])
# # @login_required
# # def get_review_history():
# #     conn = get_db_connection()
# #     try:
# #         rows = conn.execute(
# #             """SELECT id, review, ml_prediction, ml_confidence,
# #                       lstm_prediction, lstm_confidence, created_at
# #                FROM review_history
# #                WHERE user_id = ?
# #                ORDER BY id DESC""",
# #             (session["user_id"],),
# #         ).fetchall()
# #         return jsonify([dict(row) for row in rows]), 200
# #     except sqlite3.Error as error:
# #         return jsonify({
# #             "error": "Unable to retrieve review history.",
# #             "details": str(error),
# #         }), 500
# #     finally:
# #         conn.close()
# # # --------------------------------------------------
# # # 15. DELETE ONE REVIEW FROM HISTORY
# # # --------------------------------------------------
# # @app.route("/history/<int:review_id>", methods=["DELETE"])
# # @login_required
# # def delete_review_history(review_id):
# #     conn = get_db_connection()
# #     try:
# #         cursor = conn.execute(
# #             "DELETE FROM review_history WHERE id = ? AND user_id = ?",
# #             (review_id, session["user_id"]),
# #         )
# #         conn.commit()
# #         if cursor.rowcount == 0:
# #             return jsonify({"error": "Review not found."}), 404
# #         return jsonify({"message": "Review deleted successfully."}), 200
# #     except sqlite3.Error as error:
# #         conn.rollback()
# #         return jsonify({
# #             "error": "Unable to delete review.",
# #             "details": str(error),
# #         }), 500
# #     finally:
# #         conn.close()
# # # --------------------------------------------------
# # # 16. CSV OR JSON REVIEW FILE UPLOAD
# # # --------------------------------------------------
# # @app.route("/upload", methods=["POST"])
# # @login_required
# # def upload():
# #     uploaded_file = request.files.get("file")
# #     if not uploaded_file or not uploaded_file.filename:
# #         return jsonify({"error": "No file uploaded."}), 400
# #     filename = uploaded_file.filename.lower()
# #     if filename.endswith(".csv"):
# #         try:
# #             dataframe = pd.read_csv(uploaded_file)
# #         except Exception as error:
# #             return jsonify({"error": f"Unable to read CSV file: {error}"}), 400
# #     elif filename.endswith(".json"):
# #         try:
# #             dataframe = pd.read_json(uploaded_file)
# #         except Exception as error:
# #             return jsonify({"error": f"Unable to read JSON file: {error}"}), 400
# #     else:
# #         return jsonify({"error": "Only CSV or JSON files are allowed."}), 400
# #     if "review" not in dataframe.columns:
# #         return jsonify({"error": "File must contain a 'review' column."}), 400
# #     results = []
# #     try:
# #         for review in dataframe["review"]:
# #             if pd.isna(review) or not str(review).strip():
# #                 results.append({
# #                     "review": "" if pd.isna(review) else str(review),
# #                     "prediction": "Invalid",
# #                     "confidence": 0,
# #                 })
# #                 continue
# #             prediction = get_combined_prediction(str(review))
# #             results.append({
# #                 "review": str(review),
# #                 "prediction": prediction["prediction"],
# #                 "confidence": prediction["confidence"],
# #             })
# #         return jsonify(results), 200
# #     except Exception as error:
# #         app.logger.exception("File prediction failed")
# #         return jsonify({
# #             "error": "Unable to process uploaded file.",
# #             "details": str(error),
# #         }), 400
# # # --------------------------------------------------
# # # 17. HOME / HEALTH CHECK
# # # --------------------------------------------------
# # @app.route("/", methods=["GET"])
# # def home():
# #     return jsonify({
# #         "message": "Fake Review Detection Backend is running."
# #     }), 200
# # # --------------------------------------------------
# # # 18. RUN FLASK SERVER
# # # --------------------------------------------------
# # if __name__ == "__main__":
# #     app.run(
# #         host="127.0.0.1",
# #         port=5000,
# #         debug=True,
# #         use_reloader=False,
# #     )



# import os
# import re
# import string
# import pickle
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
# print("RUNNING APP FROM:", __file__)
# print("USING SOFT VOTING PREDICTION")
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
#             conn.execute("ALTER TABLE review_history ADD COLUMN user_id INTEGER")
#         conn.commit()
#     finally:
#         conn.close()
# init_db()
# # --------------------------------------------------
# # 2. LOAD TRAINED MACHINE-LEARNING MODELS
# # --------------------------------------------------
# def load_pickle(filename):
#     path = BASE_DIR / filename
#     if not path.is_file():
#         raise FileNotFoundError(
#             f"Required file is missing: {path}. Run train_model.py first."
#         )
#     with path.open("rb") as file:
#         return pickle.load(file)
# lr_model = load_pickle("lr_model.pkl")
# nb_model = load_pickle("nb_model.pkl")
# vectorizer = load_pickle("vectorizer.pkl")
# # Random Forest is optional. If its file is unavailable, LR and NB still run.
# try:
#     rf_model = load_pickle("rf_model.pkl")
#     print("Random Forest model loaded successfully.")
# except Exception as error:
#     print(f"Random Forest unavailable: {error}")
#     rf_model = None
# # --------------------------------------------------
# # 3. LOAD TRAINED LSTM MODEL AND TOKENIZER
# # --------------------------------------------------
# MODEL_PATH = BASE_DIR / "lstm_model.keras"
# TOKENIZER_PATH = BASE_DIR / "lstm_tokenizer.pkl"
# if not MODEL_PATH.is_file():
#     raise FileNotFoundError(
#         f"Required file is missing: {MODEL_PATH}. Run train_dl_model.py first."
#     )
# if not TOKENIZER_PATH.is_file():
#     raise FileNotFoundError(
#         f"Required file is missing: {TOKENIZER_PATH}. Run train_dl_model.py first."
#     )
# lstm_model = tf.keras.models.load_model(MODEL_PATH)
# with TOKENIZER_PATH.open("rb") as file:
#     lstm_tokenizer = pickle.load(file)
# MAX_LENGTH = 150
# # --------------------------------------------------
# # 4. FLASK APPLICATION AND CORS
# # --------------------------------------------------
# app = Flask(__name__)
# app.config.update(
#     SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-secret"),
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE="Lax",
#     SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
#     PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
# )
# CORS(
#     app,
#     supports_credentials=True,
#     origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#     ],
# )
# # --------------------------------------------------
# # 5. AUTHENTICATION HELPER
# # --------------------------------------------------
# def login_required(view):
#     @wraps(view)
#     def wrapped(*args, **kwargs):
#         if not session.get("user_id"):
#             return jsonify({"error": "Please log in to continue."}), 401
#         return view(*args, **kwargs)
#     return wrapped
# # --------------------------------------------------
# # 6. TEXT CLEANING
# # Keep these functions consistent with the two training scripts.
# # --------------------------------------------------
# def clean_ml_text(text):
#     """Cleaning used by train_model.py (TF-IDF models)."""
#     text = str(text).lower()
#     text = re.sub(r"\d+", "", text)
#     return text.translate(str.maketrans("", "", string.punctuation))
# def clean_lstm_text(text):
#     """Cleaning used by train_dl_model.py (LSTM model)."""
#     text = str(text).lower()
#     text = re.sub(r"http\S+|www\S+", " ", text)
#     text = re.sub(r"[^a-z\s]", " ", text)
#     return re.sub(r"\s+", " ", text).strip()
# def label_name(value):
#     """Project convention: 1 = Fake and 0 = Genuine."""
#     try:
#         return "Fake" if int(value) == 1 else "Genuine"
#     except (TypeError, ValueError):
#         normalized = str(value).strip().lower()
#         if normalized in {"fake", "deceptive", "false", "1"}:
#             return "Fake"
#         return "Genuine"
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
#         return jsonify({"error": "Name, email and password are required."}), 400
#     if len(name) > 80 or len(email) > 254 or "@" not in email:
#         return jsonify({"error": "Please enter a valid name and email address."}), 400
#     if len(password) < 8:
#         return jsonify({"error": "Password must contain at least 8 characters."}), 400
#     conn = get_db_connection()
#     try:
#         cursor = conn.execute(
#             """INSERT INTO users (name, email, password_hash, created_at)
#                VALUES (?, ?, ?, ?)""",
#             (
#                 name,
#                 email,
#                 generate_password_hash(password),
#                 datetime.now().astimezone().isoformat(timespec="seconds"),
#             ),
#         )
#         conn.commit()
#         user_id = cursor.lastrowid
#     except sqlite3.IntegrityError:
#         return jsonify({"error": "An account with this email already exists. Please log in."}), 409
#     finally:
#         conn.close()
#     session.clear()
#     session["user_id"] = user_id
#     session["user_name"] = name
#     session.permanent = True
#     return jsonify({
#         "message": "Account created successfully.",
#         "user": {"id": user_id, "name": name, "email": email},
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
#             "SELECT id, name, email, password_hash FROM users WHERE email = ?",
#             (email,),
#         ).fetchone()
#     finally:
#         conn.close()
#     if not user or not check_password_hash(user["password_hash"], password):
#         return jsonify({"error": "Incorrect email or password."}), 401
#     session.clear()
#     session["user_id"] = user["id"]
#     session["user_name"] = user["name"]
#     session.permanent = True
#     return jsonify({
#         "message": "Login successful.",
#         "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
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
#             "SELECT id, name, email FROM users WHERE id = ?",
#             (user_id,),
#         ).fetchone()
#     finally:
#         conn.close()
#     if not user:
#         session.clear()
#         return jsonify({"user": None}), 200
#     return jsonify({"user": dict(user)}), 200
# # --------------------------------------------------
# # 10. LOGOUT
# # --------------------------------------------------
# @app.route("/auth/logout", methods=["POST"])
# def logout():
#     session.clear()
#     return jsonify({"message": "Logged out successfully."}), 200
# # --------------------------------------------------
# # 11. MACHINE-LEARNING PREDICTION
# # --------------------------------------------------
# def get_best_prediction(vectorized_review):
#     """Return the soft-voting ML prediction and fake probability."""
#     models = [lr_model, nb_model]
#     if rf_model is not None:
#         models.append(rf_model)
#     fake_probabilities = []
#     for model in models:
#         probabilities = model.predict_proba(vectorized_review)[0]
#         fake_index = list(model.classes_).index(1)
#         fake_probabilities.append(float(probabilities[fake_index]))
#     avg_fake_probability = float(sum(fake_probabilities) / len(fake_probabilities))
#     prediction = "Fake" if avg_fake_probability >= 0.5 else "Genuine"
#     confidence = avg_fake_probability if prediction == "Fake" else 1.0 - avg_fake_probability
#     return {
#         "prediction": prediction,
#         "confidence": round(float(confidence), 2),
#         "fake_probability": avg_fake_probability,
#     }
# # 12. LSTM PREDICTION
# # --------------------------------------------------
# def get_lstm_prediction(review):
#     cleaned_review = clean_lstm_text(review)
#     sequence = lstm_tokenizer.texts_to_sequences([cleaned_review])
#     padded = pad_sequences(
#         sequence,
#         maxlen=MAX_LENGTH,
#         padding="post",
#         truncating="post",
#     )
#     probability = float(
#         np.asarray(lstm_model.predict(padded, verbose=0)).reshape(-1)[0]
#     )
#     # The training script requires label 1 = Fake and label 0 = Genuine.
#     predicted_class = 1 if probability >= 0.5 else 0
#     confidence = probability if predicted_class == 1 else 1.0 - probability
#     return {
#         "prediction": "Fake" if predicted_class == 1 else "Genuine",
#         "confidence": round(confidence, 2),
#         "fake_probability": probability,
#     }
# # --------------------------------------------------
# def get_combined_prediction(review):
#     """Combine ML and LSTM fake probabilities for uploaded-file predictions."""
#     cleaned_ml_review = clean_ml_text(review)
#     vectorized_review = vectorizer.transform([cleaned_ml_review])
#     ml_result = get_best_prediction(vectorized_review)
#     lstm_result = get_lstm_prediction(review)
#     combined_fake_probability = (
#         0.5 * ml_result["fake_probability"]
#         + 0.5 * lstm_result["fake_probability"]
#     )
#     prediction = "Fake" if combined_fake_probability >= 0.5 else "Genuine"
#     confidence = (
#         combined_fake_probability
#         if prediction == "Fake"
#         else 1.0 - combined_fake_probability
#     )
#     return {
#         "prediction": prediction,
#         "confidence": round(float(confidence), 4),
#     }
# # 13. ANALYZE ONE REVIEW
# # --------------------------------------------------
# @app.route("/analyze", methods=["POST"])
# @login_required
# def analyze():
#     data = request.get_json(silent=True) or {}
#     review = data.get("review")
#     if not review or not str(review).strip():
#         return jsonify({"error": "Please enter a review."}), 400
#     try:
#         cleaned_review = clean_ml_text(review)
#         vectorized_review = vectorizer.transform([cleaned_review])
#         ml_result = get_best_prediction(vectorized_review)
#         lstm_result = get_lstm_prediction(review)
#         conn = get_db_connection()
#         try:
#             conn.execute(
#                 """INSERT INTO review_history
#                    (user_id, review, ml_prediction, ml_confidence,
#                     lstm_prediction, lstm_confidence, created_at)
#                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
#                 (
#                     session["user_id"],
#                     str(review),
#                     ml_result["prediction"],
#                     ml_result["confidence"],
#                     lstm_result["prediction"],
#                     lstm_result["confidence"],
#                     datetime.now().astimezone().isoformat(timespec="seconds"),
#                 ),
#             )
#             conn.commit()
#         finally:
#             conn.close()
#         return jsonify({
#             "ml_prediction": ml_result,
#             "lstm_prediction": lstm_result,
#         }), 200
#     except Exception as error:
#         app.logger.exception("Review analysis failed")
#         return jsonify({
#             "error": "Review analysis failed.",
#             "details": str(error),
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
#             """SELECT id, review, ml_prediction, ml_confidence,
#                       lstm_prediction, lstm_confidence, created_at
#                FROM review_history
#                WHERE user_id = ?
#                ORDER BY id DESC""",
#             (session["user_id"],),
#         ).fetchall()
#         return jsonify([dict(row) for row in rows]), 200
#     except sqlite3.Error as error:
#         return jsonify({
#             "error": "Unable to retrieve review history.",
#             "details": str(error),
#         }), 500
#     finally:
#         conn.close()
# # --------------------------------------------------
# # 15. DELETE ONE REVIEW FROM HISTORY
# # --------------------------------------------------
# @app.route("/history/<int:review_id>", methods=["DELETE"])
# @login_required
# def delete_review_history(review_id):
#     conn = get_db_connection()
#     try:
#         cursor = conn.execute(
#             "DELETE FROM review_history WHERE id = ? AND user_id = ?",
#             (review_id, session["user_id"]),
#         )
#         conn.commit()
#         if cursor.rowcount == 0:
#             return jsonify({"error": "Review not found."}), 404
#         return jsonify({"message": "Review deleted successfully."}), 200
#     except sqlite3.Error as error:
#         conn.rollback()
#         return jsonify({
#             "error": "Unable to delete review.",
#             "details": str(error),
#         }), 500
#     finally:
#         conn.close()
# # --------------------------------------------------
# # 16. CSV OR JSON REVIEW FILE UPLOAD
# # --------------------------------------------------
# @app.route("/upload", methods=["POST"])
# @login_required
# def upload():
#     uploaded_file = request.files.get("file")
#     if not uploaded_file or not uploaded_file.filename:
#         return jsonify({"error": "No file uploaded."}), 400
#     filename = uploaded_file.filename.lower()
#     if filename.endswith(".csv"):
#         try:
#             dataframe = pd.read_csv(uploaded_file)
#         except Exception as error:
#             return jsonify({"error": f"Unable to read CSV file: {error}"}), 400
#     elif filename.endswith(".json"):
#         try:
#             dataframe = pd.read_json(uploaded_file)
#         except Exception as error:
#             return jsonify({"error": f"Unable to read JSON file: {error}"}), 400
#     else:
#         return jsonify({"error": "Only CSV or JSON files are allowed."}), 400
#     if "review" not in dataframe.columns:
#         return jsonify({"error": "File must contain a 'review' column."}), 400
#     results = []
#     try:
#         for review in dataframe["review"]:
#             if pd.isna(review) or not str(review).strip():
#                 results.append({
#                     "review": "" if pd.isna(review) else str(review),
#                     "prediction": "Invalid",
#                     "confidence": 0,
#                 })
#                 continue
#             prediction = get_combined_prediction(str(review))
#             results.append({
#                 "review": str(review),
#                 "prediction": prediction["prediction"],
#                 "confidence": prediction["confidence"],
#             })
#         return jsonify(results), 200
#     except Exception as error:
#         app.logger.exception("File prediction failed")
#         return jsonify({
#             "error": "Unable to process uploaded file.",
#             "details": str(error),
#         }), 400
# # --------------------------------------------------
# # 17. HOME / HEALTH CHECK
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
#         use_reloader=False,
#     )



import os
import re
import string
import pickle
import sqlite3
import json
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

print("RUNNING APP FROM:", __file__)
print("USING SOFT VOTING FOR ML + LSTM FILE PREDICTIONS")

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
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(review_history)"
            ).fetchall()
        }

        if "user_id" not in columns:
            conn.execute(
                "ALTER TABLE review_history ADD COLUMN user_id INTEGER"
            )

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
            f"Required file is missing: {path}. "
            "Run train_model.py first."
        )

    with path.open("rb") as file:
        return pickle.load(file)


lr_model = load_pickle("lr_model.pkl")
nb_model = load_pickle("nb_model.pkl")
vectorizer = load_pickle("vectorizer.pkl")

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
        f"Required file is missing: {MODEL_PATH}. "
        "Run train_dl_model.py first."
    )

if not TOKENIZER_PATH.is_file():
    raise FileNotFoundError(
        f"Required file is missing: {TOKENIZER_PATH}. "
        "Run train_dl_model.py first."
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
    SECRET_KEY=os.environ.get(
        "SECRET_KEY",
        "development-only-change-this-secret"
    ),
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
            return jsonify({
                "error": "Please log in to continue."
            }), 401

        return view(*args, **kwargs)

    return wrapped


# --------------------------------------------------
# 6. TEXT CLEANING
# These must match the corresponding training scripts.
# --------------------------------------------------

def clean_ml_text(text):
    """Cleaning used by the TF-IDF machine-learning pipeline."""
    text = str(text).lower()
    text = re.sub(r"\d+", "", text)
    return text.translate(
        str.maketrans("", "", string.punctuation)
    )


def clean_lstm_text(text):
    """Cleaning used by the LSTM training pipeline."""
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
        return jsonify({
            "error": "Name, email and password are required."
        }), 400

    if len(name) > 80 or len(email) > 254 or "@" not in email:
        return jsonify({
            "error": "Please enter a valid name and email address."
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must contain at least 8 characters."
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
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
        return jsonify({
            "error": (
                "An account with this email already exists. "
                "Please log in."
            )
        }), 409

    finally:
        conn.close()

    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name
    session.permanent = True

    return jsonify({
        "message": "Account created successfully.",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
        },
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
            """
            SELECT id, name, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(
        user["password_hash"], password
    ):
        return jsonify({
            "error": "Incorrect email or password."
        }), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session.permanent = True

    return jsonify({
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
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
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
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

    return jsonify({
        "message": "Logged out successfully."
    }), 200


# --------------------------------------------------
# 11. MACHINE-LEARNING PREDICTION
# --------------------------------------------------

def get_best_prediction(vectorized_review):
    """
    Average the fake probabilities from the available ML models.
    Returns one ML prediction and its confidence.
    """

    models = [lr_model, nb_model]

    if rf_model is not None:
        models.append(rf_model)

    fake_probabilities = []

    for model in models:
        probabilities = model.predict_proba(
            vectorized_review
        )[0]

        classes = list(model.classes_)

        if 1 not in classes:
            raise ValueError(
                "The ML model does not contain class 1 (Fake). "
                "Check the labels used during training."
            )

        fake_index = classes.index(1)
        fake_probabilities.append(
            float(probabilities[fake_index])
        )

    avg_fake_probability = float(
        np.mean(fake_probabilities)
    )

    prediction = (
        "Fake"
        if avg_fake_probability >= 0.5
        else "Genuine"
    )

    confidence = (
        avg_fake_probability
        if prediction == "Fake"
        else 1.0 - avg_fake_probability
    )

    return {
        "prediction": prediction,
        "confidence": round(float(confidence), 4),
        "fake_probability": avg_fake_probability,
    }


# --------------------------------------------------
# 12. LSTM PREDICTION
# --------------------------------------------------

def get_lstm_prediction(review):
    cleaned_review = clean_lstm_text(review)

    sequence = lstm_tokenizer.texts_to_sequences(
        [cleaned_review]
    )

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post",
    )

    probability = float(
        np.asarray(
            lstm_model.predict(padded, verbose=0)
        ).reshape(-1)[0]
    )

    # Training convention: 1 = Fake, 0 = Genuine.
    predicted_class = 1 if probability >= 0.5 else 0

    confidence = (
        probability
        if predicted_class == 1
        else 1.0 - probability
    )

    return {
        "prediction": (
            "Fake" if predicted_class == 1 else "Genuine"
        ),
        "confidence": round(float(confidence), 4),
        "fake_probability": probability,
    }


# --------------------------------------------------
# 13. COMBINED PREDICTION FOR FILE UPLOADS ONLY
# --------------------------------------------------

def get_combined_prediction(review):
    """
    Combine ML and LSTM fake probabilities with equal weights.

    P(Fake) = 0.5 * ML fake probability
              + 0.5 * LSTM fake probability
    """

    cleaned_ml_review = clean_ml_text(review)
    vectorized_review = vectorizer.transform(
        [cleaned_ml_review]
    )

    ml_result = get_best_prediction(vectorized_review)
    lstm_result = get_lstm_prediction(review)

    combined_fake_probability = (
        0.5 * ml_result["fake_probability"]
        + 0.5 * lstm_result["fake_probability"]
    )

    prediction = (
        "Fake"
        if combined_fake_probability >= 0.5
        else "Genuine"
    )

    confidence = (
        combined_fake_probability
        if prediction == "Fake"
        else 1.0 - combined_fake_probability
    )

    return {
        "prediction": prediction,
        "confidence": round(float(confidence), 4),
    }


# --------------------------------------------------
# 14. ANALYZE ONE REVIEW
# Individual review: return ML and LSTM separately.
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    data = request.get_json(silent=True) or {}
    review = data.get("review")

    if review is None or not str(review).strip():
        return jsonify({
            "error": "Please enter a review."
        }), 400

    try:
        review = str(review)

        cleaned_review = clean_ml_text(review)
        vectorized_review = vectorizer.transform(
            [cleaned_review]
        )

        ml_result = get_best_prediction(vectorized_review)
        lstm_result = get_lstm_prediction(review)

        conn = get_db_connection()

        try:
            conn.execute(
                """
                INSERT INTO review_history
                (
                    user_id,
                    review,
                    ml_prediction,
                    ml_confidence,
                    lstm_prediction,
                    lstm_confidence,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    review,
                    ml_result["prediction"],
                    ml_result["confidence"],
                    lstm_result["prediction"],
                    lstm_result["confidence"],
                    datetime.now().astimezone().isoformat(
                        timespec="seconds"
                    ),
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
# 15. GET REVIEW HISTORY
# --------------------------------------------------

@app.route("/history", methods=["GET"])
@login_required
def get_review_history():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                review,
                ml_prediction,
                ml_confidence,
                lstm_prediction,
                lstm_confidence,
                created_at
            FROM review_history
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],),
        ).fetchall()

        return jsonify([
            dict(row) for row in rows
        ]), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": "Unable to retrieve review history.",
            "details": str(error),
        }), 500

    finally:
        conn.close()


# --------------------------------------------------
# 16. DELETE ONE REVIEW FROM HISTORY
# --------------------------------------------------

@app.route("/history/<int:review_id>", methods=["DELETE"])
@login_required
def delete_review_history(review_id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            DELETE FROM review_history
            WHERE id = ? AND user_id = ?
            """,
            (review_id, session["user_id"]),
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Review not found."
            }), 404

        return jsonify({
            "message": "Review deleted successfully."
        }), 200

    except sqlite3.Error as error:
        conn.rollback()

        return jsonify({
            "error": "Unable to delete review.",
            "details": str(error),
        }), 500

    finally:
        conn.close()


# --------------------------------------------------
# 17. READ CSV OR JSON FILE
# Supports:
# - CSV with a review column
# - JSON array of objects
# - JSON object containing a list of records
# - JSON Lines (one JSON object per line)
# --------------------------------------------------

def read_uploaded_dataframe(uploaded_file, filename):
    if filename.endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(
                uploaded_file,
                encoding="latin-1"
            )

    if filename.endswith(".json"):
        raw_content = uploaded_file.read()

        if not raw_content:
            raise ValueError("The uploaded JSON file is empty.")

        try:
            decoded_content = raw_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            decoded_content = raw_content.decode("latin-1")

        # First try standard JSON: array or object.
        try:
            json_data = json.loads(decoded_content)

            if isinstance(json_data, list):
                return pd.DataFrame(json_data)

            if isinstance(json_data, dict):
                # Accept {"data": [...]} or {"reviews": [...]}.
                for key in ("data", "reviews", "records"):
                    if (
                        key in json_data
                        and isinstance(json_data[key], list)
                    ):
                        return pd.DataFrame(json_data[key])

                # A single record such as {"review": "..."}.
                return pd.DataFrame([json_data])

            raise ValueError(
                "JSON must contain an array of review objects "
                "or a review object."
            )

        except json.JSONDecodeError:
            # If standard JSON parsing fails, try JSON Lines.
            try:
                return pd.read_json(
                    decoded_content,
                    lines=True
                )
            except ValueError as error:
                raise ValueError(
                    "Unable to read JSON. Use a JSON array, "
                    "a JSON object, or JSON Lines format."
                ) from error

    raise ValueError(
        "Only CSV or JSON files are allowed."
    )


# --------------------------------------------------
# 18. CSV OR JSON REVIEW FILE UPLOAD
# Each valid review receives one combined ML + LSTM result.
# --------------------------------------------------

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    uploaded_file = request.files.get("file")

    if not uploaded_file or not uploaded_file.filename:
        return jsonify({
            "error": "No file uploaded."
        }), 400

    filename = uploaded_file.filename.lower()

    if not (
        filename.endswith(".csv")
        or filename.endswith(".json")
    ):
        return jsonify({
            "error": "Only CSV or JSON files are allowed."
        }), 400

    try:
        dataframe = read_uploaded_dataframe(
            uploaded_file,
            filename
        )

        if dataframe.empty:
            return jsonify({
                "error": "The uploaded file contains no review records."
            }), 400

        if "review" not in dataframe.columns:
            return jsonify({
                "error": "File must contain a 'review' column."
            }), 400

        results = []

        for review in dataframe["review"].tolist():
            if review is None or pd.isna(review) or not str(review).strip():
                results.append({
                    "review": (
                        "" if review is None or pd.isna(review)
                        else str(review)
                    ),
                    "prediction": "Invalid",
                    "confidence": 0,
                })
                continue

            review_text = str(review).strip()
            combined_result = get_combined_prediction(
                review_text
            )

            results.append({
                "review": review_text,
                "prediction": combined_result["prediction"],
                "confidence": combined_result["confidence"],
            })

        return jsonify(results), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        app.logger.exception("File prediction failed")

        return jsonify({
            "error": "Unable to process uploaded file.",
            "details": str(error),
        }), 500


# --------------------------------------------------
# 19. HOME / HEALTH CHECK
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Fake Review Detection Backend is running."
    }), 200


# --------------------------------------------------
# 20. RUN FLASK SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False,
    )
