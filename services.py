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
