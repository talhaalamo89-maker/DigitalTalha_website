-- Only keyed IP digests and short-lived rate-limit timestamps; no enquiries.
CREATE TABLE IF NOT EXISTS enquiry_limits (
  key TEXT PRIMARY KEY,
  expires INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS enquiry_limits_expiry ON enquiry_limits(expires);
