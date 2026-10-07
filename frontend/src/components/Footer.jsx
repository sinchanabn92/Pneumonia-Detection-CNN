import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 mb-4">
          <div className="flex items-start gap-3">
            <ShieldAlert className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-200/90 leading-relaxed">
              <span className="font-semibold text-amber-300">Mandatory Research Disclaimer:</span>{' '}
              This application is a research prototype for educational and experimental purposes. It is not a medical
              diagnostic device and must not be used as a substitute for evaluation by a qualified healthcare professional.
              Grad-CAM visualizations indicate feature activations in DenseBlock4 and do not constitute pathological proof of disease.
            </div>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            Pneumonia-AI-System &bull; Trained DenseNet121 Architecture &bull; Calibrated Inference Engine
          </div>
          <div>
            Strict Research Protocol &bull; No Training At Runtime
          </div>
        </div>
      </div>
    </footer>
  );
}
