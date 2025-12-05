import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import Playbooks from './pages/Playbooks';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/playbooks" element={<Playbooks />} />
          <Route path="/settings" element={<div className="text-white">Settings (Coming Soon)</div>} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
