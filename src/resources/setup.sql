DROP TABLE events CASCADE;

CREATE TABLE events (
  event_name  VARCHAR(256) NOT NULL,  -- TODO: Create all event list for check
  event_time  INT          NOT NULL , -- TODO: Change int to Timestamp???
  user_id     INT          NOT NULL   -- TODO: User's table and foreign key
);