import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Upload from './pages/Upload';
import Summary from './pages/Summary';
import'./App.css';

const App = () => {
  return (
    <div className="bg-slate-300 min-h-screen p-8">
      <nav style={{ padding: "1rem", background: "#f0f0f0" }}>
        <Link to="/upload" style={{ marginRight: "1rem" }}>Upload</Link>
        <Link to="/summary">Summary</Link>
      </nav>

      <Routes>
        <Route path="/upload" element={<Upload />} />
        <Route path="/summary" element={<Summary />} />
      </Routes>
    </div>
  );
};

export default App;
