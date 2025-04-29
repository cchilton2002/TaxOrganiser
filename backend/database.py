import mysql.connector
import logging
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        try:           
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            self._create_tables()
        except mysql.connector.Error as err:
            logging.error(f"There was an error connecting to the database: {err}")
            raise

        

    def _create_tables(self):
        self._create_user_table()
        self._create_payslips_table()
        self._create_earnings_table()
        self._create_pension_table()
        self._create_deductions_table()
        self._create_summaries_table()
        self.conn.commit()

    def _create_user_table(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(250) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tax_code VARCHAR(20),
                    national_insurance_number VARCHAR(20)
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
                    total_pension_employee DECIMAL(10,2) DEFAULT 0.00,
                    total_pension_employer DECIMAL(10,2) DEFAULT 0.00,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE KEY uk_user_tax_year (user_id, tax_year)
                )
            '''
        )
        
    def create_user(self, username: str, email: str, password_hash: str) -> int:
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        
        self.cursor.execute(query, (username, email, password_hash))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_user_by_id(self, user_id: int) -> dict:
        self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()
    
    def insert_payslip(self, user_id: int, payment_date: str, pdf_path: str) -> int:
        query = """
            INSERT INTO payslips (user_id, payment_date, pdf_path)
            VALUES (%s, %s, %s)
        """

        self.cursor.execute(query, (user_id, payment_date, pdf_path))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_payslip_by_user(self, user_id: int) -> dict:
        self.cursor.execute("SELECT * FROM payslips WHERE user_id = %s", (user_id,))
        return self.cursor.fetchall()
    
    def add_earning(self, payslip_id: int, amount: float) -> int:
        """Add an earning entry to a payslip"""
        query = """
            INSERT INTO earnings (payslip_id, amount, earning_type)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (payslip_id, amount, earning_type))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_deduction(self, payslip_id: int, deduction_type: str, amount: float) -> int:
        """Add a deduction to a payslip"""
        query = """
            INSERT INTO deductions (payslip_id, deduction_type, amount)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (payslip_id, deduction_type, amount))
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.connection.close()
        
    def begin_transaction(self):
        """Start a transaction"""
        self.cursor.execute("START TRANSACTION")

    def commit_transaction(self):
        """Commit the current transaction"""
        self.conn.commit()
        
    def rollback_transaction(self):
        self.conn.rollback()
        
    def insert_complete_payslip(self, user_id: int, payment_date: str, earning: list, deductions: list, pension_data: dict, pdf_path: str) -> int:
        try: 
            self.begin_transaction()
            
            payslip_id = self.insert_payslip(user_id, payment_date, pdf_path)

            for earning in earning:
                self.add_earning(payslip_id, earning['amount'], earning['type'])

            for deduction in deductions:
                self.add_deduction(payslip_id, deduction['type'], deduction['amount'])

            pension_query = """
                INSERT INTO pension (payslip_id, employee_contribution, employer_contribution)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(pension_query, (
                payslip_id,
                pension_data.get('employee_contribution', 0),
                pension_data.get('employer_contribution', 0)
            ))
            
            self._update_tax_summary(user_id, payment_date)

            self.commit_transaction()
            return payslip_id
            
        except Exception as e:
            self.rollback_transaction()
            logging.error(f"Failed to insert payslip: {e}")
            raise

        
        