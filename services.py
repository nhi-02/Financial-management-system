from typing import Dict, Any, List, Optional
from models import SavingsGoal, Account, Transaction
from datetime import datetime
import csv
import io

class SavingsService:
    """Savings service - Business logic"""
    
    @staticmethod
    def create_goal(name: str, target_amount: float, deadline: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Tạo mục tiêu tiết kiệm"""
        if not name or not name.strip():
            raise ValueError("Tên mục tiêu không được để trống")
        
        if target_amount <= 0:
            raise ValueError("Số tiền mục tiêu phải lớn hơn 0")
        
        return SavingsGoal.create(name, target_amount, deadline, user_id)
    
    @staticmethod
    def get_all_goals(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy tất cả mục tiêu"""
        return SavingsGoal.find_all(user_id)
    
    @staticmethod
    def get_goal_by_id(goal_id: str) -> Optional[Dict[str, Any]]:
        """Lấy mục tiêu theo ID"""
        return SavingsGoal.find_by_id(goal_id)
    
    @staticmethod
    def update_goal(goal_id: str, name: Optional[str] = None, target_amount: Optional[float] = None,
                   current_amount: Optional[float] = None, deadline: Optional[str] = None) -> Dict[str, Any]:
        """Cập nhật mục tiêu"""
        goal = SavingsGoal.find_by_id(goal_id)
        if not goal:
            raise ValueError("Không tìm thấy mục tiêu")
        
        return SavingsGoal.update(goal_id, name, target_amount, current_amount, deadline)
    
    @staticmethod
    def delete_goal(goal_id: str) -> bool:
        """Xóa mục tiêu"""
        goal = SavingsGoal.find_by_id(goal_id)
        if not goal:
            raise ValueError("Không tìm thấy mục tiêu")
        
        return SavingsGoal.delete(goal_id)
    
    @staticmethod
    def add_amount_to_goal(goal_id: str, amount: float) -> Dict[str, Any]:
        """Thêm tiền vào mục tiêu"""
        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        
        return SavingsGoal.add_amount(goal_id, amount)
    
    @staticmethod
    def calculate_progress(goal: Dict[str, Any]) -> Dict[str, Any]:
        """Tính tiến độ hoàn thành"""
        target = goal['targetAmount']
        current = goal['currentAmount']
        
        if target <= 0:
            progress = 0
        else:
            progress = min(100, (current / target) * 100)
        
        remaining = max(0, target - current)
        is_complete = current >= target
        
        return {
            **goal,
            'progress': round(progress, 1),
            'remaining': remaining,
            'isComplete': is_complete
        }
    
    @staticmethod
    def get_summary(user_id: Optional[str] = None) -> Dict[str, Any]:
        """Tổng hợp tất cả mục tiêu"""
        goals = SavingsGoal.find_all(user_id)
        
        total_target = sum(g['targetAmount'] for g in goals)
        total_current = sum(g['currentAmount'] for g in goals)
        
        if total_target > 0:
            overall_progress = (total_current / total_target) * 100
        else:
            overall_progress = 0
        
        completed_count = sum(1 for g in goals if g['currentAmount'] >= g['targetAmount'])
        
        return {
            'totalGoals': len(goals),
            'completedGoals': completed_count,
            'totalTarget': total_target,
            'totalCurrent': total_current,
            'overallProgress': round(overall_progress, 1),
            'goals': [SavingsService.calculate_progress(g) for g in goals]
        }


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
    
    @staticmethod
    def delete_transaction(trans_id: str) -> bool:
        """Xóa giao dịch"""
        transaction = Transaction.find_by_id(trans_id)
        if not transaction:
            raise ValueError("Không tìm thấy giao dịch")
        
        account_id = transaction.get('accountId')
        
        # Xóa giao dịch
        result = Transaction.delete(trans_id)
        
        # Cập nhật lại số dư tài khoản
        if account_id:
            AccountService.recalculate_balance(account_id)
        
        return result
