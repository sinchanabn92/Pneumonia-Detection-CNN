import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, AlertCircle, FileCheck, Loader2, ArrowRight } from 'lucide-react';
import { predictXray } from '../api';

export default function AnalyzePage({ setActiveTab, setSelectedAnalysis }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  const maxSizeBytes = 10 * 1024 * 1024; // 10MB

  const handleFile = (file) => {
    setError(null);
    if (!file) return;

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(jpe?g|png)$/i)) {
      setError('Please select a valid image file (.jpg, .jpeg, or .png).');
      return;
    }

    if (file.size > maxSizeBytes) {
      setError('File size exceeds the 10 MB limit.');
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select an X-ray image to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await predictXray(selectedFile);
      setSelectedAnalysis(result);
      setActiveTab('results');
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || err.message || 'Analysis failed. Please ensure the backend is running.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Upload Chest X-Ray</h1>
        <p className="text-sm text-slate-400">
          Upload a frontal chest radiograph (CXR) for evaluation by the trained DenseNet121 model.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 flex items-start gap-3 text-rose-300 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0 text-rose-400 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold">Analysis Error</span>
            <p className="text-xs text-rose-200/90 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {/* Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
          isDragging
            ? 'border-cyan-400 bg-cyan-950/20'
            : previewUrl
            ? 'border-slate-700 bg-slate-900/40 hover:border-slate-600'
            : 'border-slate-800 bg-slate-900/30 hover:border-cyan-500/60 hover:bg-slate-900/50'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFile(e.target.files?.[0])}
          accept=".jpg,.jpeg,.png,image/jpeg,image/png"
          className="hidden"
        />

        {previewUrl ? (
          <div className="space-y-4">
            <div className="relative inline-block mx-auto rounded-xl overflow-hidden border border-slate-700 shadow-2xl bg-black">
              <img
                src={previewUrl}
                alt="Selected Chest X-Ray Preview"
                className="max-h-80 max-w-full object-contain mx-auto"
              />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-semibold text-white flex items-center justify-center gap-2">
                <FileCheck className="h-4 w-4 text-emerald-400" />
                {selectedFile?.name}
              </p>
              <p className="text-xs text-slate-400">
                {(selectedFile?.size / 1024).toFixed(1)} KB &bull; Click or drop another image to replace
              </p>
            </div>
          </div>
        ) : (
          <div className="py-12 space-y-4">
            <div className="h-16 w-16 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto text-cyan-400">
              <UploadCloud className="h-8 w-8" />
            </div>
            <div className="space-y-1">
              <p className="text-base font-semibold text-white">
                Drag and drop your Chest X-Ray here, or <span className="text-cyan-400 underline">browse</span>
              </p>
              <p className="text-xs text-slate-500">
                Supports JPG, JPEG, and PNG formats up to 10 MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Action Bar */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-xs text-slate-500">
          Preprocessing: Resize (224&times;224) &bull; Grayscale &bull; 3 Channels &bull; ImageNet Normalization
        </div>
        <button
          onClick={handleAnalyze}
          disabled={!selectedFile || loading}
          className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
            !selectedFile || loading
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 hover:opacity-95 shadow-lg shadow-cyan-500/20'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
              Running Inference &amp; Grad-CAM...
            </>
          ) : (
            <>
              Analyze Radiograph
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
