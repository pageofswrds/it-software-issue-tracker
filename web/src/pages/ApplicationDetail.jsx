// web/src/pages/ApplicationDetail.jsx
import { useState, useEffect } from 'react';
import IssueCard from '../components/IssueCard';

function ApplicationDetail({ app, onSelectIssue }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');

  useEffect(() => {
    setLoading(true);
    const url = severityFilter
      ? `/api/applications/${app.id}/issues?severity=${severityFilter}`
      : `/api/applications/${app.id}/issues`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        setIssues(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching issues:', err);
        setLoading(false);
      });
  }, [app.id, severityFilter]);

  return (
    <div className="application-detail">
      <div className="detail-header">
        <h2>{app.name}</h2>
        <p className="vendor">{app.vendor || 'Unknown vendor'}</p>
      </div>

      <div className="filters">
        <label>Filter by severity:</label>
        <select
          value={severityFilter}
          onChange={e => setSeverityFilter(e.target.value)}
        >
          <option value="">All</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading issues...</div>
      ) : issues.length === 0 ? (
        <div className="no-issues">No issues found. Run the crawler to populate data.</div>
      ) : (
        <div className="issues-list">
          {issues.map(issue => (
            <IssueCard
              key={issue.id}
              issue={issue}
              onClick={() => onSelectIssue(issue)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default ApplicationDetail;
