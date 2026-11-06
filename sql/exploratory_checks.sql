-- Illustrative SQL checks for a table named match_events.
-- Adapt table and column names to the selected source dataset.

-- 1. Find duplicate event identifiers.
SELECT event_id, COUNT(*) AS occurrences
FROM match_events
GROUP BY event_id
HAVING COUNT(*) > 1;

-- 2. Find rows missing a player identifier.
SELECT *
FROM match_events
WHERE player_id IS NULL;

-- 3. Find event times outside an expected match window.
SELECT *
FROM match_events
WHERE minute < 0 OR minute > 130;
