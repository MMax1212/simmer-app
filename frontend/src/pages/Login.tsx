import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { errorText } from "../services/api";
export function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const from = (useLocation().state as {
        from?: string;
    } | null)?.from ?? "/";
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [busy, setBusy] = useState(false);
    async function onSubmit(e: FormEvent) {
        e.preventDefault();
        setBusy(true);
        setError(null);
        try {
            await login(email, password);
            navigate(from, { replace: true });
        }
        catch (err) {
            setError(errorText(err));
        }
        finally {
            setBusy(false);
        }
    }
    return (<form className="card narrow" onSubmit={onSubmit}>
      <h1>Log in</h1>
      <label>Username or email<input type="text" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="username"/></label>
      <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required maxLength={1024} autoComplete="current-password"/></label>
      <ErrorMessage error={error}/>
      <button type="submit" disabled={busy}>{busy ? "Logging in…" : "Log in"}</button>
      <p className="muted">New here? <Link to="/register">Create an account</Link></p>
    </form>);
}
