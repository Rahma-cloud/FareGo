-- FareGo schema for a HOSTED MySQL database (import this in phpMyAdmin).
-- The host gives you a fixed database, so there is no CREATE DATABASE or USE here.
-- Uses TIMESTAMP for created_at because some free hosts run an old MySQL that
-- rejects DATETIME with a CURRENT_TIMESTAMP default (error #1067).
-- Safe to import twice: tables are only created if missing, and the fare row
-- is only added if missing. (Your normal schema.sql stays as it is for local use.)

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  pin_hash VARCHAR(255) NOT NULL,
  role ENUM('student','driver') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS drivers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  bus_number VARCHAR(20) NOT NULL,
  qr_code VARCHAR(20) NOT NULL UNIQUE,
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wallets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  balance DECIMAL(12,2) NOT NULL DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  payer_user_id INT NOT NULL,
  payee_driver_id INT NULL,
  amount DECIMAL(10,2) NOT NULL,
  type ENUM('topup','fare') NOT NULL,
  flagged_duplicate TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (payer_user_id) REFERENCES users(id),
  FOREIGN KEY (payee_driver_id) REFERENCES drivers(id),
  INDEX idx_payer_time (payer_user_id, created_at),
  INDEX idx_payee_time (payee_driver_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS receipts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id INT NOT NULL UNIQUE,
  receipt_no VARCHAR(20) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS settings (
  setting_key VARCHAR(50) PRIMARY KEY,
  setting_value VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Placeholder amount: change 200 to the real shuttle fare.
INSERT IGNORE INTO settings (setting_key, setting_value) VALUES ('fare', '200');