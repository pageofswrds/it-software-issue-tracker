// web/src/pages/IssueDetail.jsx
function IssueDetail({ issue }) {
  const severityColors = {
    critical: '#f44336',
    major: '#ff9800',
    minor: '#666'
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="issue-detail">
      <div className="issue-detail-header">
        <span
          className="severity-badge large"
          style={{ backgroundColor: severityColors[issue.severity] }}
        >
          {issue.severity.toUpperCase()}
        </span>
        <h2>{issue.title}</h2>
      </div>

      <div className="issue-detail-meta">
        <div className="meta-item">
          <label>Source</label>
          <span>{issue.source_type}</span>
        </div>
        <div className="meta-item">
          <label>Type</label>
          <span>{issue.issue_type || 'Unknown'}</span>
        </div>
        <div className="meta-item">
          <label>Reported</label>
          <span>{formatDate(issue.source_date)}</span>
        </div>
        <div className="meta-item">
          <label>Engagement</label>
          <span>{'\u2191'} {issue.upvotes} {'\u00B7'} {'\uD83D\uDCAC'} {issue.comment_count}</span>
        </div>
      </div>

      <div className="issue-section">
        <h3>Summary</h3>
        <p>{issue.summary}</p>
      </div>

      <div className="issue-section">
        <a
          href={issue.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="source-link"
        >
          View Original Source {'\u2197'}
        </a>
      </div>

      {issue.raw_content && (
        <details className="raw-content">
          <summary>Show Raw Content</summary>
          <pre>{issue.raw_content}</pre>
        </details>
      )}
    </div>
  );
}

export default IssueDetail;
