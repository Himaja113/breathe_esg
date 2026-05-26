import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Filter, Check, AlertTriangle } from 'lucide-react';
import api from '../api';

export default function ReviewTable() {
  const [records, setRecords] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');

  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecords();
  }, [statusFilter]);

  const fetchRecords = async () => {
    try {
      let url = 'records/';
      if (statusFilter) url += `?status=${statusFilter}`;
      const res = await api.get(url);
      setRecords(res.data.results);
      setError(null);
    } catch (err) {
      console.error("ReviewTable API Error:", err);
      setError(err.message || "Failed to load records");
    }
  };

  const approveRecord = async (id) => {
    await api.patch(`records/${id}/approve/`);
    fetchRecords();
  };

  const getStatusBadge = (status) => {
    const map = {
      PENDING: 'bg-amber-100 text-amber-800',
      FLAGGED: 'bg-red-100 text-red-800',
      APPROVED: 'bg-green-100 text-green-800',
      LOCKED: 'bg-gray-200 text-gray-800',
    };
    return <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${map[status]}`}>{status}</span>;
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Data Review</h1>
        
        <div className="flex items-center gap-4">
          <div className="relative">
            <Filter className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <select 
              value={statusFilter} 
              onChange={e => setStatusFilter(e.target.value)}
              className="pl-9 pr-4 py-2 border rounded-lg bg-white text-sm focus:ring-2 focus:ring-brand-500 outline-none"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="FLAGGED">Flagged</option>
              <option value="APPROVED">Approved</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-sm text-gray-500 font-medium">
                <th className="p-4">Date</th>
                <th className="p-4">Source</th>
                <th className="p-4">Activity</th>
                <th className="p-4 text-right">Quantity</th>
                <th className="p-4 text-right">Emissions (kg CO2e)</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {records.map(record => (
                <tr key={record.id} className="hover:bg-gray-50 transition-colors group">
                  <td className="p-4 text-sm text-gray-900">
                    <Link to={`/review/${record.id}`} className="hover:underline hover:text-brand-600">
                      {record.reporting_date}
                    </Link>
                  </td>
                  <td className="p-4 text-sm text-gray-500">{record.source_type}</td>
                  <td className="p-4 text-sm font-medium text-gray-900">{record.activity_type}</td>
                  <td className="p-4 text-sm text-gray-900 text-right">{parseFloat(record.normalized_quantity).toLocaleString()} {record.normalized_unit}</td>
                  <td className="p-4 text-sm text-gray-900 text-right">{record.calculated_emissions_kg ? parseFloat(record.calculated_emissions_kg).toLocaleString() : '-'}</td>
                  <td className="p-4">
                    {getStatusBadge(record.status)}
                    {record.status === 'FLAGGED' && (
                      <p className="text-xs text-red-600 mt-1 max-w-[200px] truncate" title={record.anomaly_reason}>
                        {record.anomaly_reason}
                      </p>
                    )}
                  </td>
                  <td className="p-4 text-right space-x-2">
                    {['PENDING', 'FLAGGED'].includes(record.status) && (
                      <button 
                        onClick={() => approveRecord(record.id)}
                        className="text-gray-400 hover:text-green-600 p-1 bg-white rounded-md border shadow-sm transition-all"
                        title="Approve"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    )}
                    <Link to={`/review/${record.id}`} className="text-sm text-brand-600 hover:text-brand-800 font-medium">
                      Details
                    </Link>
                  </td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr>
                  <td colSpan="7" className="p-8 text-center text-gray-500">No records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
