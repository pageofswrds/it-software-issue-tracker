-- database/seed.sql
-- Sample applications to monitor
INSERT INTO applications (name, vendor, keywords) VALUES
    ('Adobe Acrobat', 'Adobe', ARRAY['adobe acrobat', 'acrobat reader', 'acrobat dc', 'pdf reader']),
    ('Microsoft Teams', 'Microsoft', ARRAY['microsoft teams', 'ms teams', 'teams app']),
    ('Zoom', 'Zoom', ARRAY['zoom', 'zoom client', 'zoom app']),
    ('Slack', 'Salesforce', ARRAY['slack', 'slack app', 'slack desktop']);
