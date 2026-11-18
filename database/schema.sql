
CREATE DATABASE IF NOT EXISTS communityconnect
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE communityconnect;

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    event_date DATE NOT NULL,
    location VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id)
) ENGINE=InnoDB;

-- Only seed sample data when the events table is empty.
INSERT INTO events (title, event_date, location)
SELECT 'Community Technology Workshop', '2026-12-05', 'Sydney'
WHERE NOT EXISTS (SELECT 1 FROM events);

INSERT INTO events (title, event_date, location)
SELECT 'Local Volunteer Meetup', '2027-01-15', 'Parramatta'
WHERE NOT EXISTS (
    SELECT 1 FROM events
    WHERE title = 'Local Volunteer Meetup'
);

INSERT INTO events (title, event_date, location)
SELECT 'Community Networking Day', '2027-02-03', 'Chatswood'
WHERE NOT EXISTS (
    SELECT 1 FROM events
    WHERE title = 'Community Networking Day'
);
