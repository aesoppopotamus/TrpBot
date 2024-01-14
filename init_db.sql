CREATE TABLE IF NOT EXISTS scheduled_repeating_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    message_content TEXT,
    interval_unit VARCHAR(50),
    interval_value INT,
    job_id VARCHAR(255),
    scheduled_by VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS scheduled_commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    command_content TEXT,
    interval_unit VARCHAR(50),
    interval_value INT,
    job_id VARCHAR(255),
    scheduled_by VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS monthly_planning (
    id int AUTO_INCREMENT PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    planning_header TEXT,
    planning_content TEXT,
    planning_month TEXT,
    username VARCHAR(255),
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);