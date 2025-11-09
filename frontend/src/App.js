import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { authService } from './apiClient';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import ChangePassword from './pages/ChangePassword';
import Subscription from './pages/Subscription';
import DNAProfiling from './pages/DNAProfiling'; // Add import for DNA Profiling
import SmartJournal from './pages/SmartJournal';
import SmartJournalEntries from './pages/SmartJournalEntries';
import MentalWellness from './pages/MentalWellness';
import Nutrition from './pages/Nutrition';
import AICompanion from './pages/AICompanion';
import AICompanionRaw from './pages/AICompanionRaw';  // Add import for Raw AI Companion

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const isAuthenticated = authService.isTokenValid();
  
  // If not authenticated, redirect to login with intended destination
  if (!isAuthenticated) {
    return <Navigate 
      to="/login" 
      state={{ from: location }} 
      replace 
    />;
  }
  
  return children;
};

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/change-password"
            element={
              <ProtectedRoute>
                <ChangePassword />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription"
            element={
              <ProtectedRoute>
                <Subscription />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dna-profiling"
            element={
              <ProtectedRoute>
                <DNAProfiling />
              </ProtectedRoute>
            }
          />
          <Route
            path="/smart-journal"
            element={
              <ProtectedRoute>
                <SmartJournal />
              </ProtectedRoute>
            }
          />
          <Route
            path="/smart-journal/entries"
            element={
              <ProtectedRoute>
                <SmartJournalEntries />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mental-wellness"
            element={
              <ProtectedRoute>
                <MentalWellness />
              </ProtectedRoute>
            }
          />
          <Route
            path="/nutrition"
            element={
              <ProtectedRoute>
                <Nutrition />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai-companion"
            element={
              <ProtectedRoute>
                <AICompanion />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai-companion-raw"
            element={
              <ProtectedRoute>
                <AICompanionRaw />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
