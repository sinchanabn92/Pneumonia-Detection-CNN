import React, { useEffect, useState } from 'react';
import { Activity, ShieldAlert, Cpu, CheckCircle2, AlertTriangle, FileText, History, BarChart3, UploadCloud } from 'lucide-react';
import { getHealth } from '../api';

export default function Navbar({ activeTab, setActiveTab }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await getHealth();
        setHealth(data);
      } catch (err) {
        setHealth({ status: 'offline', model_loaded: false, message: 'Backend unreachable' });
      } finally {
        setLoading(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'analyze', label: 'Analyze X-Ray', icon: UploadCloud },
    { id: 'history', label: 'Audit History', icon: History },
    { id: 'model', label: 'Model & Reliability', icon: BarChart3 },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white">Pneumonia<span className="text-cyan-400">AI</span></span>
                <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-cyan-400 border border-slate-700">RESEARCH</span>
              </div>
              <p className="text-xs text-slate-400">DenseNet121 &bull; Calibrated Decision System</p>
            </div>
          </div>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-cyan-400 shadow-sm border border-slate-700/60'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* System Status Pill */}
          <div className="flex items-center gap-2">
            {loading ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400 animate-pulse">
                <span className="h-2 w-2 rounded-full bg-slate-500"></span> Connecting...
              </span>
            ) : health?.model_loaded ? (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950/70 text-emerald-400 border border-emerald-800/80">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>Model Online ({health.device})</span>
              </div>
            ) : (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-950/70 text-amber-300 border border-amber-800/80" title={health?.message}>
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>Model Standby</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
