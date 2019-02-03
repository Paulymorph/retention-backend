DROP TABLE events CASCADE;

CREATE TABLE events (
  event_name  VARCHAR(256) NOT NULL,  -- TODO: Create all event list for check
  event_time  BIGINT          NOT NULL,
  user_id     INT          NOT NULL   -- TODO: User's table and foreign key
);