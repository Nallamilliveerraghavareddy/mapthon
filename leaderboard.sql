PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE leaderboard (display_name TEXT, user_email TEXT UNIQUE, osm_user_id TEXT default null, current_score INT default 0, last_update TEXT, mr_cid TEXT default '0');
COMMIT;
