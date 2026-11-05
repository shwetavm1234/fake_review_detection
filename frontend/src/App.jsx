import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import DetectReview from "./pages/DetectReview";
import UploadFile from "./pages/UploadFile";
import Result from "./pages/Result";
import History from "./pages/History";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { useAuth } from "./context/AuthContext";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex min-h-screen items-center justify-center text-violet-300">Checking your login...</div>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex min-h-screen items-center justify-center bg-black text-violet-300">Loading Fake Review Detection...</div>;
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-black text-white">
      <div className="absolute inset-0 z-10 bg-linear-to-b from-violet-900/30 via-black/50 to-black" />
      {user && <div className="relative z-20"><Navbar /></div>}
      <main className="relative z-20 grow">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
          <Route path="/register" element={user ? <Navigate to="/" replace /> : <Register />} />
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/detect" element={<ProtectedRoute><DetectReview /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><UploadFile /></ProtectedRoute>} />
          <Route path="/result" element={<ProtectedRoute><Result /></ProtectedRoute>} />
          <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to={user ? "/" : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
}
