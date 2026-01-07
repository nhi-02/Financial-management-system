import sqlite3
from datetime import datetime
import os
from typing import Dict, Any, List, Optional
import csv
import io

from models import SavingsGoal, Account, Transaction

DB_PATH = 'prisma/dev.db'

def init_database():
    """Khởi tạo database với schema cơ bản (KHÔNG có dữ liệu mẫu)"""
    
    # Tạo thư mục prisma nếu chưa có
    os.makedirs('prisma', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tạo bảng SavingsGoal
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SavingsGoal (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            targetAmount REAL NOT NULL,
            currentAmount REAL DEFAULT 0,
            deadline TEXT,
            userId TEXT,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    ''')
    
    # Tạo bảng Account (Tài khoản ngân hàng)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            bank TEXT,
            accountNumber TEXT,
            currentBalance REAL DEFAULT 0,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    ''')
    
    # Tạo bảng Transaction (Giao dịch) - WRAP với backticks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `Transaction` (
            id TEXT PRIMARY KEY,
            accountId TEXT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL,
            FOREIGN KEY (accountId) REFERENCES Account(id)
        )
    ''')
    
    conn.commit()
    
    # Kiểm tra xem đã có dữ liệu chưa
    cursor.execute('SELECT COUNT(*) FROM SavingsGoal')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("⚠️  Database trống - chưa có dữ liệu")
        print("   Hãy thêm mục tiêu tiết kiệm đầu tiên qua giao diện web")
    else:
        print(f"✅ Database đã có {count} mục tiêu tiết kiệm")
    
    conn.close()
    
    print(f"✅ Database đã sẵn sàng tại {DB_PATH}")

class SavingsService:
    """Savings service - giữ nguyên code hiện tại"""
    # ...existing code...

class AccountService:
    """Account service - Quản lý tài khoản ngân hàng"""
    
    @staticmethod
    def create_account(name: str, bank: str, account_number: str, starting_balance: float = 0) -> Dict[str, Any]:
        """Tạo tài khoản ngân hàng mới"""
        return Account.create(name, bank, account_number, starting_balance)
    
    @staticmethod
    def get_all_accounts() -> List[Dict[str, Any]]:
        """Lấy tất cả tài khoản"""
        return Account.find_all()
    
    @staticmethod
    def get_account_by_id(account_id: str) -> Optional[Dict[str, Any]]:
        """Lấy tài khoản theo ID"""
        return Account.find_by_id(account_id)
    
    @staticmethod
    def import_csv_statement(account_id: str, csv_content: str) -> Dict[str, Any]:
        """
        Import sao kê ngân hàng từ CSV
        Format CSV mong đợi: Date, Description, Amount, Category
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        transactions = []
        errors = []
        
        for row_num, row in enumerate(reader, start=1):
            try:
                # Parse dữ liệu
                date = row.get('Date', row.get('Ngày'))
                description = row.get('Description', row.get('Mô tả'))
                amount_str = row.get('Amount', row.get('Số tiền', '0'))
                category = row.get('Category', row.get('Danh mục', 'other'))
                
                # Xử lý số tiền (loại bỏ dấu phẩy, ký tự đặc biệt)
                amount = float(amount_str.replace(',', '').replace(' ', '').replace('đ', ''))
                
                # Xác định loại giao dịch (income/expense)
                trans_type = 'income' if amount > 0 else 'expense'
                
                # Tạo transaction
                trans = Transaction.create(
                    account_id=account_id,
                    amount=abs(amount),
                    category=category,
                    description=description,
                    date=date,
                    trans_type=trans_type
                )
                transactions.append(trans)
                
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'error': str(e),
                    'data': row
                })
        
        # Cập nhật số dư tài khoản
        if transactions:
            AccountService.recalculate_balance(account_id)
        
        return {
            'imported': len(transactions),
            'errors': errors,
            'transactions': transactions
        }
    
    @staticmethod
    def recalculate_balance(account_id: str) -> float:
        """Tính lại số dư tài khoản từ giao dịch"""
        from models import db
        
        # Tính tổng thu nhập
        income_query = '''
            SELECT COALESCE(SUM(amount), 0) FROM Transaction 
            WHERE accountId = ? AND type = 'income'
        '''
        income = db.execute_one(income_query, (account_id,))[0]
        
        # Tính tổng chi phí
        expense_query = '''
            SELECT COALESCE(SUM(amount), 0) FROM Transaction 
            WHERE accountId = ? AND type = 'expense'
        '''
        expense = db.execute_one(expense_query, (account_id,))[0]
        
        balance = income - expense
        
        # Cập nhật vào database
        update_query = 'UPDATE Account SET currentBalance = ?, updatedAt = ? WHERE id = ?'
        db.execute(update_query, (balance, datetime.now().isoformat(), account_id))
        
        return balance

class TransactionService:
    """Transaction service - Quản lý giao dịch"""
    
    @staticmethod
    def create_transaction(account_id: str, amount: float, category: str, 
                          description: str, date: str, trans_type: str) -> Dict[str, Any]:
        """Tạo giao dịch mới"""
        transaction = Transaction.create(account_id, amount, category, description, date, trans_type)
        
        # Cập nhật số dư tài khoản
        AccountService.recalculate_balance(account_id)
        
        return transaction
    
    @staticmethod
    def get_transactions(account_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Lấy danh sách giao dịch"""
        return Transaction.find_all(account_id, limit)

if __name__ == '__main__':
    init_database()
