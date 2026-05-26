import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Edit2, CheckCircle2, History, AlertTriangle } from 'lucide-react';
import api from '../api';

export default function RecordDetail() {
  const { id } = useParams();
  const [record, setRecord] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({});

  const fetchRecord = async () => {
    const res = await api.get(`records/${id}/`);
    setRecord(res.data);
    setEditForm({
      activity_type: res.data.activity_type,
      normalized_quantity: res.data.normalized_quantity,
    });
    
    const auditRes = await api.get(`audit/${id}/`);
    setAuditLogs(auditRes.data.results || []);
  };

  useEffect(() => {
    fetchRecord();
  }, [id]);

  const handleSave = async () => {
    await api.patch(`records/${id}/`, editForm);
    setIsEditing(false);
    fetchRecord();
  };

  const isAnalyst = localStorage.getItem('role') === 'ANALYST';

  if (!record) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <Link to="/review" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-brand-600 transition-colors">
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Review
      </Link>

      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Record #{record.id}</h1>
        <div className="flex gap-3">
          {isAnalyst && ['PENDING', 'FLAGGED'].includes(record.status) && (
            <>
              <button 
                onClick={() => setIsEditing(!isEditing)}
                className="px-4 py-2 border rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <Edit2 className="w-4 h-4" /> Edit
              </button>
              <button 
                onClick={async () => { await api.patch(`records/${id}/approve/`); fetchRecord(); }}
                className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" /> Approve
              </button>
            </>
          )}
        </div>
      </div>

      {record.status === 'FLAGGED' && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-xl flex gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900">Anomaly Detected</h3>
            <p className="text-sm mt-1">{record.anomaly_reason}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-white border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Normalized Data</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider">Date</label>
                <div className="mt-1 text-sm font-medium text-gray-900">{record.reporting_date}</div>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider">Activity Type</label>
                {isEditing ? (
                  <input 
                    type="text" 
                    value={editForm.activity_type} 
                    onChange={e => setEditForm({...editForm, activity_type: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-500 focus:border-brand-500 sm:text-sm px-3 py-2 border"
                  />
                ) : (
                  <div className="mt-1 text-sm font-medium text-gray-900">{record.activity_type}</div>
                )}
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</label>
                {isEditing ? (
                  <div className="flex items-center gap-2 mt-1">
                    <input 
                      type="number" 
                      value={editForm.normalized_quantity} 
                      onChange={e => setEditForm({...editForm, normalized_quantity: e.target.value})}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-500 focus:border-brand-500 sm:text-sm px-3 py-2 border"
                    />
                    <span className="text-sm font-medium text-gray-500">{record.normalized_unit}</span>
                  </div>
                ) : (
                  <div className="mt-1 text-sm font-medium text-gray-900">{parseFloat(record.normalized_quantity)} {record.normalized_unit}</div>
                )}
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider">Calculated Emissions</label>
                <div className="mt-1 text-sm font-medium text-green-600 bg-green-50 inline-block px-2 py-1 rounded">
                  {record.calculated_emissions_kg ? `${parseFloat(record.calculated_emissions_kg).toLocaleString()} kg CO2e` : 'Pending Factor'}
                </div>
              </div>
              
              {isEditing && (
                <div className="pt-4 flex justify-end">
                  <button onClick={handleSave} className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800">
                    Save Changes
                  </button>
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-white border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2 flex items-center gap-2">
              <History className="w-5 h-5 text-gray-400" /> Audit Trail
            </h2>
            <div className="space-y-4">
              {auditLogs.map((log, idx) => (
                <div key={idx} className="border-l-2 border-brand-200 pl-4 py-1">
                  <p className="text-xs text-gray-500">{new Date(log.timestamp).toLocaleString()} by {log.user_name || 'System'}</p>
                  <p className="text-sm font-medium text-gray-900 mt-1">{log.reason}</p>
                </div>
              ))}
              {auditLogs.length === 0 && <p className="text-sm text-gray-500 italic">No manual edits yet.</p>}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 border-b border-gray-200 pb-2">Original Raw Payload</h2>
            <pre className="text-xs bg-gray-900 text-gray-300 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(record.raw_data, null, 2)}
            </pre>
            <p className="text-xs text-gray-500 mt-4">This is the immutable payload ingested from the source file.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
