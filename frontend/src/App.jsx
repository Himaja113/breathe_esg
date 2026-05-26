import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Ingest from './pages/Ingest';
import ReviewTable from './pages/ReviewTable';
import RecordDetail from './pages/RecordDetail';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-500 rounded-md flex items-center justify-center text-white font-bold shadow-sm">B</div>
            <span className="text-xl font-bold text-gray-900 tracking-tight">Breathe ESG</span>
          </div>
          <nav className="flex gap-6">
            <Link to="/" className="text-gray-500 hover:text-brand-600 font-medium transition-colors">Dashboard</Link>
            <Link to="/ingest" className="text-gray-500 hover:text-brand-600 font-medium transition-colors">Ingest</Link>
            <Link to="/review" className="text-gray-500 hover:text-brand-600 font-medium transition-colors">Review</Link>
          </nav>
        </header>
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ingest" element={<Ingest />} />
            <Route path="/review" element={<ReviewTable />} />
            <Route path="/review/:id" element={<RecordDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
