
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

const Result = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { result, reviewText } = location.state || {};

  // Handle missing result data
  if (!result) {
    return (
      <div className="text-center mt-10 text-white">
        <p>No result found. Please analyze a review first.</p>
        <button
          onClick={() => navigate("/detect")}
          className="mt-4 px-4 py-2 bg-violet-600 rounded hover:bg-violet-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  // Support predictions returned as either objects or strings
  const getPrediction = (value) => {
    if (value == null) return "No prediction available";

    if (typeof value === "string" || typeof value === "number") {
      return String(value);
    }

    return (
      value.prediction ??
      value.label ??
      value.result ??
      "No prediction available"
    );
  };

  const getConfidence = (value) => {
    if (value == null || typeof value !== "object") {
      return null;
    }

    const confidence = value.confidence;

    if (typeof confidence !== "number" || !Number.isFinite(confidence)) {
      return null;
    }

    // Accept confidence represented as either 0–1 or 0–100
    const percentage =
      confidence >= 0 && confidence <= 1
        ? confidence * 100
        : confidence;

    return `${percentage.toFixed(2)}%`;
  };

  const PredictionCard = ({ title, value }) => {
    const prediction = getPrediction(value);
    const isFake = prediction.toLowerCase().includes("fake");
    const confidence = getConfidence(value);

    return (
      <div className="mb-6 p-6 bg-black/40 border border-gray-700 rounded-xl">
        <h2 className="text-xl font-semibold mb-4">{title}</h2>

        <p
          className={`text-2xl font-bold ${
            isFake ? "text-red-500" : "text-green-500"
          }`}
        >
          {prediction}
        </p>

        {confidence !== null && (
          <p className="text-gray-400 mt-3">
            Confidence: {confidence}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-12 text-white">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Analysis Result
      </h1>

      {/* Review text */}
      <div className="mb-6 p-6 bg-black/40 border border-gray-700 rounded-xl">
        <h2 className="text-xl font-semibold mb-3">Review</h2>

        <p className="text-gray-300 whitespace-pre-wrap">
          {reviewText || "Review text not available"}
        </p>
      </div>

      {/* Machine learning prediction */}
      <PredictionCard
        title="Machine Learning Prediction"
        value={result.ml_prediction}
      />

      {/* Deep learning prediction */}
      <PredictionCard
        title="Deep Learning Prediction (LSTM)"
        value={result.lstm_prediction}
      />

      {/* Analyze another review */}
      <div className="text-center mt-8">
        <button
          onClick={() => navigate("/detect")}
          className="px-6 py-3 bg-violet-600 rounded-lg hover:bg-violet-700 transition-colors"
        >
          Analyze Another Review
        </button>
      </div>
    </div>
  );
};

export default Result;
