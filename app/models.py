import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    balance REAL NOT NULL
)
""")
conn.commit()


class User:
    @staticmethod
    def get(username):
        cursor.execute(
            "SELECT username, balance FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user is None:
            cursor.execute(
                "INSERT INTO users (username, balance) VALUES (?, 0)", (username,))
            conn.commit()
        cursor.execute(
            "SELECT username, balance FROM users WHERE username = ?", (username,))
        return {"username": user[0]}

    @staticmethod
    def deposit(username, amount):
        cursor.execute(
            "SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone() is None:
            raise Exception("User not found")
        cursor.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE username = ?
        """, (amount, username))
        conn.commit()
        cursor.execute(
            "SELECT balance FROM users WHERE username = ?", (username,))
        return cursor.fetchone()[0]

    @staticmethod
    def transfer(sender, recipient, amount):
        cursor.execute(
            "SELECT username, balance FROM users WHERE username = ?", (sender,))
        user = cursor.fetchone()
        if user is None:
            raise Exception("Sender not found")
        if user[1] < amount:
            raise Exception("Insufficient funds")
        cursor.execute(
            "SELECT username FROM users WHERE username = ?", (recipient,))
        if cursor.fetchone() is None:
            raise Exception("Recipient not found")
        cursor.execute("""
        UPDATE users
        SET balance = balance - ?
        WHERE username = ?
        """, (amount, sender))
        cursor.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE username = ?
        """, (amount, recipient))
        conn.commit()

        return {"from_username": sender, "to_username": recipient, "amount": amount}

    @staticmethod
    def get_balance(username):
        cursor.execute(
            "SELECT username, balance FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user is None:
            raise Exception("User not found")
        return {"username": user[0], "balance": user[1]}
