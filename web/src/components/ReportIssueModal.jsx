// web/src/components/ReportIssueModal.jsx
import { useState, useEffect } from 'react';

function ReportIssueModal({ onClose, onCreated }) {
  const [applications, setApplications] = useState([]);
  const [applicationId, setApplicationId] = useState('');
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [severity, setSeverity] = useState('');
  const [issueType, setIssueType] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/applications')
      .then(res => res.json())
      .then(data => setApplications(data))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch('/api/issues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          application_id: applicationId,
          title,
          summary,
          severity,
          issue_type: issueType || undefined,
          source_url: sourceUrl || undefined,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to report issue');
      }

      onCreated();
      onClose();
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Manual Entry</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <p className="modal-description">
          Manually report a bug or issue you've experienced.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="issue-app">Application *</label>
            <select
              id="issue-app"
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
              required
            >
              <option value="">Select an application</option>
              {applications.map(app => (
                <option key={app.id} value={app.id}>{app.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="issue-title">Title *</label>
            <input
              id="issue-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Brief description of the issue"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="issue-summary">Summary *</label>
            <textarea
              id="issue-summary"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="Detailed description of the bug or issue experienced..."
              rows={4}
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="issue-severity">Severity *</label>
              <select
                id="issue-severity"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                required
              >
                <option value="">Select severity</option>
                <option value="critical">Critical</option>
                <option value="major">Major</option>
                <option value="minor">Minor</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="issue-type">Issue Type</label>
              <select
                id="issue-type"
                value={issueType}
                onChange={(e) => setIssueType(e.target.value)}
              >
                <option value="">Select type</option>
                <option value="crash">Crash</option>
                <option value="performance">Performance</option>
                <option value="install">Install</option>
                <option value="security">Security</option>
                <option value="compatibility">Compatibility</option>
                <option value="ui">UI</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="issue-url">Source URL</label>
            <input
              id="issue-url"
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://..."
            />
            <span className="form-hint">Optional link to the original report or documentation.</span>
          </div>
          {error && <div className="form-error">{error}</div>}
          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Report Issue'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ReportIssueModal;
