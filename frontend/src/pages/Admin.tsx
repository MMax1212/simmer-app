import { useEffect, useState } from "react";
import { ErrorMessage } from "../components/ErrorMessage";
import { useAuth } from "../context/auth";
import { api, errorText, type User } from "../services/api";

/** US1.2: minimal admin panel to view accounts and (de)activate them. */
export function Admin() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.adminListUsers().then(setUsers).catch((e) => setError(errorText(e)));
  }, []);

  async function update(u: User, changes: { is_active?: boolean; role?: string }) {
    try {
      const updated = await api.adminUpdateUser(u.id, changes);
      setUsers(users.map((x) => (x.id === u.id ? updated : x)));
    } catch (e) {
      setError(errorText(e));
    }
  }

  return (
    <section className="card">
      <h1>Admin: users</h1>
      <ErrorMessage error={error} />
      <div className="table-wrap">
        <table>
          <thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.email}</td>
                <td>{u.role}</td>
                <td>{u.is_active ? "Active" : "Deactivated"}</td>
                <td>
                  {u.id !== me?.id && (
                    <button className={u.is_active ? "danger small" : "secondary small"} onClick={() => update(u, { is_active: !u.is_active })}>
                      {u.is_active ? "Deactivate" : "Reactivate"}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
