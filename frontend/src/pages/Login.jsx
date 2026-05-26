import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('login/', { username, password });
      if (res.data.token && res.data.role === 'ANALYST') {
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('role', res.data.role);
        localStorage.setItem('username', res.data.username);
        // Force full reload to update api interceptor and App state if needed, or just navigate
        window.location.href = '/';
      } else {
        setError('Only Analysts are authorized to login.');
      }
    } catch (err) {
      setError('Invalid credentials.');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-sm border max-w-sm w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">Analyst Login</h1>
        {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">{error}</div>}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={e => setUsername(e.target.value)}
              className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-brand-500 focus:border-brand-500 p-2 border" 
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-brand-500 focus:border-brand-500 p-2 border" 
              required 
            />
          </div>
          <button type="submit" className="w-full bg-brand-600 text-white rounded-lg p-2 font-medium hover:bg-brand-700">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
