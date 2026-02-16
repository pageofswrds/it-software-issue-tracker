// web/src/App.jsx
import { useState, useEffect } from 'react';
import ApplicationList from './pages/ApplicationList';
import ApplicationDetail from './pages/ApplicationDetail';
import IssueDetail from './pages/IssueDetail';
import AddApplicationModal from './components/AddApplicationModal';
import ReportIssueModal from './components/ReportIssueModal';

const DEMO_MODE = true;

function App() {
  const [selectedApp, setSelectedApp] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [showAddApp, setShowAddApp] = useState(false);
  const [showReportIssue, setShowReportIssue] = useState(false);
  const [demoToast, setDemoToast] = useState(null);

  const handleBack = () => {
    if (selectedIssue) {
      setSelectedIssue(null);
    } else {
      setSelectedApp(null);
    }
  };

  useEffect(() => {
    if (demoToast) {
      const timer = setTimeout(() => setDemoToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [demoToast]);

  return (
    <div className="app">
      <header>
        <div className="header-left">
          {(selectedApp || selectedIssue) && (
            <button onClick={handleBack}>&larr; Back</button>
          )}
          <h1>Enterprise IT Patch Crowdsourcer</h1>
        </div>
        <div className="header-right">
          <button className="btn-header btn-new-request" onClick={() => setShowAddApp(true)}>
            + New Application
          </button>
          <button className="btn-header btn-manual-entry" onClick={() => setShowReportIssue(true)}>
            + Manual Entry
          </button>
        </div>
      </header>

      {demoToast && (
        <div className="demo-toast">
          {demoToast}
        </div>
      )}

      <main>
        {!selectedApp ? (
          <ApplicationList onSelectApp={setSelectedApp} />
        ) : !selectedIssue ? (
          <ApplicationDetail app={selectedApp} onSelectIssue={setSelectedIssue} />
        ) : (
          <IssueDetail issue={selectedIssue} />
        )}
      </main>

      {showAddApp && (
        <AddApplicationModal
          demoMode={DEMO_MODE}
          onClose={() => setShowAddApp(false)}
          onDemoSubmit={() => {
            setShowAddApp(false);
            setDemoToast('Submissions are disabled in demo mode.');
          }}
        />
      )}
      {showReportIssue && (
        <ReportIssueModal
          demoMode={DEMO_MODE}
          onClose={() => setShowReportIssue(false)}
          onDemoSubmit={() => {
            setShowReportIssue(false);
            setDemoToast('Submissions are disabled in demo mode.');
          }}
        />
      )}
    </div>
  );
}

export default App;
