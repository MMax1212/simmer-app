import { useEffect, useState, type ReactNode } from "react";
import { api, tokenStore, type User } from "../services/api";
import { AuthContext } from "./auth";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  // Only "loading" if there's a saved token to check.
  const [loading, setLoading] = useState(() => tokenStore.get() !== null);

  // On page load, if we have a saved token, fetch who it belongs to.
  useEffect(() => {
    if (!tokenStore.get()) return;
    api.me()
      .then(setUser)
      .catch(() => tokenStore.clear()) // expired or invalid token
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const { access_token } = await api.login(email, password);
    tokenStore.set(access_token);
    setUser(await api.me());
  }

  async function register(email: string, username: string, password: string) {
    await api.register(email, username, password);
    await login(email, password);
  }

  function logout() {
    tokenStore.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}
