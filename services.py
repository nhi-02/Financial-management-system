from typing import Dict, Any, List, Optional
from models import SavingsGoal, Account, Transaction, db
from datetime import datetime, timedelta
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
        
    @staticmethod
    def get_financial_data_for_ai(user_id: Optional[str] = None, months: int = 6) -> Dict[str, Any]:
        """
            Tổng hợp dữ liệu tài chính để gửi cho AI
            Bao gồm: thu nhập, chi tiêu, mục tiêu tiết kiệm
        """
        # Lấy mục tiêu
        goals = SavingsGoal.find_all(user_id)
        
        # Lấy giao dịch (giả sử có Transaction model)
        try:
            # Lấy giao dịch 6 tháng gần đây
            cutoff_date = (datetime.now() - timedelta(days=months*30)).isoformat()
            transactions = Transaction.find_all(limit=1000)
            
            # Lọc theo thời gian
            recent_trans = [t for t in transactions if t.get('date', '') >= cutoff_date]
            
            total_income = sum(t['amount'] for t in recent_trans if t['type'] == 'INCOME')
            total_expense = sum(t['amount'] for t in recent_trans if t['type'] == 'EXPENSE')
            
            # Chi tiêu theo danh mục
            expense_by_category = {}
            for t in recent_trans:
                if t['type'] == 'EXPENSE':
                    cat = t.get('category', 'Khác')
                    expense_by_category[cat] = expense_by_category.get(cat, 0) + t['amount']
            
        except Exception as e:
            # Nếu chưa có giao dịch hoặc lỗi
            total_income = 0
            total_expense = 0
            expense_by_category = {}
        
        # Tổng tiết kiệm hiện tại
        current_savings = sum(g.get('currentAmount', 0) for g in goals)
        
        # Chi tiêu trung bình/tháng
        monthly_avg_expense = total_expense / months if months > 0 else 0
        monthly_avg_income = total_income / months if months > 0 else 0
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'monthly_avg_income': monthly_avg_income,
            'monthly_avg_expense': monthly_avg_expense,
            'current_savings': current_savings,
            'savings_goals': goals,
            'expense_by_category': expense_by_category,
            'period_months': months,
            'monthly_income': monthly_avg_income,
            'monthly_expense': monthly_avg_expense,
            'other_goals': goals
        }
        
class TransactionService:
    @staticmethod
    def add_transaction(user_id, category_id, amount, date, note, trans_type):
        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")

        if trans_type not in ('expense', 'income'):
            raise ValueError("Loại giao dịch không hợp lệ")

        return Transaction.create(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            note=note,
            date=date,
            trans_type=trans_type
        )
    @staticmethod
    def summary_by_month(user_id, month, trans_type):
        query = '''
            SELECT c.name as category,
                   SUM(t.amount) as total
            FROM "Transaction" t
            JOIN Category c ON t.categoryId = c.id
            WHERE t.userId = ?
              AND t.type = ?
              AND strftime('%Y-%m', t.date) = ?
            GROUP BY c.id
            ORDER BY total DESC
        '''
        rows = db.execute(query, (user_id, trans_type, month))
        return [dict(r) for r in rows]
    
class AnalysisService:
    @staticmethod
    def category_summary(user_id, month, trans_type):
        query = '''
            SELECT c.name AS category, SUM(t.amount) AS total
            FROM "Transaction" t
            JOIN Category c ON t.categoryId = c.id
            WHERE t.userId = ?
              AND t.type = ?
              AND strftime('%Y-%m', t.date) = ?
            GROUP BY c.id
        '''
        rows = db.execute(query, (user_id, trans_type, month))
        return [dict(r) for r in rows]
    
    @staticmethod
    def daily_summary(user_id, month):
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT date,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense,
                   SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS income
            FROM "Transaction"
            WHERE userId = ?
              AND strftime('%Y-%m', date) = ?
            GROUP BY date
            ORDER BY date
        """, (user_id, month))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                'date': r['date'],
                'expense': r['expense'] or 0,
                'income': r['income'] or 0
            }
            for r in rows
        ]