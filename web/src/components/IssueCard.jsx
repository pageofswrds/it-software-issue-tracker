// web/src/components/IssueCard.jsx
function IssueCard({ issue, onClick }) {
  const severityColors = {
    critical: '#f44336',
    major: '#ff9800',
    minor: '#666'
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  return (
    <div className="issue-card" onClick={onClick}>
      <div className="issue-header">
        <span
          className="severity-badge"
          style={{ backgroundColor: severityColors[issue.severity] }}
        >
          {issue.severity.toUpperCase()}
        </span>
        {issue.issue_type && (
          <span className="issue-type">{issue.issue_type}</span>
        )}
        <span className="issue-date">{formatDate(issue.source_date || issue.created_at)}</span>
      </div>
      <h4>{issue.title}</h4>
      <p className="issue-summary">{issue.summary}</p>
      <div className="issue-meta">
        <span>{issue.source_type}</span>
        <span>&uarr; {issue.upvotes}</span>
        <span>&#x1F4AC; {issue.comment_count}</span>
      </div>
    </div>
  );
}

export default IssueCard;
