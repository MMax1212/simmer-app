import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth";
export function ProtectedRoute({ children, adminOnly = false }: {
    children: ReactNode;
    adminOnly?: boolean;
}) {
    const { user, loading } = useAuth();
    const location = useLocation();
    if (loading)
        return <p className="muted">Loading…</p>;
    if (!user)
        return <Navigate to="/login" replace state={{ from: location.pathname }}/>;
    if (adminOnly && user.role !== "admin")
        return <Navigate to="/" replace state={{ notice: "Access denied: administrators only." }}/>;
    return <>{children}</>;
}
