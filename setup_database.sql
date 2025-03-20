-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS mood_tracker;
USE mood_tracker;

-- Create mood_entries table
CREATE TABLE IF NOT EXISTS mood_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    text_input TEXT,
    voice_input TEXT,
    sentiment_score FLOAT NOT NULL,
    mood_category VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create daily_analysis table
CREATE TABLE IF NOT EXISTS daily_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    happy_count INT DEFAULT 0,
    sad_count INT DEFAULT 0,
    neutral_count INT DEFAULT 0,
    average_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (date)
);

-- Create weekly_analysis table
CREATE TABLE IF NOT EXISTS weekly_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    week_start_date DATE NOT NULL,
    happy_count INT DEFAULT 0,
    sad_count INT DEFAULT 0,
    neutral_count INT DEFAULT 0,
    average_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_week (week_start_date)
);

-- Insert some test data
INSERT INTO mood_entries (date, text_input, sentiment_score, mood_category) VALUES
(CURDATE(), "I'm feeling really happy today!", 0.8, 'Happy'),
(DATE_SUB(CURDATE(), INTERVAL 1 DAY), "Not feeling great, had a rough day.", -0.3, 'Sad'),
(DATE_SUB(CURDATE(), INTERVAL 2 DAY), "Just a regular day, nothing special.", 0.1, 'Neutral'); 