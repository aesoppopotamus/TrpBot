CREATE TABLE IF NOT EXISTS scheduled_repeating_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    message_content TEXT,
    interval_unit VARCHAR(50),
    interval_value INT,
    job_id VARCHAR(255)
    scheduled_by VARCHAR(255)
);