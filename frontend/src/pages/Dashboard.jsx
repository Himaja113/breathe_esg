import React, { useEffect, useState } from 'react';
import { ArrowUpRight, CheckCircle2, Clock, AlertCircle, Lock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('dashboard/summary/')
      .then(res => setData(res.data))
      .catch(err => {
        console.error("Dashboard API Error:", err);
        setError(err.message || "Failed to load dashboard data");
      });
  }, []);

  if (error) return <div className="p-8 text-red-500 font-bold">API Error: {error}. Please check if the backend is running.</div>;
  if (!data) return <div className="p-8">Loading...</div>;

  const stats = [
    { name: 'Total Records', value: data.total_records, icon: ArrowUpRight, color: 'text-gray-900' },
    { name: 'Pending Review', value: data.pending, icon: Clock, color: 'text-amber-500' },
    { name: 'Flagged', value: data.flagged, icon: AlertCircle, color: 'text-red-500' },
    { name: 'Approved', value: data.approved, icon: CheckCircle2, color: 'text-green-500' },
    { name: 'Locked', value: data.locked, icon: Lock, color: 'text-brand-600' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Platform Overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col">
            <div className="flex justify-between items-start">
              <span className="text-sm font-medium text-gray-500">{stat.name}</span>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <span className="text-3xl font-bold text-gray-900 mt-4">{stat.value}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Emissions by Scope (kg CO2e)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.emissions_by_scope}>
                <XAxis dataKey="scope" />
                <YAxis />
                <Tooltip cursor={{fill: 'transparent'}} />
                <Bar dataKey="total" fill="#22c55e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Recent Ingestion Jobs</h2>
          <div className="space-y-4">
            {data.recent_jobs.map((job) => (
              <div key={job.id} className="flex justify-between items-center p-4 rounded-lg bg-gray-50">
                <div>
                  <p className="font-medium text-gray-900">{job.source_type}</p>
                  <p className="text-sm text-gray-500">{new Date(job.ingested_at).toLocaleString()}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${job.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
                    {job.status}
                  </span>
                  <p className="text-sm text-gray-500 mt-1">{job.row_count} rows</p>
                </div>
              </div>
            ))}
            {data.recent_jobs.length === 0 && <p className="text-gray-500">No recent jobs.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
