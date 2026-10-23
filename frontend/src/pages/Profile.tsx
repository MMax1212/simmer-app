import { useState, type FormEvent } from "react";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { api, CULINARY_PREFS, errorText } from "../services/api";

// --- US1.3: User Profile Management (Profile Viewing & Editing Interface) ---
export function Profile() {
  const { user, setUser } = useAuth();
  const [bio, setBio] = useState(user?.bio ?? "");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url ?? "");
  const [prefs, setPrefs] = useState<string[]>(user?.culinary_preferences ?? []);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  if (!user) return null;

  const toggle = (p: string) => setPrefs(prefs.includes(p) ? prefs.filter((x) => x !== p) : [...prefs, p]);

  // --- US1.3: Task 3.3: Submit Profile Updates to Backend ---
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaved(false);
    try {
      setUser(await api.updateProfile({ bio: bio || null, avatar_url: avatarUrl || null, culinary_preferences: prefs }));
      setSaved(true);
    } catch (err) {
      setError(errorText(err));
    }
  }

  return (
    <form className="card narrow" onSubmit={onSubmit}>
      <div className="profile-header">
        {avatarUrl ? <img src={avatarUrl} alt="" className="avatar" /> : <div className="avatar placeholder">{user.username[0].toUpperCase()}</div>}
        <div>
          <h1>{user.username}</h1>
          <p className="muted">{user.email}</p>
        </div>
      </div>
      <label>Bio<textarea value={bio} onChange={(e) => setBio(e.target.value)} maxLength={500} rows={3} placeholder="Tell the community what you love to cook" /></label>
      <label>Avatar image URL<input type="url" value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} placeholder="https://…" maxLength={255} pattern="https?://.*" /></label>
      <fieldset>
        <legend>Culinary preferences</legend>
        <div className="chips">
          {Array.from(new Set([...CULINARY_PREFS, ...prefs])).map((p) => (
            <label key={p} className={`chip ${prefs.includes(p) ? "on" : ""}`}>
              <input type="checkbox" checked={prefs.includes(p)} onChange={() => toggle(p)} />
              {p}
            </label>
          ))}
        </div>
      </fieldset>
      <ErrorMessage error={error} />
      {saved && <p className="success">Profile saved.</p>}
      <button type="submit">Save profile</button>
    </form>
  );
}
