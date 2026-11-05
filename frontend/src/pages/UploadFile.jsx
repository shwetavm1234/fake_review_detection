import React, { useState } from "react";
import LoadingSpinner from "../components/LoadingSpinner";
import { API_URL } from "../context/AuthContext";

const UploadFile = () => {
  // Initially:- file = null because no file is selected.
  // setFile() is used to change the selected file.
  const [file, setFile] = useState(null);

  // Stores whether the upload is happening.
  // Initially:- isLoading = false, During upload: isLoading = true
  // Initially:// results = null
  const [isLoading, setIsLoading] = useState(false);

  // Stores the response from the backend.
  const [results, setResults] = useState(null);

  // Stores error messages.
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileType = selectedFile.name.split(".").pop().toLowerCase();
      if (fileType === "csv" || fileType === "json") {
        setFile(selectedFile);
        setError("");
      } else {
        setError("Please upload a CSV or JSON file");
        setFile(null);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to upload");
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      // to upload csv file  - formData()
      const formData = new FormData();
      formData.append("file", file);

      // Simulate API call - replace with actual endpoint
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setResults(result);
      } else {
        const err = await response.json();
        setError(err.error || "Error processing file");
      }
    } catch (error) {
      console.error(error);
      setError(
        "Failed to connect to backend. Make sure Flask server is running.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">

      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-black/40 border border-gray-700 text-sm mb-6">
          <span>📁 Batch Processing</span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-4">
          Batch File Upload
        </h1>
        <p className="text-gray-400">
          Upload a CSV or JSON file containing multiple reviews for analysis
        </p>
      </div>

      <div className="bg-black/40 border border-gray-700 rounded-xl p-8 mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label
              htmlFor="file"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Select File (CSV or JSON)
            </label>
            <input
              type="file"
              id="file"
              accept=".csv,.json"
              onChange={handleFileChange}
              className="w-full px-4 py-3 bg-black/50 border border-gray-700 rounded-xl focus:border-violet-500 focus:ring-1 focus:ring-violet-500 outline-none text-white"
              disabled={isLoading}
            />

            {file && (
              <p className="mt-2 text-sm text-green-400">
                {/* converts bytes into KB. */}
                Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-700 text-red-400 rounded-xl">
              {error}
            </div>
          )}

          <div className="flex justify-center">
            <button
              type="submit"
              // Button disabled when: Uploading or No file selected
              disabled={isLoading || !file}
              className="px-8 py-3 rounded-xl text-sm font-medium bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition active:scale-95"
            >
              {isLoading ? <LoadingSpinner /> : "Upload and Analyze"}
            </button>
          </div>
        </form>
      </div>

      {results && results.length > 0 && (
        <div className="bg-black/40 border border-gray-700 rounded-xl p-8">

          <h2 className="text-2xl font-bold text-white mb-6">
            Analysis Results
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="bg-black/30 border-b border-gray-700">
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-300">
                    
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-300">
                    Review
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-300">
                    Prediction
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-300">
                    Confidence
                  </th>
                </tr>
              </thead>

              <tbody>
                {results.map((result, index) => (
                  <tr key={index} className="border-t border-gray-700">
                    <td className="px-4 py-2 text-sm text-gray-400">
                      {index + 1}
                    </td>

                    <td className="px-4 py-2 text-sm text-white max-w-md truncate">
                      {result.review}
                    </td>

                    <td className="px-4 py-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          result.prediction === "Genuine"
                            ? "bg-green-900/30 text-green-400 border border-green-700/30"
                            : "bg-red-900/30 text-red-400 border border-red-700/30"
                        }`}
                      >
                        {result.prediction}
                      </span>
                    </td>

                    <td className="px-4 py-2 text-sm text-gray-400">
                      {(result.confidence * 100).toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadFile;
