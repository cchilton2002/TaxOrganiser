import mysql.connector
import logging
from datetime import datetime
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO)

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
    
    def update_summary(self, user_id: int, payment_date: int) -> int:
        pay_date = datetime.strptime(payment_date, "%Y-%m-%d")
        tax_year = pay_date.year - 1 if (pay_date.month < 4 or (pay_date.month == 4 and pay_date.day < 6)) else pay_date.year
        
        # Get financial year boundaries
        fy_start = f"{tax_year}-04-06"
        fy_end = f"{tax_year + 1}-04-05"
        
        print(f"Tax year {tax_year} range: {fy_start} to {fy_end}")

        self.cursor.execute("""
            SELECT SUM(e.amount) AS total_gross
            FROM earnings e
            JOIN payslips p ON e.payslip_id = p.payslip_id
            WHERE p.user_id = %s
            AND e.earning_type = %s;
        """, (user_id, 'Total Pay'))
        total_gross = self.cursor.fetchone()['total_gross'] or 0.0
        
        self.cursor.execute("""
            SELECT SUM(e.amount) AS total_ni
            FROM deductions e
            JOIN payslips p ON e.payslip_id = p.payslip_id
            WHERE p.user_id = %s
            AND e.deduction_type = %s;
        """, (user_id, 'National Insurance'))
        total_ni = self.cursor.fetchone()['total_ni'] or 0.0
        
        self.cursor.execute("""
            SELECT SUM(e.amount) AS total_tax
            FROM deductions e
            JOIN payslips p ON e.payslip_id = p.payslip_id
            WHERE p.user_id = %s
            AND e.deduction_type = %s;
        """, (user_id, 'Income Tax'))
        total_tax = self.cursor.fetchone()['total_tax'] or 0.0
        
        total_taxable = total_gross
        tax_year = pay_date.year
        
        self.cursor.execute(
            "SELECT user_id FROM summary WHERE user_id = %s AND tax_year = %s",
            (user_id, tax_year)
        )
        existing = self.cursor.fetchone()

        if existing:
            # Update
            query = """
                UPDATE summary
                SET total_gross = %s, total_taxable = %s, total_tax = %s, total_ni = %s
                WHERE user_id = %s AND tax_year = %s
            """
            self.cursor.execute(query, (total_gross, total_taxable, total_tax, total_ni, user_id, tax_year))
        else:
            # Insert
            query = """
                INSERT INTO summary (user_id, tax_year, total_gross, total_taxable, total_tax, total_ni)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (user_id, tax_year, total_gross, total_taxable, total_tax, total_ni))

        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_summaries(self, user_id: int):
        self.cursor.execute("""
            SELECT tax_year, total_gross, total_taxable, total_tax, total_ni
            FROM summary
            WHERE user_id = %s
            ORDER BY tax_year DESC;
        """, (user_id,))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    
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
            
            self.update_summary(user_id, payment_date)
            self.commit_transaction()
            return payslip_id
            
        except Exception as e:
            self.rollback_transaction()
            logging.error(f"Failed to insert payslip: {e}")
            raise

        
        