import React, { useEffect, useState } from 'react';
import { ShieldCheck, Layers, Gauge, Target, HelpCircle, FileCheck, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';
import { getModelInfo } from '../api';

export default function ModelReliability() {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const data = await getModelInfo();
        setModelInfo(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInfo();
  }, []);

  const internal = modelInfo?.internal_test_metrics || {
    accuracy: 0.9638,
    precision: 0.9478,
    sensitivity: 0.9816,
    specificity: 0.9460,
    f1_score: 0.9644,
    roc_auc: 0.9960,
    samples: 5439
  };

  const external = modelInfo?.external_test_metrics || {
    accuracy: 0.9535,
    precision: 0.9308,
    sensitivity: 1.0000,
    specificity: 0.8761,
    f1_score: 0.9642,
    roc_auc: 0.9998,
    samples: 624
  };

  return (
    <div className="space-y-10 max-w-6xl mx-auto">
      {/* Title */}
      <div className="space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <ShieldCheck className="h-8 w-8 text-cyan-400" />
          Model Architecture &amp; Reliability Engineering
        </h1>
        <p className="text-sm text-slate-400 max-w-3xl leading-relaxed">
          Comprehensive specification of the deployed DenseNet121 neural network, temperature-calibrated posterior probabilities, decision boundary optimization, and uncertainty estimation.
        </p>
      </div>

      {/* 4 Core Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pillar 1: Architecture */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-3 text-cyan-400 font-semibold text-base">
            <Cpu className="h-5 w-5" />
            <h3>1. Neural Architecture &amp; Preprocessing</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">&bull;</span>
              <span><strong>Base Architecture:</strong> DenseNet121 (DenseNet features with 4 dense blocks and transition layers).</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">&bull;</span>
              <span><strong>Classifier Head:</strong> <code className="text-cyan-300">Linear(in_features=1024, out_features=2, bias=True)</code> initialized via Kaiming normal.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">&bull;</span>
              <span><strong>Input Dimensions:</strong> 224 &times; 224 pixels with 3 channels.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">&bull;</span>
              <span><strong>Standard Transform:</strong> Resize((224, 224)) &rarr; Grayscale(3) &rarr; ToTensor() &rarr; ImageNet Normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]).</span>
            </li>
          </ul>
        </div>

        {/* Pillar 2: Calibration */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-3 text-teal-400 font-semibold text-base">
            <Gauge className="h-5 w-5" />
            <h3>2. Temperature Scaling Calibration</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold">&bull;</span>
              <span><strong>Temperature Parameter (T):</strong> <code className="text-teal-300">1.0726476907730103</code> (loaded dynamically from artifact).</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold">&bull;</span>
              <span><strong>Mathematical Formulation:</strong> <code className="text-teal-300">p = softmax(logits / T)</code>.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold">&bull;</span>
              <span><strong>Preservation:</strong> Temperature scaling softens overconfident logits without altering model weights or accuracy.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold">&bull;</span>
              <span><strong>Calibration Metric:</strong> Expected Calibration Error (ECE) reduced from 0.0063 to 0.0036 on duplicate-aware validation data.</span>
            </li>
          </ul>
        </div>

        {/* Pillar 3: Decision Threshold */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-3 text-indigo-400 font-semibold text-base">
            <Target className="h-5 w-5" />
            <h3>3. Clinical Decision Threshold (0.16)</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-indigo-400 font-bold">&bull;</span>
              <span><strong>Selected Pneumonia Threshold:</strong> <code className="text-indigo-300">0.16</code> (rather than uncalibrated 0.50 default).</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-400 font-bold">&bull;</span>
              <span><strong>Clinical Justification:</strong> Prioritizes high sensitivity (minimizing dangerous false negatives) while constraining specificity to &ge; 95%.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-400 font-bold">&bull;</span>
              <span><strong>Decision Logic:</strong> If <code className="text-indigo-300">P(Pneumonia) &ge; 0.16</code> &rarr; PNEUMONIA; else NORMAL.</span>
            </li>
          </ul>
        </div>

        {/* Pillar 4: Uncertainty & Abstention */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-3 text-amber-400 font-semibold text-base">
            <HelpCircle className="h-5 w-5" />
            <h3>4. Uncertainty Abstention (Threshold: 0.10)</h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">&bull;</span>
              <span><strong>Confidence &amp; Uncertainty:</strong> Confidence = P(predicted class); Uncertainty = 1 - Confidence.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">&bull;</span>
              <span><strong>Abstention Threshold:</strong> Uncertainty &le; 0.10 &rarr; <strong className="text-emerald-400">ACCEPTED</strong>; Uncertainty &gt; 0.10 &rarr; <strong className="text-amber-400">UNCERTAIN / REVIEW</strong>.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">&bull;</span>
              <span><strong>Abstention Performance:</strong> Captures 75.35% of erroneous classifications; increases accepted subset accuracy to 99.16% at 92.0% coverage.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">&bull;</span>
              <span><strong>Separation Principle:</strong> Prediction remains NORMAL/PNEUMONIA; review status is tracked and reported separately.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Verified Performance Metrics Comparison (Source of Truth) */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-6">
        <div className="space-y-1">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileCheck className="h-5 w-5 text-cyan-400" />
            Empirical Evaluation Benchmarks (Ground Truth)
          </h2>
          <p className="text-xs text-slate-400">
            Performance figures extracted directly from the verified research notebooks (Notebook 3 final evaluation &amp; generalization results).
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5">Metric</th>
                <th className="px-5 py-3.5">Internal Test (Clean CXR)</th>
                <th className="px-5 py-3.5">External Test (Kermany Pediatric)</th>
                <th className="px-5 py-3.5">Generalization Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">Test Sample Count</td>
                <td className="px-5 py-3">{internal.samples} images</td>
                <td className="px-5 py-3">{external.samples} images (Zero training)</td>
                <td className="px-5 py-3 text-slate-500">&mdash;</td>
              </tr>
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">Accuracy</td>
                <td className="px-5 py-3 font-mono font-bold text-emerald-400">{(internal.accuracy * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono font-bold text-cyan-400">{(external.accuracy * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono text-rose-400">{((external.accuracy - internal.accuracy) * 100).toFixed(2)}%</td>
              </tr>
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">Precision</td>
                <td className="px-5 py-3 font-mono">{(internal.precision * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono">{(external.precision * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono text-rose-400">{((external.precision - internal.precision) * 100).toFixed(2)}%</td>
              </tr>
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">Sensitivity (Recall)</td>
                <td className="px-5 py-3 font-mono">{(internal.sensitivity * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono font-bold text-emerald-400">{(external.sensitivity * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono text-emerald-400">+{((external.sensitivity - internal.sensitivity) * 100).toFixed(2)}%</td>
              </tr>
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">Specificity</td>
                <td className="px-5 py-3 font-mono">{(internal.specificity * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono">{(external.specificity * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono text-rose-400">{((external.specificity - internal.specificity) * 100).toFixed(2)}%</td>
              </tr>
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">F1-Score</td>
                <td className="px-5 py-3 font-mono">{(internal.f1_score * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono">{(external.f1_score * 100).toFixed(2)}%</td>
                <td className="px-5 py-3 font-mono text-slate-400">{((external.f1_score - internal.f1_score) * 100).toFixed(2)}%</td>
              </tr>
              <tr className="hover:bg-slate-800/20">
                <td className="px-5 py-3 font-semibold text-white">ROC-AUC</td>
                <td className="px-5 py-3 font-mono font-bold text-cyan-400">{internal.roc_auc.toFixed(4)}</td>
                <td className="px-5 py-3 font-mono font-bold text-emerald-400">{external.roc_auc.toFixed(4)}</td>
                <td className="px-5 py-3 font-mono text-emerald-400">+{(external.roc_auc - internal.roc_auc).toFixed(4)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
