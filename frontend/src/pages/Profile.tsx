import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { api, CULINARY_PREFS, errorText, type CookingHistoryItem } from "../services/api";

// --- US1.3 & US2.3: User Profile & Cooking History Tab Interface ---
export function Profile() {
  const { user, setUser } = useAuth();
  const [tab, setTab] = useState<"profile" | "history">("profile");

  // Profile Form State
  const [bio, setBio] = useState(user?.bio ?? "");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url ?? "");
  const [prefs, setPrefs] = useState<string[]>(user?.culinary_preferences ?? []);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  // --- US2.3 Task 2.3.4: Cooking History Tab State ---
  const [history, setHistory] = useState<CookingHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  useEffect(() => {
    if (tab === "history") {
      let active = true;
      setHistoryLoading(true);
      setHistoryError(null);
      api.getCookingHistory()
        .then((items) => {
          if (active) setHistory(items);
        })
        .catch((err) => {
          if (active) setHistoryError(errorText(err));
        })
        .finally(() => {
          if (active) setHistoryLoading(false);
        });
      return () => {
        active = false;
      };
    }
  }, [tab]);

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
    <div className="card narrow">
      <div className="profile-header">
        {avatarUrl ? <img src={avatarUrl} alt="" className="avatar" /> : <div className="avatar placeholder">{user.username[0].toUpperCase()}</div>}
        <div>
          <h1>{user.username}</h1>
          <p className="muted">{user.email}</p>
        </div>
      </div>

      {/* --- US2.3 Task 2.3.4: Navigation Tabs --- */}
      <div className="tab-bar" style={{ display: "flex", gap: "1rem", borderBottom: "1px solid var(--border)", marginBottom: "1.5rem" }}>
        <button
          type="button"
          className={`link-button ${tab === "profile" ? "active font-bold" : "muted"}`}
          onClick={() => setTab("profile")}
          style={{ paddingBottom: "0.5rem", borderBottom: tab === "profile" ? "2px solid currentColor" : "none" }}
        >
          Profile Settings
        </button>
        <button
          type="button"
          className={`link-button ${tab === "history" ? "active font-bold" : "muted"}`}
          onClick={() => setTab("history")}
          style={{ paddingBottom: "0.5rem", borderBottom: tab === "history" ? "2px solid currentColor" : "none" }}
        >
          Cooking History
        </button>
      </div>

      {tab === "profile" ? (
        <form onSubmit={onSubmit}>
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
      ) : (
        /* --- US2.3 Task 2.3.4: Cooking History Tab View --- */
        <div className="cooking-history">
          <h2>Cooking History</h2>
          {historyLoading && <p className="muted">Loading cooking history…</p>}
          {historyError && <ErrorMessage error={historyError} />}
          {!historyLoading && !historyError && history.length === 0 && (
            <p className="muted">No cooking history yet. Cook a recipe and click "I Cooked This!" to track it here.</p>
          )}
          {!historyLoading && !historyError && history.length > 0 && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
              {history.map((item) => (
                <article key={item.id} className="card" style={{ padding: "1rem" }}>
                  <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                    {item.recipe_image_url && (
                      <img
                        src={item.recipe_image_url}
                        alt={item.recipe_title}
                        style={{ width: "64px", height: "64px", objectFit: "cover", borderRadius: "8px" }}
                      />
                    )}
                    <div style={{ flex: 1 }}>
                      <h3 style={{ margin: 0 }}>
                        <Link to={`/recipes/${item.recipe_id}`}>{item.recipe_title}</Link>
                      </h3>
                      <p className="muted" style={{ margin: "0.25rem 0" }}>
                        Cooked on {new Date(item.cooked_at).toLocaleDateString(undefined, {
                          year: "numeric", month: "short", day: "numeric"
                        })}
                      </p>
                      {item.rating && (
                        <div className="rating" aria-label={`${item.rating} out of 5 stars`}>
                          {"★".repeat(item.rating)}{"☆".repeat(5 - item.rating)}
                          <span className="muted" style={{ marginLeft: "0.5rem" }}>({item.rating}/5)</span>
                        </div>
                      )}
                      {item.notes && (
                        <p style={{ marginTop: "0.5rem", fontStyle: "italic" }}>
                          "{item.notes}"
                        </p>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
