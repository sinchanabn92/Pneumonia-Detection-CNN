import React from 'react';
import { Download, FileText, ArrowLeft, CheckCircle2, AlertTriangle, ShieldAlert, Sparkles, Layers, RefreshCw } from 'lucide-react';
import { getAssetUrl, getReportUrl } from '../api';

export default function ResultsPage({ analysis, setActiveTab }) {
  if (!analysis) {
    return (
      <div className="py-20 text-center space-y-4">
        <AlertTriangle className="h-12 w-12 text-slate-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">No Analysis Selected</h2>
        <p className="text-sm text-slate-400">Please upload a chest X-ray to generate and view diagnostic results.</p>
        <button
          onClick={() => setActiveTab('analyze')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-colors"
        >
          Go to Upload
        </button>
      </div>
    );
  }

  const isPneumonia = analysis.prediction === 'PNEUMONIA';
  const isAccepted = analysis.status === 'ACCEPTED';
  const pneumoniaPct = (analysis.pneumonia_probability * 100).toFixed(1);
  const normalPct = (analysis.normal_probability * 100).toFixed(1);
  const confidencePct = (analysis.confidence * 100).toFixed(1);
  const uncertaintyPct = (analysis.uncertainty * 100).toFixed(1);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Analysis Results</h1>
            <span className="font-mono text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
              ID: {analysis.analysis_id || analysis.id}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Timestamp: {new Date(analysis.created_at).toLocaleString()} &bull; DenseNet121 Calibrated Inference
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setActiveTab('analyze')}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Analyze Another
          </button>
          <a
            href={getReportUrl(analysis.analysis_id || analysis.id)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-colors cursor-pointer"
          >
            <FileText className="h-3.5 w-3.5" />
            Download PDF Report
          </a>
        </div>
      </div>

      {/* Primary Result Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Prediction Card */}
        <div className={`rounded-2xl border p-6 space-y-3 ${
          isPneumonia
            ? 'border-rose-800/80 bg-rose-950/20'
            : 'border-emerald-800/80 bg-emerald-950/20'
        }`}>
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Model Prediction</div>
          <div className="flex items-center gap-3">
            <span className={`text-3xl font-extrabold ${isPneumonia ? 'text-rose-400' : 'text-emerald-400'}`}>
              {analysis.prediction}
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Pneumonia Probability: <span className="font-semibold text-white">{pneumoniaPct}%</span> &bull; Decision Threshold: <span className="text-cyan-400 font-semibold">{analysis.decision_threshold}</span>
          </p>
        </div>

        {/* Validation Status Card (Task 45) */}
        <div className={`rounded-2xl border p-6 space-y-3 ${
          isAccepted
            ? 'border-emerald-800/60 bg-slate-900/60'
            : 'border-amber-800/60 bg-amber-950/20'
        }`}>
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Decision Reliability Status</div>
          <div className="flex items-center gap-2.5">
            {isAccepted ? (
              <CheckCircle2 className="h-6 w-6 text-emerald-400" />
            ) : (
              <AlertTriangle className="h-6 w-6 text-amber-400" />
            )}
            <span className={`text-2xl font-bold ${isAccepted ? 'text-emerald-400' : 'text-amber-400'}`}>
              {analysis.status}
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {isAccepted
              ? 'Uncertainty is within the calibrated abstention tolerance (≤ 0.10).'
              : 'Confidence is below threshold (Uncertainty > 0.10). Clinical expert review is strongly recommended.'}
          </p>
        </div>

        {/* Confidence & Uncertainty Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Confidence &amp; Uncertainty</div>
          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-2xl font-bold text-white">{confidencePct}%</div>
              <div className="text-[11px] text-slate-400">Confidence P(ŷ)</div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-slate-300">{uncertaintyPct}%</div>
              <div className="text-[11px] text-slate-400">Uncertainty (1 - Conf)</div>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            Temperature Scaled: T = {analysis.temperature?.toFixed(4) || '1.0726'}
          </div>
        </div>
      </div>

      {/* Calibrated Probability Breakdown Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
          <span>NORMAL PROBABILITY: {normalPct}%</span>
          <span>PNEUMONIA PROBABILITY: {pneumoniaPct}%</span>
        </div>

        <div className="relative w-full h-4 bg-slate-800 rounded-full overflow-hidden flex">
          <div
            style={{ width: `${normalPct}%` }}
            className="h-full bg-emerald-500 transition-all duration-500"
            title={`Normal: ${normalPct}%`}
          />
          <div
            style={{ width: `${pneumoniaPct}%` }}
            className="h-full bg-rose-500 transition-all duration-500"
            title={`Pneumonia: ${pneumoniaPct}%`}
          />
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-500">
          <span>0.0 (Normal)</span>
          <span className="text-cyan-400 font-medium">Selected Decision Threshold: 0.16 (16%)</span>
          <span>1.0 (Pneumonia)</span>
        </div>
      </div>

      {/* Dual Image Comparison: Original vs Grad-CAM (Task 22 & 44) */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-cyan-400" />
              Grad-CAM Explainability (DenseBlock4)
            </h2>
            <p className="text-xs text-slate-400">
              Visual interpretability showing image regions that contributed to the model prediction.
            </p>
          </div>
          <a
            href={getAssetUrl(analysis.gradcam_url)}
            download={`gradcam_${analysis.analysis_id || analysis.id}.png`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 self-start sm:self-auto cursor-pointer"
          >
            <Download className="h-3.5 w-3.5" /> Download Overlay
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Original Radiograph */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-300">Original Radiograph</div>
            <div className="rounded-xl overflow-hidden border border-slate-800 bg-black aspect-square flex items-center justify-center">
              <img
                src={getAssetUrl(analysis.original_image_url)}
                alt="Original Chest Radiograph"
                className="w-full h-full object-contain"
              />
            </div>
            <p className="text-[11px] text-slate-500 text-center">Input image normalized to 224&times;224 ImageNet standards</p>
          </div>

          {/* Grad-CAM Heatmap Overlay */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-300">Grad-CAM Activation Overlay</div>
            <div className="rounded-xl overflow-hidden border border-slate-800 bg-black aspect-square flex items-center justify-center">
              <img
                src={getAssetUrl(analysis.gradcam_url)}
                alt="Grad-CAM Activation Overlay"
                className="w-full h-full object-contain"
              />
            </div>
            <p className="text-[11px] text-slate-500 text-center">DenseNet121 features.denseblock4 feature-map gradients</p>
          </div>
        </div>

        {/* Explainability Callout (Task 23) */}
        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 text-xs text-slate-400 leading-relaxed">
          <span className="font-semibold text-slate-300">Interpretability Note:</span>{' '}
          This Grad-CAM visualization is an interpretability tool illustrating which regions of the input radiograph
          contributed most heavily to the model's classification score. It does not provide medical disease localization,
          does not prove pathology, and is not a substitute for radiologist interpretation.
        </div>
      </div>
    </div>
  );
}
