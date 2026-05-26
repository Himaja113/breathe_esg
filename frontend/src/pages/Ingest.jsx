import React, { useState } from 'react';
import { UploadCloud, FileType, CheckCircle2 } from 'lucide-react';
import api from '../api';

export default function Ingest() {
  const [sourceType, setSourceType] = useState('SAP');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const sources = [
    { id: 'SAP', name: 'SAP (Fuel & Procurement)', desc: 'Tab-delimited .txt (MANDT, WERKS, MENGE, etc.)' },
    { id: 'UTILITY', name: 'Utility Data', desc: 'CSV format (account, meter, kWh, dates)' },
    { id: 'TRAVEL', name: 'Corporate Travel', desc: 'CSV format (flights, hotels, transport)' },
  ];

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post(`ingest/${sourceType.toLowerCase()}/`, formData);
      setResult(res.data);
    } catch (err) {
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Ingest Data</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {sources.map(source => (
          <button
            key={source.id}
            onClick={() => setSourceType(source.id)}
            className={`p-4 rounded-xl border text-left transition-colors ${
              sourceType === source.id ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-500' : 'border-gray-200 bg-white hover:border-brand-300'
            }`}
          >
            <FileType className={`w-6 h-6 mb-2 ${sourceType === source.id ? 'text-brand-600' : 'text-gray-400'}`} />
            <h3 className="font-semibold text-gray-900">{source.name}</h3>
            <p className="text-xs text-gray-500 mt-1">{source.desc}</p>
          </button>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
        {!result ? (
          <form onSubmit={handleUpload} className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 hover:bg-gray-50 transition-colors relative">
              <input 
                type="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                onChange={(e) => setFile(e.target.files[0])}
                accept=".csv,.txt"
              />
              <UploadCloud className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 font-medium">
                {file ? file.name : 'Click or drag file to this area to upload'}
              </p>
              <p className="text-sm text-gray-500 mt-1">Supports CSV, TXT</p>
            </div>
            
            <button 
              type="submit" 
              disabled={!file || uploading}
              className="bg-brand-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors w-full sm:w-auto"
            >
              {uploading ? 'Processing...' : 'Upload and Process'}
            </button>
          </form>
        ) : (
          <div className="py-8">
            <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Completed!</h2>
            <p className="text-gray-600 mb-6">Job ID: {result.id} is now processing in the background.</p>
            <button 
              onClick={() => {setResult(null); setFile(null);}}
              className="text-brand-600 font-medium hover:text-brand-700"
            >
              Upload another file
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
