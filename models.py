import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load .env from project root so DATABASE_PATH can override default
load_dotenv()

class Database:
    """Database connection handler - giữ nguyên"""
    
    def __init__(self, db_path=os.getenv('DATABASE_PATH','prisma/dev.db')):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute(self, query: str, params: tuple = ()):
        """Execute query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        result = cursor.fetchall()
        conn.close()
        return result
    
    def execute_one(self, query: str, params: tuple = ()):
        """Execute query and return one result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        result = cursor.fetchone()
        conn.close()
        return result

    def execute_insert(self, query, params=()):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        last = cur.lastrowid
        conn.close()
        return last

# Global database instance
db = Database()
print(f"[DEBUG] Using SQLite DB: {db.db_path}")

class SavingsGoal:
    """Savings Goal model - giữ nguyên"""
    
    @staticmethod
    def create(name: str, target_amount: float, deadline: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Tạo mục tiêu tiết kiệm mới"""
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO SavingsGoal (name, targetAmount, currentAmount, deadline, userId, createdAt, updatedAt)
            VALUES (?, ?, 0, ?, ?, ?, ?)
        '''
        new_id = db.execute_insert(query, (name, target_amount, deadline, user_id, now, now))
        return SavingsGoal.find_by_id(new_id)
    
    @staticmethod
    def find_all(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy tất cả mục tiêu"""
        if user_id:
            query = 'SELECT * FROM SavingsGoal WHERE userId = ? ORDER BY createdAt DESC'
            results = db.execute(query, (user_id,))
        else:
            query = 'SELECT * FROM SavingsGoal ORDER BY createdAt DESC'
            results = db.execute(query)
        
        return [dict(row) for row in results]
    
    @staticmethod
    def find_by_id(goal_id: str) -> Optional[Dict[str, Any]]:
        """Tìm mục tiêu theo ID"""
        query = 'SELECT * FROM SavingsGoal WHERE id = ?'
        result = db.execute_one(query, (goal_id,))
        return dict(result) if result else None
    
    @staticmethod
    def update(goal_id: str, name: Optional[str] = None, target_amount: Optional[float] = None, 
               current_amount: Optional[float] = None, deadline: Optional[str] = None) -> Dict[str, Any]:
        """Cập nhật mục tiêu"""
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if target_amount is not None:
            updates.append('targetAmount = ?')
            params.append(target_amount)
        if current_amount is not None:
            updates.append('currentAmount = ?')
            params.append(current_amount)
        if deadline is not None:
            updates.append('deadline = ?')
            params.append(deadline)
        
        updates.append('updatedAt = ?')
        params.append(datetime.now().isoformat())
        params.append(goal_id)
        
        query = f"UPDATE SavingsGoal SET {', '.join(updates)} WHERE id = ?"
        db.execute(query, tuple(params))
        
        return SavingsGoal.find_by_id(goal_id)
    
    @staticmethod
    def delete(goal_id: str) -> bool:
        """Xóa mục tiêu"""
        query = 'DELETE FROM SavingsGoal WHERE id = ?'
        db.execute(query, (goal_id,))
        return True
    
    @staticmethod
    def add_amount(goal_id: str, amount: float) -> Dict[str, Any]:
        """Thêm tiền vào mục tiêu"""
        query = '''
            UPDATE SavingsGoal 
            SET currentAmount = currentAmount + ?, updatedAt = ?
            WHERE id = ?
        '''
        db.execute(query, (amount, datetime.now().isoformat(), goal_id))
        return SavingsGoal.find_by_id(goal_id)

class Account:
    """Account model - Tài khoản ngân hàng"""
    
    @staticmethod
    def create(name: str, bank: str, account_number: str, starting_balance: float = 0) -> Dict[str, Any]:
        """Tạo tài khoản mới"""
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO Account (name, bank, accountNumber, currentBalance, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        new_id = db.execute_insert(query, (name, bank, account_number, starting_balance, now, now))
        return Account.find_by_id(new_id)
    
    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """Lấy tất cả tài khoản"""
        query = 'SELECT * FROM Account ORDER BY name'
        results = db.execute(query)
        return [dict(row) for row in results]
    
    @staticmethod
    def find_by_id(account_id: str) -> Optional[Dict[str, Any]]:
        """Tìm tài khoản theo ID"""
        query = 'SELECT * FROM Account WHERE id = ?'
        result = db.execute_one(query, (account_id,))
        return dict(result) if result else None
    
    @staticmethod
    def update_balance(account_id: str, new_balance: float) -> bool:
        """Cập nhật số dư"""
        query = 'UPDATE Account SET currentBalance = ?, updatedAt = ? WHERE id = ?'
        db.execute(query, (new_balance, datetime.now().isoformat(), account_id))
        return True

class Transaction:
    """Transaction model - Giao dịch thu chi"""
    
    @staticmethod
    def create(user_id: int, category_id: int, amount: float,
               note: str, date: str, trans_type: str):
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO "Transaction"
            (userId, categoryId, amount, note, date, type, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        new_id = db.execute_insert(query, (
            user_id, category_id, amount, note, date,
            trans_type, now, now
        ))
        return Transaction.find_by_id(new_id)

    @staticmethod
    def find_by_id(trans_id: int):
        row = db.execute_one(
            'SELECT * FROM "Transaction" WHERE id = ?', (trans_id,)
        )
        return dict(row) if row else None
    
    @staticmethod
    def find_by_month(user_id: int, month: str):
        query = '''
            SELECT t.*, c.name AS categoryName
            FROM "Transaction" t
            JOIN Category c ON t.categoryId = c.id
            WHERE t.userId = ?
            AND strftime('%Y-%m', t.date) = ?
            ORDER BY t.date DESC, t.createdAt DESC
        '''
        rows = db.execute(query, (user_id, month))
        return [dict(r) for r in rows]

class User:
    """User model - simple auth"""
    
    @staticmethod
    def create(username, name, email, password, phone=None):
        now = datetime.now().isoformat()
        phash = generate_password_hash(password)
        # Insert without id -> SQLite assigns INTEGER PK
        query = '''INSERT INTO "User" (username,name,email,passwordHash,phone,createdAt,updatedAt)
                   VALUES (?, ?, ?, ?, ?, ?, ?)'''
        new_id = db.execute_insert(query, (username, name, email, phash, phone, now, now))
        return User.find_by_id(new_id)
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        query = 'SELECT * FROM "User" WHERE id = ?'
        result = db.execute_one(query, (user_id,))
        return dict(result) if result else None
    
    @staticmethod
    def find_by_username(username: str) -> Optional[Dict[str, Any]]:
        query = 'SELECT * FROM "User" WHERE username = ?'
        result = db.execute_one(query, (username,))
        return dict(result) if result else None
    
    @staticmethod
    def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        query = 'SELECT * FROM "User" WHERE email = ?'
        result = db.execute_one(query, (email,))
        return dict(result) if result else None
    
    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        return check_password_hash(stored_hash, password)
    
    @staticmethod
    def update_name(user_id: str, new_name: str) -> Dict[str, Any]:
        query = 'UPDATE "User" SET name = ?, updatedAt = ? WHERE id = ?'
        db.execute(query, (new_name, datetime.now().isoformat(), user_id))
        return User.find_by_id(user_id)

class Category:
    @staticmethod
    def create(name, type_, user_id, icon=None):
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO Category (name, type, userId, createdAt)
            VALUES (?, ?, ?, ?)
        '''
        new_id = db.execute_insert(
            query, (name, type_, user_id, now)
        )
        return Category.find_by_id(new_id)

    @staticmethod
    def find_all(user_id, type_):
        rows = db.execute(
            '''
            SELECT * FROM Category
            WHERE userId = ? AND type = ?
            ORDER BY name
            ''',
            (user_id, type_)
        )
        return [dict(r) for r in rows]

    @staticmethod
    def find_by_id(cat_id):
        row = db.execute_one(
            'SELECT * FROM Category WHERE id = ?', (cat_id,)
        )
        return dict(row) if row else None
