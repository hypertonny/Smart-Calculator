import sqlite3
from datetime import datetime

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect('transactions.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create customer transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                amount REAL NOT NULL,
                type TEXT CHECK(type IN ('credit', 'debit')),
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        self.conn.commit()

    def add_transaction(self, amount, description):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO transactions (amount, description) VALUES (?, ?)',
                      (amount, description))
        self.conn.commit()

    def get_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 100')
        return cursor.fetchall()

    def add_customer(self, name, phone, email, address):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, email, address))
        self.conn.commit()
        return cursor.lastrowid

    def get_customers(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY name')
        return cursor.fetchall()

    def update_customer(self, customer_id, name, phone, email, address):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE customers 
            SET name=?, phone=?, email=?, address=?
            WHERE id=?
        ''', (name, phone, email, address, customer_id))
        self.conn.commit()

    def delete_customer(self, customer_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM customers WHERE id=?', (customer_id,))
        self.conn.commit()

    def add_customer_transaction(self, customer_id, amount, type, description):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO customer_transactions (customer_id, amount, type, description)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, amount, type, description))
        self.conn.commit()

    def get_customer_transactions(self, customer_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM customer_transactions 
            WHERE customer_id=? 
            ORDER BY timestamp DESC
        ''', (customer_id,))
        return cursor.fetchall()

    def get_customer(self, customer_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id=?', (customer_id,))
        return cursor.fetchone()

    def export_customer_data(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.*, GROUP_CONCAT(ct.amount || ',' || ct.type || ',' || ct.timestamp)
            FROM customers c
            LEFT JOIN customer_transactions ct ON c.id = ct.customer_id
            GROUP BY c.id
        ''')
        return cursor.fetchall()

    def import_customer_data(self, customer_data):
        cursor = self.conn.cursor()
        for customer in customer_data:
            cursor.execute('''
                INSERT INTO customers (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', customer[:4])
        self.conn.commit()

    def __del__(self):
        self.conn.close()
