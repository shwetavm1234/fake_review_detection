# Fake Review Detection System

## 📌 Project Overview

The **Fake Review Detection System** is a web application designed to identify potentially fake product reviews using Machine Learning and Deep Learning techniques.

The application allows users to submit a review and analyze its authenticity using two approaches:

- **Machine Learning:** Uses a trained classification model to predict whether a review is fake or genuine.
- **Deep Learning (LSTM):** Uses a Long Short-Term Memory neural network to analyze review text and generate a prediction.

The application provides a user-friendly interface built with React and a Flask backend that processes requests, runs predictions, and stores review history.

## 🎯 Objectives

- Identify potentially fake and genuine product reviews.
- Compare predictions from Machine Learning and Deep Learning models.
- Provide a simple web interface for submitting reviews.
- Display prediction results and confidence scores when available.
- Maintain a history of previously analyzed reviews.
- Allow users to delete individual records from review history.

## ✨ Features

- Review text analysis.
- Machine Learning-based fake review prediction.
- LSTM-based Deep Learning prediction.
- Prediction confidence display.
- Review history management.
- Delete individual saved reviews.
- React-based frontend.
- Flask REST API backend.
- SQLite database for storing review history.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Backend API |
| Flask-CORS | Communication between frontend and backend |
| Pandas | Data processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine Learning model support |
| TensorFlow / Keras | LSTM Deep Learning model |
| React.js | Frontend development |
| Vite | Frontend development server |
| Tailwind CSS | User interface styling, if configured |
| SQLite | Review history storage |
| Git and GitHub | Version control and collaboration |
| Git LFS | Storage of large model files |

## 🧠 Models Used

### 1. Machine Learning Model

A trained Machine Learning classifier analyzes review text and predicts whether it is fake or genuine.

The backend uses the trained model and its corresponding text vectorizer to process review input.

### 2. Deep Learning Model (LSTM)

The LSTM model processes text sequences and generates a prediction based on patterns learned during training.

A tokenizer is used to convert text into sequences suitable for the neural network.

**Note:** The exact model architecture, training dataset, and evaluation metrics should be documented according to the implementation in this repository.

## 🏗️ Project Structure

```text
Fake-Review-Detection/
├── backend/
│   ├── app.py
│   ├── model.py
│   ├── train_model.py
│   ├── train_dl_model.py
│   ├── lr_model.pkl
│   ├── nb_model.pkl
│   ├── rf_model.pkl
│   ├── vectorizer.pkl
│   ├── lstm_model.keras
│   ├── lstm_tokenizer.pkl
│   ├── fake_reviews.csv
│   └── fake_reviews.json
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

*This is a representative structure. Some filenames or folders may differ in your repository.*

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the project:

- Python
- Node.js and npm
- Git
- Git LFS

### 1. Clone the Repository

```bash
git clone https://github.com/shrutigiri558-code/Fake-Review-Detection.git
cd Fake-Review-Detection
```

### 2. Set Up the Backend

Open a terminal in the project root and run:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required Python packages:

```bash
python -m pip install flask flask-cors pandas numpy tensorflow scikit-learn
```

If a `requirements.txt` file is available, install the project's pinned dependencies instead:

```bash
python -m pip install -r requirements.txt
```

Start the Flask backend:

```bash
python app.py
```

The backend is expected to run at:

```text
http://127.0.0.1:5000
```

### 3. Set Up the Frontend

Open a second terminal and run:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal, commonly:

```text
http://localhost:5173
```

Keep both the Flask backend and React frontend running while using the application.

## 🔄 Application Workflow

1. The user enters or submits a product review through the React interface.
2. The frontend sends the review to the Flask backend.
3. The backend preprocesses the text as required by the trained models.
4. The Machine Learning model generates a prediction.
5. The LSTM model generates a prediction.
6. The frontend displays the available predictions and confidence scores.
7. The analysis result is saved in the SQLite review-history database.
8. The user can view past results and delete individual history records.

## 🗃️ Review History

The application stores review-history records in the SQLite `review_history` table.

Each record may contain:

- Review ID
- Review text
- Machine Learning prediction
- Machine Learning confidence
- LSTM prediction
- LSTM confidence
- Creation timestamp

The application provides a history endpoint and supports deleting a selected history record.

## 🔌 Backend API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/history` | Retrieve saved review history |
| DELETE | `/history/<review_id>` | Delete a selected history record |

The prediction endpoints should be documented here according to the actual routes defined in `backend/app.py`.

## 📊 Evaluation

Model performance should be evaluated using appropriate metrics, such as:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

Actual evaluation results should be added after testing the models on a suitable held-out dataset.

## 🔐 Notes

- Do not commit passwords, API keys, or private configuration files.
- Do not upload private or sensitive review data.
- Git LFS is used for large model files that exceed GitHub's regular file-size limit.
- Ensure all required model files and tokenizer/vectorizer files are available before running predictions.
- A prediction is an automated estimate and should not be treated as definitive proof that a review is fake.

## 🚀 Future Enhancements

- Improve model performance using larger and more diverse datasets.
- Add model evaluation reports and visualizations.
- Improve review-history search and filtering.
- Add user authentication and access control.
- Deploy the application to a cloud platform.
- Add automated testing and continuous integration.

## 👥 Team Project

This project demonstrates the integration of Machine Learning, Deep Learning, Flask APIs, React frontend development, database operations, and GitHub collaboration.

## 📄 License

Add an appropriate license before distributing the project publicly. If no license has been selected, the project is shared without an explicit open-source license.


## 🔐 Login and Registration (added)

The application now supports account registration and login. Accounts are stored in the SQLite database at `backend/reviews.db`; passwords are stored as secure hashes. Login is maintained with a Flask session cookie. Review analysis, upload, and review-history API routes require a logged-in session, and review history is associated with the signed-in account.

### Backend setup

From the project root, open a terminal and run:

```bash
cd backend
python -m pip install flask flask-cors werkzeug pandas numpy scikit-learn tensorflow
```

Set a strong Flask session secret before starting the backend. On Windows PowerShell:

```powershell
$env:SECRET_KEY = "replace-this-with-a-long-random-secret"
python app.py
```

On macOS/Linux:

```bash
export SECRET_KEY="replace-this-with-a-long-random-secret"
python app.py
```

For local development, the session cookie is configured for HTTP. For deployment, use HTTPS, set `COOKIE_SECURE=1`, and update the allowed frontend origins in `backend/app.py` to your deployed frontend domain. Do not use the development fallback secret in production.

### Frontend setup

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. New users should select **Create account**. After registration or login, the app opens the existing Fake Review Detection home page. Use **Logout** in the navigation bar to end the session.

### First-time test

1. Open `http://127.0.0.1:5173`.
2. Select **Create account**.
3. Enter your name, email address, and a password with at least 8 characters.
4. Submit the form; you should be redirected to the project home page.
5. Log out, then sign in using the same email and password.
6. Try opening `/detect` in a private/incognito window without logging in; it should redirect to `/login`.

The first account is created by the registration page. There is no hard-coded default username or password.
