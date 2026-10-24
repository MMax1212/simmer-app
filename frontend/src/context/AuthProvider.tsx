import { useEffect, useState, type ReactNode } from "react";
import { api, SESSION_EXPIRED, tokenStore, type User } from "../services/api";
import { AuthContext } from "./auth";

// --- US1.1: User Account Registration & Login (Global Authentication State Provider) ---
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(() => tokenStore.get() !== null);

  useEffect(() => {
    let active = true;
    const expire = () => { setUser(null); setLoading(false); };
    window.addEventListener(SESSION_EXPIRED, expire);
    if (tokenStore.get()) {
      api.me().then((me) => { if (active) setUser(me); })
        .catch(() => { if (active) { tokenStore.clear(); setUser(null); } })
        .finally(() => { if (active) setLoading(false); });
    }
    return () => { active = false; window.removeEventListener(SESSION_EXPIRED, expire); };
  }, []);

  async function login(identifier: string, password: string) {
    const response = await api.login(identifier, password);
    tokenStore.set(response.access_token);
    setUser(response.user);
  }

  async function register(email: string, username: string, password: string) {
    await api.register(email, username, password);
    await login(email, password);
  }

  function logout() {
    tokenStore.clear();
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>{children}</AuthContext.Provider>;
}
