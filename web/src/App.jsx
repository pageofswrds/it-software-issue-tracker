// web/src/App.jsx
import { useState, useCallback } from 'react';
import ApplicationList from './pages/ApplicationList';
import ApplicationDetail from './pages/ApplicationDetail';
import IssueDetail from './pages/IssueDetail';
import AddApplicationModal from './components/AddApplicationModal';
import ReportIssueModal from './components/ReportIssueModal';

function App() {
  const [selectedApp, setSelectedApp] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [showAddApp, setShowAddApp] = useState(false);
  const [showReportIssue, setShowReportIssue] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleBack = () => {
    if (selectedIssue) {
      setSelectedIssue(null);
    } else {
      setSelectedApp(null);
    }
  };

  const handleCreated = useCallback(() => {
    setRefreshKey(k => k + 1);
  }, []);

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
            + New Request
          </button>
          <button className="btn-header btn-manual-entry" onClick={() => setShowReportIssue(true)}>
            + Manual Entry
          </button>
        </div>
      </header>
      <main>
        {!selectedApp ? (
          <ApplicationList key={refreshKey} onSelectApp={setSelectedApp} />
        ) : !selectedIssue ? (
          <ApplicationDetail app={selectedApp} onSelectIssue={setSelectedIssue} />
        ) : (
          <IssueDetail issue={selectedIssue} />
        )}
      </main>

      {showAddApp && (
        <AddApplicationModal
          onClose={() => setShowAddApp(false)}
          onCreated={handleCreated}
        />
      )}
      {showReportIssue && (
        <ReportIssueModal
          onClose={() => setShowReportIssue(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}

export default App;
