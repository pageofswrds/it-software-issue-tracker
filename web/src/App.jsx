// web/src/App.jsx
import { useState } from 'react';
import ApplicationList from './pages/ApplicationList';

function App() {
  const [selectedApp, setSelectedApp] = useState(null);

  return (
    <div className="app">
      <header>
        <h1>IT Issue Tracker</h1>
        {selectedApp && (
          <button onClick={() => setSelectedApp(null)}>&larr; Back</button>
        )}
      </header>
      <main>
        {!selectedApp ? (
          <ApplicationList onSelectApp={setSelectedApp} />
        ) : (
          <div>Application detail coming soon: {selectedApp.name}</div>
        )}
      </main>
    </div>
  );
}

export default App;
