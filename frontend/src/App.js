import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Upload from './pages/Upload';
import Summary from './pages/Summary';
import'./App.css';

const App = () => {
  return (
    <div className="bg-slate-100 min-h-screen p-8">
      <nav className="bg-white shadow-md rounded-xl px-6 py-4 mb-8 flex space-x-6 ">
        <Link
          to="/upload"
          className="text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200"
        >
          Upload
        </Link>
        <Link
          to="/summary"
          className="text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200"
        >
          Summary
        </Link>
      </nav>

      <Routes>
        <Route path="/upload" element={<Upload />} />
        <Route path="/summary" element={<Summary />} />
      </Routes>
    </div>

  );
};

export default App;
