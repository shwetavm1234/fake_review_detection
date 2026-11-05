import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";
import { API_URL, useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to log in.");
      setUser(data.user);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Could not connect to the server. Start Flask and try again.");
    } finally {
      setBusy(false);
    }
  }

  const fieldClass = "mt-2 flex items-center gap-3 rounded-xl border border-gray-700 bg-black/40 px-4 py-3 focus-within:border-violet-500";
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 text-white">
      <section className="w-full max-w-md rounded-3xl border border-violet-400/20 bg-gray-950/95 p-8 shadow-2xl shadow-violet-950/40">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-600/20 text-violet-300"><ShieldCheck size={30} /></div>
          <p className="text-sm font-semibold tracking-[0.22em] text-violet-300">FAKE REVIEW DETECTION</p>
          <h1 className="mt-4 text-3xl font-bold">Welcome back</h1>
          <p className="mt-2 text-sm text-gray-400">Sign in to continue to your dashboard</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          <label className="block text-sm font-medium text-gray-200">Email address
            <span className={fieldClass}><Mail size={18} className="text-gray-500" /><input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className="w-full bg-transparent text-white outline-none placeholder:text-gray-600" /></span>
          </label>
          <label className="block text-sm font-medium text-gray-200">Password
            <span className={fieldClass}><Lock size={18} className="text-gray-500" /><input type={showPassword ? "text" : "password"} required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" className="w-full bg-transparent text-white outline-none placeholder:text-gray-600" /><button type="button" onClick={() => setShowPassword((value) => !value)} className="text-gray-500 hover:text-white" aria-label="Toggle password visibility">{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></span>
          </label>
          {error && <p role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300">{error}</p>}
          <button type="submit" disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 font-semibold transition hover:bg-violet-500 disabled:opacity-60">{busy ? "Signing in..." : "Sign in"}<ArrowRight size={18} /></button>
        </form>
        <p className="mt-7 text-center text-sm text-gray-400">Don't have an account? <Link to="/register" className="font-semibold text-violet-300 hover:text-violet-200">Create account</Link></p>
      </section>
    </div>
  );
}
