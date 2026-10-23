import React, { useEffect, useState } from 'react';
import { ChefHat, Heart, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

interface Recipe {
  id: number;
  title: string;
  author: string;
  cook_time_mins: number;
  likes: number;
}

export default function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  useEffect(() => {
    // Check connection to the FastAPI backend
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setBackendStatus('connected');
          // Fetch sample recipes
          return fetch('/api/recipes/placeholder').then((r) => r.json());
        }
      })
      .then((data) => {
        if (data) setRecipes(data);
      })
      .catch(() => {
        setBackendStatus('disconnected');
      });
  }, []);

  return (
<<<<<<< HEAD
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '32px 16px' }}>
      {/* Header */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #e7e5e4', paddingBottom: '20px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ backgroundColor: '#f97316', padding: '10px', borderRadius: '12px', color: 'white', display: 'flex' }}>
            <ChefHat size={28} />
          </div>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#1c1917' }}>Simmer</h1>
            <p style={{ fontSize: '13px', color: '#78716c' }}>Social cooking for culinary enthusiasts</p>
          </div>
        </div>

        {/* Status Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', padding: '8px 14px', borderRadius: '20px', backgroundColor: backendStatus === 'connected' ? '#ecfdf5' : backendStatus === 'disconnected' ? '#fef2f2' : '#f5f5f4', color: backendStatus === 'connected' ? '#047857' : backendStatus === 'disconnected' ? '#b91c1c' : '#78716c' }}>
          {backendStatus === 'connected' && <CheckCircle2 size={16} />}
          {backendStatus === 'disconnected' && <AlertCircle size={16} />}
          <span>
            {backendStatus === 'checking' && 'Connecting to Backend...'}
            {backendStatus === 'connected' && 'Backend Connected (:8000)'}
            {backendStatus === 'disconnected' && 'Backend Offline (start uvicorn)'}
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <section style={{ backgroundColor: '#ffffff', borderRadius: '16px', padding: '24px', border: '1px solid #e7e5e4', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>🎉 Welcome to Simmer MVP Foundation!</h2>
          <p style={{ color: '#57534e', fontSize: '14px', lineHeight: '1.6' }}>
            This repository has been scaffolded for Team Simmer. Frontend is powered by <strong>TypeScript + React + Vite</strong>, 
            and the backend runs on <strong>Python + FastAPI</strong>.
          </p>
        </section>

        {/* Recipe Cards Preview */}
        <section>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#44403c' }}>Featured Community Recipes (Live API Data)</h3>
          {recipes.length === 0 ? (
            <p style={{ color: '#a8a29e', fontSize: '14px' }}>Loading recipes from backend or backend is currently offline...</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
              {recipes.map((recipe) => (
                <div key={recipe.id} style={{ backgroundColor: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '14px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
                  <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '6px' }}>{recipe.title}</h4>
                  <p style={{ fontSize: '13px', color: '#78716c', marginBottom: '16px' }}>By {recipe.author}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px', color: '#57534e', borderTop: '1px solid #f5f5f4', paddingTop: '12px' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Clock size={15} color="#f97316" /> {recipe.cook_time_mins} mins
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Heart size={15} color="#ef4444" /> {recipe.likes}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
=======
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
>>>>>>> US-1.1
  );
}
