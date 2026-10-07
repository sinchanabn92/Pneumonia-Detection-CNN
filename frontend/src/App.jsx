import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import AnalyzePage from './pages/AnalyzePage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import ModelReliability from './pages/ModelReliability';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard
            setActiveTab={setActiveTab}
            setSelectedAnalysis={setSelectedAnalysis}
          />
        );
      case 'analyze':
        return (
          <AnalyzePage
            setActiveTab={setActiveTab}
            setSelectedAnalysis={setSelectedAnalysis}
          />
        );
      case 'results':
        return (
          <ResultsPage
            analysis={selectedAnalysis}
            setActiveTab={setActiveTab}
          />
        );
      case 'history':
        return (
          <HistoryPage
            setActiveTab={setActiveTab}
            setSelectedAnalysis={setSelectedAnalysis}
          />
        );
      case 'model':
        return <ModelReliability />;
      default:
        return (
          <Dashboard
            setActiveTab={setActiveTab}
            setSelectedAnalysis={setSelectedAnalysis}
          />
        );
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/20 selection:text-cyan-300">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>
      <Footer />
    </div>
  );
}
