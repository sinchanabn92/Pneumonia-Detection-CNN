import React, { useEffect, useState } from 'react';
import { Activity, UploadCloud, CheckCircle2, AlertTriangle, ArrowRight, FileText, Clock, Layers, ShieldCheck, Eye } from 'lucide-react';
import { getHealth, getModelInfo, getHistory, getReportUrl } from '../api';

export default function Dashboard({ setActiveTab, setSelectedAnalysis }) {
  const [health, setHealth] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [history, setHistory] = useState({ total: 0, records: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hData, mData, histData] = await Promise.all([
          getHealth().catch(() => null),
          getModelInfo().catch(() => null),
          getHistory(1, 5).catch(() => ({ total: 0, records: [] }))
        ]);
        setHealth(hData);
        setModelInfo(mData);
        setHistory(histData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 p-8">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
            <Layers className="h-3.5 w-3.5" />
            DenseNet121 Architecture &bull; Calibrated Decision Support
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Chest X-Ray Pneumonia Detection & Explainability
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            A research prototype integrating temperature-scaled probability calibration, sensitivity-optimized decision thresholding (0.16), uncertainty-based abstention (0.10), and DenseBlock4 Grad-CAM visual interpretability.
          </p>
          <div className="pt-2 flex flex-wrap gap-4">
            <button
              onClick={() => setActiveTab('analyze')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
            >
              <UploadCloud className="h-4 w-4" />
              Analyze New Chest X-Ray
            </button>
            <button
              onClick={() => setActiveTab('model')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer"
            >
              <ShieldCheck className="h-4 w-4" />
              View Model Verification Specs
            </button>
          </div>
        </div>
      </div>

      {/* Metrics & System Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>MODEL STATUS</span>
            <Activity className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {health?.model_loaded ? 'Online' : 'Standby'}
          </div>
          <div className="text-xs text-slate-400">
            {health?.model_loaded ? `Loaded on ${health.device}` : 'Awaiting Checkpoint'}
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>DECISION THRESHOLD</span>
            <CheckCircle2 className="h-4 w-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {modelInfo ? modelInfo.decision_threshold : '0.16'}
          </div>
          <div className="text-xs text-slate-400">
            Sensitivity: 98.16% (Specificity &ge; 95%)
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>TEMPERATURE (T)</span>
            <Layers className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {modelInfo ? modelInfo.temperature.toFixed(4) : '1.0726'}
          </div>
          <div className="text-xs text-slate-400">
            Calibrated Softmax ECE: 0.0036
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>TOTAL ANALYSES</span>
            <Clock className="h-4 w-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {history.total}
          </div>
          <div className="text-xs text-slate-400">
            Recorded in local audit database
          </div>
        </div>
      </div>

      {/* Recent Analyses Section */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Recent Analyses</h2>
            <p className="text-xs text-slate-400">Audit trail of recently evaluated chest X-rays</p>
          </div>
          {history.total > 0 && (
            <button
              onClick={() => setActiveTab('history')}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
            >
              View all {history.total} records <ArrowRight className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-500 text-sm">Loading recent records...</div>
        ) : history.records.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <FileText className="h-10 w-10 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400 font-medium">No analyses available yet.</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Upload a chest X-ray image in the Analyze tab to generate real inference and Grad-CAM explainability.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Analysis ID</th>
                  <th className="px-4 py-3">Original File</th>
                  <th className="px-4 py-3">Prediction</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Uncertainty</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {history.records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">{r.id.slice(0, 8)}...</td>
                    <td className="px-4 py-3 max-w-[160px] truncate" title={r.original_filename}>{r.original_filename}</td>
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
      </div>
    </div>
  );
}
