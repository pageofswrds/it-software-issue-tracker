// web/src/components/ApplicationCard.jsx
function ApplicationCard({ app, onClick }) {
  const totalIssues = app.critical_count + app.major_count + app.minor_count;

  let statusIcon = '\u2713';
  let statusClass = 'status-ok';

  if (app.critical_count > 0) {
    statusIcon = '\uD83D\uDD34';
    statusClass = 'status-critical';
  } else if (app.major_count > 0) {
    statusIcon = '\u26A0\uFE0F';
    statusClass = 'status-major';
  }

  return (
    <div className={`app-card ${statusClass}`} onClick={onClick}>
      <div className="app-card-header">
        <span className="status-icon">{statusIcon}</span>
        <h3>{app.name}</h3>
      </div>
      <p className="vendor">{app.vendor || 'Unknown vendor'}</p>
      <div className="issue-counts">
        <span className="critical">{app.critical_count} critical</span>
        <span className="major">{app.major_count} major</span>
        <span className="minor">{app.minor_count} minor</span>
      </div>
    </div>
  );
}

export default ApplicationCard;
