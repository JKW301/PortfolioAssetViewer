import { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import { Toaster } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" theme="dark" />
    </div>
  );
}

export default App;