import { useState, type ChangeEvent, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { errorText } from "../services/api";

// --- US1.1: User Account Registration & Login (Registration View & Client Validation) ---
export function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", password: "", confirm: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: k === "username" ? e.target.value.replace(/\s/g, "") : e.target.value });

  // --- US1.1: Task 1.5 & Task 1.6: Client-Side Input Validation & API Integration ---
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (form.password !== form.confirm) return setError("Passwords don't match");
    setBusy(true);
    setError(null);
    try {
      await register(form.email, form.username, form.password);
      navigate("/profile");
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card narrow" onSubmit={onSubmit}>
      <h1>Create your account</h1>
      <label>Email<input type="email" value={form.email} onChange={set("email")} required autoComplete="email" /></label>
      <label>
        Username
        <input value={form.username} onChange={set("username")} required minLength={3} maxLength={50} pattern="[A-Za-z0-9_]+" title="Letters, numbers and underscores only" autoComplete="username" />
      </label>
      <label>Password<input type="password" value={form.password} onChange={set("password")} required minLength={8} maxLength={1024} autoComplete="new-password" /></label>
      <label>Confirm password<input type="password" value={form.confirm} onChange={set("confirm")} required autoComplete="new-password" /></label>
      <ErrorMessage error={error} />
      <button type="submit" disabled={busy}>{busy ? "Creating…" : "Sign up"}</button>
      <p className="muted">Already have an account? <Link to="/login">Log in</Link></p>
    </form>
  );
}
