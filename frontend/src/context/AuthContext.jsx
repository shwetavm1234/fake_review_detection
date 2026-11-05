import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);
// Change this only if your Flask backend runs at a different address.
// export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";
// export const API_URL = "http://localhost:5000";
export const API_URL = "http://127.0.0.1:5000";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetch(`${API_URL}/auth/me`, { credentials: "include" })
      .then((response) => {
        if (!response.ok) throw new Error("Unable to check login session");
        return response.json();
      })
      .then((data) => { if (active) setUser(data.user); })
      .catch(() => { if (active) setUser(null); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
