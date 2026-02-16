// web/src/pages/ApplicationDetail.jsx
import { useState, useEffect, useRef } from 'react';
import IssueCard from '../components/IssueCard';

function ApplicationDetail({ app, onSelectIssue }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState({});
  const sectionRefs = useRef({});

  useEffect(() => {
    setLoading(true);
    fetch(`/data/issues/${app.id}.json`)
      .then(res => res.json())
      .then(data => {
        setIssues(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching issues:', err);
        setLoading(false);
      });
  }, [app.id]);

  const toggleSection = (severity) => {
    setCollapsed(prev => ({ ...prev, [severity]: !prev[severity] }));
  };

  const scrollToSection = (severity) => {
    // Expand the section if collapsed
    setCollapsed(prev => ({ ...prev, [severity]: false }));
    // Scroll to the section
    setTimeout(() => {
      sectionRefs.current[severity]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  };

  const grouped = {
    critical: issues.filter(i => i.severity === 'critical'),
    major: issues.filter(i => i.severity === 'major'),
    minor: issues.filter(i => i.severity === 'minor'),
  };

  const severityConfig = {
    critical: { label: 'Critical', color: '#f44336' },
    major: { label: 'Major', color: '#ff9800' },
    minor: { label: 'Minor', color: '#666' },
  };

  return (
    <div className="application-detail">
      <div className="detail-header">
        <h2>{app.name}</h2>
        <p className="vendor">{app.vendor || 'Unknown vendor'}</p>
        <div className="issue-counts-summary">
          <span className="critical count-link" onClick={() => scrollToSection('critical')}>{grouped.critical.length} Critical</span>
          <span className="major count-link" onClick={() => scrollToSection('major')}>{grouped.major.length} Major</span>
          <span className="minor count-link" onClick={() => scrollToSection('minor')}>{grouped.minor.length} Minor</span>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading issues...</div>
      ) : issues.length === 0 ? (
        <div className="no-issues">No issues found. Run the crawler to populate data.</div>
      ) : (
        <div className="severity-groups">
          {['critical', 'major', 'minor'].map(severity => {
            const group = grouped[severity];
            const config = severityConfig[severity];
            if (group.length === 0) return null;

            return (
              <div key={severity} className="severity-group" ref={el => sectionRefs.current[severity] = el}>
                <div
                  className="severity-group-header"
                  onClick={() => toggleSection(severity)}
                  style={{ borderLeftColor: config.color }}
                >
                  <span
                    className="severity-badge"
                    style={{ backgroundColor: config.color }}
                  >
                    {config.label.toUpperCase()}
                  </span>
                  <span className="severity-count">{group.length} issues</span>
                  <span className="collapse-toggle">
                    {collapsed[severity] ? '+' : '\u2212'}
                  </span>
                </div>
                {!collapsed[severity] && (
                  <div className="issues-list">
                    {group.map(issue => (
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
          })}
        </div>
      )}
    </div>
  );
}

export default ApplicationDetail;
