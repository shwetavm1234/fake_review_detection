import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, UserRound, Mail, Lock, ArrowRight } from "lucide-react";
import { API_URL, useAuth } from "../context/AuthContext";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const field = "mt-2 flex items-center gap-3 rounded-xl border border-gray-700 bg-black/40 px-4 py-3 focus-within:border-violet-500";
  const input = "w-full bg-transparent text-white outline-none placeholder:text-gray-600";

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (password !== confirm) { setError("Passwords do not match."); return; }
    if (password.length < 8) { setError("Password must contain at least 8 characters."); return; }
    setBusy(true);
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to create account.");
      setUser(data.user);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Could not connect to the server. Start Flask and try again.");
    } finally { setBusy(false); }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 text-white">
      <section className="w-full max-w-md rounded-3xl border border-violet-400/20 bg-gray-950/95 p-8 shadow-2xl shadow-violet-950/40">
        <div className="mb-7 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-600/20 text-violet-300"><ShieldCheck size={30} /></div>
          <p className="text-sm font-semibold tracking-[0.22em] text-violet-300">FAKE REVIEW DETECTION</p>
          <h1 className="mt-4 text-3xl font-bold">Create account</h1>
          <p className="mt-2 text-sm text-gray-400">Register to start checking product reviews</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block text-sm font-medium text-gray-200">Full name<span className={field}><UserRound size={18} className="text-gray-500" /><input required autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" className={input} /></span></label>
          <label className="block text-sm font-medium text-gray-200">Email address<span className={field}><Mail size={18} className="text-gray-500" /><input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className={input} /></span></label>
          <label className="block text-sm font-medium text-gray-200">Password <span className="text-xs text-gray-500">(minimum 8 characters)</span><span className={field}><Lock size={18} className="text-gray-500" /><input type="password" required minLength={8} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Create a password" className={input} /></span></label>
          <label className="block text-sm font-medium text-gray-200">Confirm password<span className={field}><Lock size={18} className="text-gray-500" /><input type="password" required autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Enter password again" className={input} /></span></label>
          {error && <p role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300">{error}</p>}
          <button type="submit" disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 font-semibold transition hover:bg-violet-500 disabled:opacity-60">{busy ? "Creating account..." : "Create account"}<ArrowRight size={18} /></button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-400">Already registered? <Link to="/login" className="font-semibold text-violet-300 hover:text-violet-200">Sign in</Link></p>
      </section>
    </div>
  );
}
