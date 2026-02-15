// web/src/pages/ApplicationList.jsx
import { useState, useEffect } from 'react';
import ApplicationCard from '../components/ApplicationCard';

function ApplicationList({ onSelectApp }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/applications')
      .then(res => res.json())
      .then(data => {
        setApplications(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="application-list">
      <h2>Monitored Applications</h2>
      <div className="app-grid">
        {applications.map(app => (
          <ApplicationCard
            key={app.id}
            app={app}
            onClick={() => onSelectApp(app)}
          />
        ))}
      </div>
    </div>
  );
}

export default ApplicationList;
