import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthProvider";
import { Admin } from "./pages/Admin";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import "./styles.css";
export default function App() {
    return <AuthProvider>
    <BrowserRouter>
      <Navbar />
      <main className="app-container">
        <Routes>
          <Route path="/" element={<Home />}/>
          <Route path="/login" element={<Login />}/>
          <Route path="/register" element={<Register />}/>
          <Route path="/admin" element={<ProtectedRoute adminOnly><Admin /></ProtectedRoute>}/>
          <Route path="*" element={<p className="muted">Page not found.</p>}/>
        </Routes>
      </main>
    </BrowserRouter>
  </AuthProvider>;
}
