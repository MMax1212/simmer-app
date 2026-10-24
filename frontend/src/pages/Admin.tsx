import { useEffect, useState } from "react";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { api, errorText, type User } from "../services/api";

// --- US1.2: Admin Account & RBAC (Admin User Management Console) ---
export function Admin() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState<number | null>(null);

  // --- US1.2: Task 2.5: Load User List from Admin API ---
  useEffect(() => {
    let active = true;
    api.adminListUsers().then((items) => { if (active) setUsers(items); })
      .catch((e) => { if (active) setError(errorText(e)); });
    return () => { active = false; };
  }, []);

  // --- US1.2: Task 2.4 & 2.5: Update User Status or Role ---
  async function update(user: User, changes: { is_active?: boolean; role?: string }) {
    setError(null);
    setPending(user.id);
    try {
      const updated = await api.adminUpdateUser(user.id, changes);
      setUsers((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch (e) { setError(errorText(e)); }
    finally { setPending(null); }
  }

  return <section className="card">
    <h1>Admin: users</h1>
    <ErrorMessage error={error} />
    <div className="table-wrap">
      <table>
        <thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Status</th><th>Manage</th></tr></thead>
        <tbody>{users.map((user) => <tr key={user.id}>
          <td>{user.username}</td><td>{user.email}</td>
          <td>{user.id === me?.id ? user.role : <select aria-label={"Role for " + user.username} value={user.role}
            disabled={pending !== null} onChange={(e) => update(user, { role: e.target.value })}>
            <option value="user">User</option><option value="admin">Admin</option>
          </select>}</td>
          <td>{user.is_active ? "Active" : "Deactivated"}</td>
          <td>{user.id !== me?.id && <button className={user.is_active ? "danger small" : "secondary small"}
            disabled={pending !== null} onClick={() => update(user, { is_active: !user.is_active })}>
            {user.is_active ? "Deactivate" : "Reactivate"}
          </button>}</td>
        </tr>)}</tbody>
      </table>
    </div>
  </section>;
}
