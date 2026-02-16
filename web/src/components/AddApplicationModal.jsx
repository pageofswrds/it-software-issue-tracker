// web/src/components/AddApplicationModal.jsx
import { useState } from 'react';

function AddApplicationModal({ onClose, onCreated }) {
  const [name, setName] = useState('');
  const [vendor, setVendor] = useState('');
  const [keywords, setKeywords] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch('/api/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, vendor, keywords }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to create application');
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
          <h2>New Request</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <p className="modal-description">
          Add a new software application to monitor for issues.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="app-name">Application Name *</label>
            <input
              id="app-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Adobe Acrobat"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="app-vendor">Vendor</label>
            <input
              id="app-vendor"
              type="text"
              value={vendor}
              onChange={(e) => setVendor(e.target.value)}
              placeholder="e.g. Adobe"
            />
          </div>
          <div className="form-group">
            <label htmlFor="app-keywords">Search Keywords</label>
            <input
              id="app-keywords"
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g. acrobat, acrobat reader, adobe pdf"
            />
            <span className="form-hint">Comma-separated. Used to search for issues online.</span>
          </div>
          {error && <div className="form-error">{error}</div>}
          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Application'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddApplicationModal;
