import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthProvider";
import { Admin } from "./pages/Admin";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";
import { MyRecipes } from "./pages/MyRecipes";
import { Profile } from "./pages/Profile";
import { RecipeDetail } from "./pages/RecipeDetail";
import { RecipeForm } from "./pages/RecipeForm";
import { Register } from "./pages/Register";
import "./styles.css";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <main className="app-container">
          <Routes>
            <Route path="/" element={<Home />} />
            {/* US1.1: User Account Registration & Login */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* US1.3: User Profile Management */}
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            {/* US1.5: Personal Recipe Tab ("My Recipes") */}
            <Route path="/recipes/my-recipes" element={<ProtectedRoute><MyRecipes /></ProtectedRoute>} />
            {/* US1.4: Recipe Creation & Saving */}
            <Route path="/recipes/new" element={<ProtectedRoute><RecipeForm /></ProtectedRoute>} />
            <Route path="/recipes/:id/edit" element={<ProtectedRoute><RecipeForm /></ProtectedRoute>} />
            {/* US1.5: Recipe Detail View */}
            <Route path="/recipes/:id" element={<RecipeDetail />} />
            {/* US1.2: Admin Account & RBAC */}
            <Route path="/admin" element={<ProtectedRoute adminOnly><Admin /></ProtectedRoute>} />
            <Route path="*" element={<p className="muted">Page not found.</p>} />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
  );
}
