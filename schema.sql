-- Reset schema for local setup; executing this file removes existing ticket data.
DROP TABLE IF EXISTS tickets;

-- One row represents one support request throughout its lifecycle.
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    submitted_by TEXT NOT NULL,
    -- Reserved for future assignment support; there is currently no assignment form.
    assigned_to TEXT,
    -- SQLite generates UTC timestamps; routes explicitly update updated_at on changes.
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- The resolve route requires a nonblank note before changing status to Resolved.
    resolution_notes TEXT
);
