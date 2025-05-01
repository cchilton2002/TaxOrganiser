import mysql.connector
import logging
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        try:           
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            logging.error(f"There was an error connecting to the database: {err}")
            raise

        
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
    
    def add_earning(self, payslip_id: int, earning_type: str, amount: float) -> int:
        """Add an earning entry to a payslip"""
        query = """
            INSERT INTO earnings (payslip_id, earning_type, amount)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (payslip_id, earning_type, amount))
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
    
    def add_pension(self, payslip_id: int, type: str, amount: float) -> int:
        query = """
            INSERT INTO pension (payslip_id, type, amount)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (payslip_id, type, amount))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def delete_existing_payslip(self, user_id: int, payment_date: str):
        query = """
            DELETE FROM payslips
            WHERE user_id = %s AND payment_date = %s
        """
        self.cursor.execute(query, (user_id, payment_date))
        self.conn.commit()
    
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
        
    def insert_complete_payslip(self, user_id: int, username: str, email: str, password_hash: str, payment_date: str, earning: list, deductions: list, pension_data: dict, pdf_path: str) -> int:
        try: 
            self.begin_transaction()
            
            self.cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            result = self.cursor.fetchone()

            if result:
                user_id = result["user_id"]
            else:
                insert_query = """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                """
                self.cursor.execute(insert_query, (username, email, password_hash))
                user_id = self.cursor.lastrowid
            
            self.delete_existing_payslip(user_id, payment_date)
            payslip_id = self.insert_payslip(user_id, payment_date, pdf_path)

            for earn in earning:
                self.add_earning(payslip_id, earn['type'], earn['amount'])

            for deduction in deductions:
                self.add_deduction(payslip_id, deduction['type'], deduction['amount'])
                
            for pension in pension_data:
                self.add_pension(payslip_id, pension['type'], pension['amount'])
            
            # self._update_tax_summary(user_id, payment_date)

            self.commit_transaction()
            return payslip_id
            
        except Exception as e:
            self.rollback_transaction()
            logging.error(f"Failed to insert payslip: {e}")
            raise

        
        