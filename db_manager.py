import sqlite3

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect('transactions.db')
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                 id INTEGER PRIMARY KEY,
                                 amount REAL,
                                 description TEXT,
                                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    def add_transaction(self, amount, description):
        with self.conn:
            self.conn.execute('INSERT INTO transactions (amount, description) VALUES (?, ?)', (amount, description))

    def get_transactions(self):
        cursor = self.conn.cursor()
        return cursor.execute('SELECT * FROM transactions').fetchall()
