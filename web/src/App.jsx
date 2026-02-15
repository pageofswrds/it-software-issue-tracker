// web/src/App.jsx
import { useState } from 'react';
import ApplicationList from './pages/ApplicationList';
import ApplicationDetail from './pages/ApplicationDetail';
import IssueDetail from './pages/IssueDetail';

function App() {
  const [selectedApp, setSelectedApp] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);

  const handleBack = () => {
    if (selectedIssue) {
      setSelectedIssue(null);
    } else {
      setSelectedApp(null);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>IT Issue Tracker</h1>
        {(selectedApp || selectedIssue) && (
          <button onClick={handleBack}>&larr; Back</button>
        )}
      </header>
      <main>
        {!selectedApp ? (
          <ApplicationList onSelectApp={setSelectedApp} />
        ) : !selectedIssue ? (
          <ApplicationDetail app={selectedApp} onSelectIssue={setSelectedIssue} />
        ) : (
          <IssueDetail issue={selectedIssue} />
        )}
      </main>
    </div>
  );
}

export default App;
