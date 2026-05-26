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
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Platform Overview</h1>
          <p className="text-gray-500 mt-1">Real-time carbon accounting ledger and ingestion status.</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col group cursor-default">
            <div className="flex justify-between items-start">
              <span className="text-sm font-semibold text-gray-500 group-hover:text-gray-700 transition-colors">{stat.name}</span>
              <div className={`p-2 rounded-lg bg-gray-50 ${stat.color.replace('text-', 'bg-').replace('500', '100').replace('600', '100')} group-hover:scale-110 transition-transform`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </div>
            <span className="text-4xl font-black text-gray-900 mt-4 tracking-tight">{stat.value.toLocaleString()}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold text-gray-900 mb-8 flex items-center gap-2">
            Emissions by Scope
            <span className="text-sm font-normal text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">kg CO2e</span>
          </h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.emissions_by_scope} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={1}/>
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0.6}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="scope" axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} tickFormatter={(value) => value.toLocaleString()} />
                <Tooltip 
                  cursor={{fill: '#f3f4f6'}}
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="total" fill="url(#colorTotal)" radius={[6, 6, 0, 0]} maxBarSize={60} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Ingestion Jobs</h2>
            <button className="text-sm text-brand-600 font-medium hover:text-brand-700">View all</button>
          </div>
          <div className="space-y-4">
            {data.recent_jobs.map((job) => (
              <div key={job.id} className="flex justify-between items-center p-4 rounded-xl bg-gray-50/50 border border-gray-100 hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white rounded-lg shadow-sm border border-gray-100">
                    <ArrowUpRight className="w-5 h-5 text-gray-400" />
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{job.source_type}</p>
                    <p className="text-sm text-gray-500 font-medium">{new Date(job.ingested_at).toLocaleString()}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase
                    ${job.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                    {job.status}
                  </span>
                  <p className="text-sm text-gray-500 mt-2 font-medium">{job.row_count} rows processed</p>
                </div>
              </div>
            ))}
            {data.recent_jobs.length === 0 && (
              <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                <Clock className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">No recent jobs found.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
