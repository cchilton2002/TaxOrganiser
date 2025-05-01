import logging
from config.settings import DB_CONFIG
import mysql.connector

class DBInitialiser:
    def __init__(self):
        try: 
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            logging.error(f"Error connecting to database: {err}")
            raise

    def _create_user_table(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(250) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        )

    def _create_payslips_table(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS payslips(                    
                    payslip_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    payment_date DATE NOT NULL,
                    pdf_path VARCHAR(100),
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    INDEX idx_payslip_user (user_id)
                )
            '''
        )
        
    def _create_earnings_table(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS earnings(                    
                    earnings_id INT AUTO_INCREMENT PRIMARY KEY,
                    payslip_id INT NOT NULL,
                    amount FLOAT NOT NULL,
                    earning_type ENUM('Total Pay', 'Holiday Pay', 'Service Charge') NOT NULL,
                    FOREIGN KEY (payslip_id) REFERENCES payslips(payslip_id) ON DELETE CASCADE,
                    INDEX idx_earning_payslip (payslip_id)
                )
            '''
        )

    def _create_pension_table(self):
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS pension(                
                pension_id INT AUTO_INCREMENT PRIMARY KEY,
                payslip_id INT NOT NULL,
                employee_contribution FLOAT,
                employer_contribution FLOAT,
                FOREIGN KEY (payslip_id) REFERENCES payslips(payslip_id) ON DELETE CASCADE,
                INDEX idx_earning_payslip (payslip_id)
            )
            '''
        )
        
    def _create_deductions_table(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS deductions(                    
                    deductions_id INT AUTO_INCREMENT PRIMARY KEY,
                    payslip_id INT NOT NULL,
                    deduction_type ENUM('Income Tax', 'National Insurance', 'Student Loan', 'Pension', 'Other') NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (payslip_id) REFERENCES payslips(payslip_id) ON DELETE CASCADE,
                    INDEX idx_earning_payslip (payslip_id)
                )
            '''
        )
        
    def _create_summaries_table(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS summary(
                    summary_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    tax_year INT NOT NULL,
                    total_gross DECIMAL(12,2) DEFAULT 0.00,
                    total_taxable DECIMAL(12,2) DEFAULT 0.00,
                    total_tax DECIMAL(10,2) DEFAULT 0.00,
                    total_ni DECIMAL(10,2) DEFAULT 0.00,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE KEY uk_user_tax_year (user_id, tax_year)
                )
            '''
        )
        
    def create_tables(self):
        self._create_user_table()
        self._create_payslips_table()
        self._create_deductions_table()
        self._create_earnings_table()
        self._create_pension_table()
        self._create_summaries_table()
        self.conn.commit()
        print("tables created successfully")

    def close(self):
        self.cursor.close()
        self.conn.close()
        
if __name__ == "__main__":
    db_init = DBInitialiser()
    db_init.create_tables()
    db_init.close()