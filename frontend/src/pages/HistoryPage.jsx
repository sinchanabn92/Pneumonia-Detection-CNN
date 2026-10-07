import React, { useEffect, useState } from 'react';
import { History, FileText, Eye, Search, ArrowLeft, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react';
import { getHistory, getReportUrl } from '../api';

export default function HistoryPage({ setActiveTab, setSelectedAnalysis }) {
  const [data, setData] = useState({ total: 0, records: [] });
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = async (p = 1) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getHistory(p, pageSize);
      setData(res);
      setPage(p);
    } catch (err) {
      console.error(err);
      setError('Failed to load history records from database.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(page);
  }, [page]);

  const filteredRecords = data.records.filter((r) => {
    const term = searchTerm.toLowerCase();
    return (
      r.original_filename?.toLowerCase().includes(term) ||
      r.id?.toLowerCase().includes(term) ||
      r.prediction?.toLowerCase().includes(term) ||
      r.status?.toLowerCase().includes(term)
    );
  });

  const totalPages = Math.ceil(data.total / pageSize) || 1;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2">
            <History className="h-7 w-7 text-cyan-400" />
            Analysis Audit History
          </h1>
          <p className="text-sm text-slate-400">
            Real permanent database log of all evaluated chest radiographs. Total records: {data.total}
          </p>
        </div>

        {/* Search & Refresh */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search filename or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-56 sm:w-64"
            />
          </div>
          <button
            onClick={() => fetchHistory(page)}
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-600 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* History Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 overflow-hidden">
        {loading ? (
          <div className="py-16 text-center text-slate-500 text-sm">Loading audit history...</div>
        ) : filteredRecords.length === 0 ? (
          <div className="py-16 text-center space-y-2">
            <p className="text-sm font-semibold text-slate-300">No records found</p>
            <p className="text-xs text-slate-500">
              {searchTerm ? 'No analyses match your search criteria.' : 'No X-rays have been analyzed yet.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Analysis ID</th>
                  <th className="px-4 py-3.5">Date / Time</th>
                  <th className="px-4 py-3.5">Original File</th>
                  <th className="px-4 py-3.5">Prediction</th>
                  <th className="px-4 py-3.5">Confidence</th>
                  <th className="px-4 py-3.5">Uncertainty</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">{r.id.slice(0, 8)}...</td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 max-w-[180px] truncate text-slate-200" title={r.original_filename}>
                      {r.original_filename}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                        r.prediction === 'PNEUMONIA'
                          ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
                          : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                      }`}>
                        {r.prediction}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">{(r.confidence * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3 font-medium">{(r.uncertainty * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                        r.status === 'ACCEPTED'
                          ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/60'
                          : 'bg-amber-950/70 text-amber-300 border border-amber-800/60'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => {
                          setSelectedAnalysis(r);
                          setActiveTab('results');
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 cursor-pointer"
                      >
                        <Eye className="h-3 w-3" /> View
                      </button>
                      <a
                        href={getReportUrl(r.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-800 cursor-pointer"
                      >
                        <FileText className="h-3 w-3" /> PDF
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/40">
            <div className="text-xs text-slate-400">
              Page <span className="font-semibold text-white">{page}</span> of{' '}
              <span className="font-semibold text-white">{totalPages}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
