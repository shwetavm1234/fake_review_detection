import React from "react";
import { Link } from "react-router-dom";
import { Search, Zap, BarChart3 } from "lucide-react";

const Home = () => {
  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center text-white overflow-hidden">

      {/* Floating Background Elements */}
      {/* <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-violet-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div> */}

      {/* Content */}
      <main className="relative z-10 text-center px-6 mt-10">
        {/* <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-black/40 border border-gray-700 text-sm mb-6 animate-fade-in-up">
          <span>🤖 AI-Powered Detection</span>
        </div> */}

        {/* Headings */}
        <h1 className="text-4xl sm:text-6xl font-semibold tracking-tighter mb-4 animate-fade-in-up delay-200">
          Detect{" "}
          <span className="text-violet-500 animate-pulse">Fake Reviews</span>
        </h1>

        <h2 className="text-2xl sm:text-4xl font-semibold text-gray-300 mb-6 animate-fade-in-up delay-300">
          <span className="text-white">Know which reviews you can trust</span>
        </h2>

        {/* Description */}
        <p className="text-gray-400 max-w-2xl mx-auto mb-10 animate-fade-in-up delay-500">
          “Utilizing modern Machine Learning and Natural Language Processing
          methods to identify fake reviews and improve reliability in online
          systems.”
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up delay-700">
          <Link
            to="/detect"
            className="px-8 py-3 rounded-xl text-sm font-medium bg-violet-600 hover:bg-violet-700 transition-all duration-300 active:scale-95 hover:scale-105 hover:shadow-lg hover:shadow-violet-500/25"
          >
            Analyze Single Review
          </Link>
          <Link
            to="/upload"
            className="px-8 py-3 rounded-xl text-sm font-medium bg-black/50 border border-gray-700 hover:border-violet-500 transition-all duration-300 active:scale-95 hover:scale-105 hover:shadow-lg hover:shadow-violet-500/10"
          >
            Upload Batch File
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-16 max-w-4xl mx-auto">
          <div className="bg-black/40 border border-gray-700 p-6 rounded-xl hover:bg-black/60 transition-all duration-500 hover:scale-105 hover:border-violet-500/50 animate-fade-in-up delay-1000 group">
            <Search className="text-violet-500 w-8 h-8 mb-4 mx-auto group-hover:animate-bounce" />
            <h3 className="text-xl font-semibold mb-2 text-white">
              Accurate Detection
            </h3>
            <p className="text-gray-400">
              Advanced ML algorithms analyze review patterns to identify fake
              content with high accuracy.
            </p>
          </div>

          <div className="bg-black/40 border border-gray-700 p-6 rounded-xl hover:bg-black/60 transition-all duration-500 hover:scale-105 hover:border-violet-500/50 animate-fade-in-up delay-1200 group">
            <Zap className="text-violet-500 w-8 h-8 mb-4 mx-auto group-hover:animate-bounce" />
            <h3 className="text-xl font-semibold mb-2 text-white">
              Fast Processing
            </h3>
            <p className="text-gray-400">
              Real-time analysis of reviews with instant results and confidence
              scores.
            </p>
          </div>

          <div className="bg-black/40 border border-gray-700 p-6 rounded-xl hover:bg-black/60 transition-all duration-500 hover:scale-105 hover:border-violet-500/50 animate-fade-in-up delay-1400 group">
            <BarChart3 className="text-violet-500 w-8 h-8 mb-4 mx-auto group-hover:animate-bounce" />
            <h3 className="text-xl font-semibold mb-2 text-white">
              Batch Analysis
            </h3>
            <p className="text-gray-400">
              Upload CSV or JSON files to analyze multiple reviews simultaneously.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
