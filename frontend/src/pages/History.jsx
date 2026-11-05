
import React, { useEffect, useState } from "react";
import { API_URL } from "../context/AuthContext";

export default function History() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_URL}/history`, { credentials: "include" });

        if (!response.ok) {
          throw new Error("Unable to load review history.");
        }

        const data = await response.json();
        setReviews(data);
      } catch (err) {
        setError(err.message || "Could not connect to Flask.");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);


const handleDelete = async (id) => {
  const confirmed = window.confirm(
    "Are you sure you want to delete this review?"
  );

  if (!confirmed) return;

  setDeletingId(id);
  setError("");

  try {
    const response = await fetch(`${API_URL}/history/${id}`, {
      method: "DELETE",
      credentials: "include",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to delete review.");
    }

    setReviews((previousReviews) =>
      previousReviews.filter((item) => item.id !== id)
    );
  } catch (err) {
    setError(err.message || "Could not delete review.");
  } finally {
    setDeletingId(null);
  }
};


  const formatConfidence = (value) => {
    if (value === null || value === undefined || value === "") {
      return "N/A";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "N/A";
    }

    // Your backend may return confidence as 0–1 or 0–100.
    const percentage =
      number >= 0 && number <= 1 ? number * 100 : number;

    return `${percentage.toFixed(2)}%`;
  };

  return (
    <main className="max-w-5xl mx-auto px-6 py-10 text-white">
      <h1 className="text-3xl font-bold mb-2">Review History</h1>

      <p className="text-gray-400 mb-8">
        Previously analyzed reviews and their model predictions.
      </p>

      {loading && <p>Loading review history...</p>}

      {error && (
        <p className="text-red-400" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && reviews.length === 0 && (
        <div className="border border-gray-700 rounded-xl p-6">
          No review history yet. Analyze a review to save your first result.
        </div>
      )}

      {!loading && !error && reviews.length > 0 && (
        <div className="space-y-5">
          {reviews.map((item) => (
            <article
              key={item.id}
              className="bg-black/40 border border-gray-700 rounded-xl p-5"
            >
              
<div className="flex flex-wrap justify-between items-center gap-3 mb-4">
  <h2 className="font-semibold">
    Review #{item.id}
  </h2>

  <div className="flex flex-wrap items-center gap-3">
    <time className="text-sm text-gray-400">
      {item.created_at
        ? new Date(item.created_at).toLocaleString()
        : "Date unavailable"}
    </time>

    <button
      type="button"
      onClick={() => handleDelete(item.id)}
      disabled={deletingId === item.id}
      className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white text-sm font-semibold"
    >
      {deletingId === item.id ? "Deleting..." : "Delete"}
    </button>
  </div>
</div>


              <p className="text-gray-300 whitespace-pre-wrap mb-5">
                {item.review}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">
                    Machine Learning
                  </h3>

                  <p>
                    Prediction:{" "}
                    <span className="font-bold">
                      {item.ml_prediction || "N/A"}
                    </span>
                  </p>

                  <p className="text-gray-400 mt-1">
                    Confidence: {formatConfidence(item.ml_confidence)}
                  </p>
                </div>

                <div className="border border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">
                    Deep Learning (LSTM)
                  </h3>

                  <p>
                    Prediction:{" "}
                    <span className="font-bold">
                      {item.lstm_prediction || "N/A"}
                    </span>
                  </p>

                  <p className="text-gray-400 mt-1">
                    Confidence: {formatConfidence(item.lstm_confidence)}
                  </p>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
