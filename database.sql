CREATE DATABASE IF NOT EXISTS personal_expense_tracker;
USE personal_expense_tracker;

CREATE TABLE IF NOT EXISTS Expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    expense_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    expense_date DATE NOT NULL
);
