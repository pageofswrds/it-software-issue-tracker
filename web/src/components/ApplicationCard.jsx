// web/src/components/ApplicationCard.jsx
import { useState } from 'react';

const VENDOR_DOMAINS = {
  'adobe': 'adobe.com',
  'microsoft': 'microsoft.com',
  'zoom': 'zoom.us',
  'slack': 'slack.com',
  'intuit': 'intuit.com',
  'atlassian': 'atlassian.com',
  'google': 'google.com',
  'apple': 'apple.com',
  'salesforce': 'salesforce.com',
  'oracle': 'oracle.com',
  'sap': 'sap.com',
  'ibm': 'ibm.com',
  'servicenow': 'servicenow.com',
  'dropbox': 'dropbox.com',
  'github': 'github.com',
  'tableau': 'tableau.com',
  'notion labs inc.': 'notion.so',
};

function getLogoDomain(vendor) {
  if (!vendor) return null;
  const key = vendor.toLowerCase().trim();
  if (VENDOR_DOMAINS[key]) return VENDOR_DOMAINS[key];
  // Try vendor name as domain directly
  if (key.includes('.')) return key;
  return `${key}.com`;
}

function ApplicationCard({ app, onClick }) {
  const [logoError, setLogoError] = useState(false);
  const totalIssues = app.critical_count + app.major_count + app.minor_count;
  const logoDomain = getLogoDomain(app.vendor);

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
      <div className="app-card-body">
        <div className="app-card-info">
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
        {logoDomain && !logoError && (
          <img
            className="vendor-logo"
            src={`https://www.google.com/s2/favicons?domain=${logoDomain}&sz=128`}
            alt={`${app.vendor} logo`}
            onError={() => setLogoError(true)}
          />
        )}
      </div>
    </div>
  );
}

export default ApplicationCard;
