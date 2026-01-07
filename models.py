import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class Database:
    """Database connection handler - giữ nguyên"""
    
    def __init__(self, db_path: str = 'prisma/dev.db'):
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

# Global database instance
db = Database()

class SavingsGoal:
    """Savings Goal model - giữ nguyên"""
    
    @staticmethod
    def create(name: str, target_amount: float, deadline: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Tạo mục tiêu tiết kiệm mới"""
        goal_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        query = '''
            INSERT INTO SavingsGoal (id, name, targetAmount, currentAmount, deadline, userId, createdAt, updatedAt)
            VALUES (?, ?, ?, 0, ?, ?, ?, ?)
        '''
        db.execute(query, (goal_id, name, target_amount, deadline, user_id, now, now))
        
        return SavingsGoal.find_by_id(goal_id)
    
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
        account_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        query = '''
            INSERT INTO Account (id, name, bank, accountNumber, currentBalance, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute(query, (account_id, name, bank, account_number, starting_balance, now, now))
        
        return Account.find_by_id(account_id)
    
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
    def create(account_id: str, amount: float, category: str, description: str, 
               date: str, trans_type: str) -> Dict[str, Any]:
        """Tạo giao dịch mới"""
        trans_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        query = '''
            INSERT INTO Transaction (id, accountId, amount, category, description, date, type, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute(query, (trans_id, account_id, amount, category, description, date, trans_type, now, now))
        
        return Transaction.find_by_id(trans_id)
    
    @staticmethod
    def find_all(account_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Lấy danh sách giao dịch"""
        if account_id:
            query = 'SELECT * FROM Transaction WHERE accountId = ? ORDER BY date DESC LIMIT ?'
            results = db.execute(query, (account_id, limit))
        else:
            query = 'SELECT * FROM Transaction ORDER BY date DESC LIMIT ?'
            results = db.execute(query, (limit,))
        
        return [dict(row) for row in results]
    
    @staticmethod
    def find_by_id(trans_id: str) -> Optional[Dict[str, Any]]:
        """Tìm giao dịch theo ID"""
        query = 'SELECT * FROM Transaction WHERE id = ?'
        result = db.execute_one(query, (trans_id,))
        return dict(result) if result else None
    
    @staticmethod
    def delete(trans_id: str) -> bool:
        """Xóa giao dịch"""
        query = 'DELETE FROM Transaction WHERE id = ?'
        db.execute(query, (trans_id,))
        return True
