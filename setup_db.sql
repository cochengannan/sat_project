-- CSC SAT 2026 - Run in phpMyAdmin on FreeSQLDatabase
USE sql12820158;

CREATE TABLE IF NOT EXISTS registrations (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    admit_card_no VARCHAR(20)  UNIQUE NOT NULL,
    name          VARCHAR(100) NOT NULL,
    gender        ENUM('Male','Female') NOT NULL,
    mobile        VARCHAR(15)  NOT NULL,
    exam_centre   VARCHAR(30)  NOT NULL,
    exam_date     VARCHAR(50)  NOT NULL,
    exam_time     VARCHAR(15)  NOT NULL,
    registered_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    is_active     TINYINT(1)   DEFAULT 1,
    INDEX idx_mobile (mobile),
    INDEX idx_admit  (admit_card_no),
    INDEX idx_centre (exam_centre)
);
