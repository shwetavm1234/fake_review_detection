// import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import { Loader2, FileText } from "lucide-react";
// import { API_URL } from "../context/AuthContext";

// const DetectReview = () => {
//   // reviewText - Stores the text entered by the user.
//   // setReviewText - Function used to update reviewText.
//   const [reviewText, setReviewText] = useState("");

//   // Stores whether the request is running.
//   // Initially: isLoading = false - The app is not processing anything.
//   const [isLoading, setIsLoading] = useState(false);

//   // Stores error messages.
//   // Initially:- error = "" -> No error.
//   const [error, setError] = useState("");

//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!reviewText.trim()) {
//       setError("Please enter a review to analyze");
//       return;
//     }
//     setIsLoading(true);
//     setError("");

//     try {
//       const response = await fetch(`${API_URL}/analyze`, {
//         method: "POST",
//         credentials: "include",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ review: reviewText }),
//       });
     
// const data = await response.json();

// if (!response.ok) {
//   throw new Error(data.error || "Failed to analyze review");
// }

// console.log("Backend response:", data);

// navigate("/result", {
//   state: {
//     result: data,
//     reviewText: reviewText,
//   },
// });

//     } catch (error) {
//       setError("Backend not running or connection error");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="max-w-4xl mx-auto px-6 py-12">

//       <div className="text-center mb-8">
//         <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-black/40 border border-gray-700 text-sm mb-6">
//           <FileText className="w-4 h-4" />
//           <span>Single Review Analysis</span>
//         </div>
//         <h1 className="text-3xl font-bold text-white mb-4">Review Analysis</h1>
//         <p className="text-gray-400">
//           Enter a review below to check if it's genuine or fake
//         </p>
//       </div>

//       <div className="bg-black/40 border border-gray-700 rounded-xl p-8">
      
//         <form onSubmit={handleSubmit}>
//           <div className="mb-6">
//             <label
//               htmlFor="review"
//               className="block text-sm font-medium text-gray-300 mb-2"
//             >
//               Review Text
//             </label>
//             <textarea
//               id="review"
//               rows={6}
//               className="w-full px-4 py-3 bg-black/50 border border-gray-700 rounded-xl focus:border-violet-500 focus:ring-1 focus:ring-violet-500 outline-none text-white placeholder-gray-400"
//               placeholder="Paste or type the review you want to analyze..."
//               value={reviewText}
//               onChange={(e) => setReviewText(e.target.value)}
//               disabled={isLoading}
//             />
//           </div>

//           {error && (
//             <div className="mb-4 p-3 bg-red-900/30 border border-red-700 text-red-400 rounded-xl">
//               {error}
//             </div>
//           )}

//           <div className="flex justify-center">
//             <button
//               type="submit"
//               disabled={isLoading}
//               className="px-8 py-3 rounded-xl text-sm font-medium bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition active:scale-95"
//             >
//               {isLoading ? (
//                 <div className="flex items-center space-x-2">
//                   <Loader2 className="animate-spin w-4 h-4" />
//                   <span>Processing...</span>
//                 </div>
//               ) : (
//                 "Analyze Review"
//               )}
//             </button>
//           </div>
//         </form>
//       </div>
//     </div>
//   );
// };

// export default DetectReview;
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, FileText } from "lucide-react";
import { API_URL } from "../context/AuthContext";

const DetectReview = () => {
  const [reviewText, setReviewText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!reviewText.trim()) {
      setError("Please enter a review to analyze.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          review: reviewText.trim(),
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 401) {
        setError("Please login first to analyze a review.");
        return;
      }

      if (response.status === 403) {
        setError("You are not authorized to perform this action.");
        return;
      }

      if (!response.ok) {
        throw new Error(
          data.error || data.message || `Server error: ${response.status}`
        );
      }

      console.log("Analysis successful:", data);

      navigate("/result", {
        state: {
          result: data,
          reviewText: reviewText,
        },
      });

    } catch (err) {
      console.error("Review analysis error:", err);

      if (err instanceof TypeError) {
        setError(
          "Cannot connect to the backend. Please check whether Flask is running."
        );
      } else {
        setError(err.message || "Something went wrong.");
      }

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">

      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-black/40 border border-gray-700 text-sm mb-6">
          <FileText className="w-4 h-4" />
          <span>Single Review Analysis</span>
        </div>

        <h1 className="text-3xl font-bold text-white mb-4">
          Review Analysis
        </h1>

        <p className="text-gray-400">
          Enter a review below to check if it's genuine or fake.
        </p>
      </div>

      <div className="bg-black/40 border border-gray-700 rounded-xl p-8">

        <form onSubmit={handleSubmit}>

          <div className="mb-6">
            <label
              htmlFor="review"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Review Text
            </label>

            <textarea
              id="review"
              rows={6}
              className="w-full px-4 py-3 bg-black/50 border border-gray-700 rounded-xl focus:border-violet-500 focus:ring-1 focus:ring-violet-500 outline-none text-white placeholder-gray-400"
              placeholder="Paste or type the review you want to analyze..."
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-700 text-red-400 rounded-xl">
              {error}
            </div>
          )}

          <div className="flex justify-center">
            <button
              type="submit"
              disabled={isLoading}
              className="px-8 py-3 rounded-xl text-sm font-medium bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition active:scale-95"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <Loader2 className="animate-spin w-4 h-4" />
                  <span>Processing...</span>
                </div>
              ) : (
                "Analyze Review"
              )}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default DetectReview;