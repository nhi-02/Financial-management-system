from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os

# Import services và models
from services import SavingsService, AccountService, TransactionService
from utils import format_currency, format_date, validate_amount

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# ==================== ĐĂNG KÝ TEMPLATE FILTERS ====================
@app.template_filter('format_currency')
def _format_currency(amount):
    """Template filter: Format tiền"""
    return format_currency(amount)

@app.template_filter('format_date')
def _format_date(date_str):
    """Template filter: Format ngày"""
    return format_date(date_str)

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Trang chủ - Dashboard tổng quan"""
    try:
        summary = SavingsService.get_summary()
        return render_template('index.html', summary=summary)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('index.html', summary={'goals': [], 'totalTarget': 0, 'totalCurrent': 0, 'overallProgress': 0})

@app.route('/goal/new')
def new_goal():
    """Form tạo mục tiêu mới"""
    return render_template('new_goal.html')

@app.route('/goal/create', methods=['POST'])
def create_goal():
    """Xử lý tạo mục tiêu"""
    try:
        name = request.form['name']
        target = validate_amount(request.form['targetAmount'])
        deadline = request.form.get('deadline') or None
        
        SavingsService.create_goal(name, target, deadline)
        flash('Tạo mục tiêu thành công!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('new_goal'))

@app.route('/goal/<goal_id>/edit')
def edit_goal(goal_id):
    """Form chỉnh sửa mục tiêu"""
    try:
        goal = SavingsService.get_goal_by_id(goal_id)
        if not goal:
            flash('Không tìm thấy mục tiêu', 'error')
            return redirect(url_for('index'))
        
        return render_template('edit_goal.html', goal=goal)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/goal/<goal_id>/update', methods=['POST'])
def update_goal(goal_id):
    """Cập nhật mục tiêu"""
    try:
        name = request.form['name']
        target = validate_amount(request.form['targetAmount'])
        current = validate_amount(request.form['currentAmount'])
        deadline = request.form.get('deadline') or None
        
        SavingsService.update_goal(goal_id, name, target, current, deadline)
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('edit_goal', goal_id=goal_id))

@app.route('/goal/<goal_id>/delete', methods=['POST'])
def delete_goal(goal_id):
    """Xóa mục tiêu"""
    try:
        SavingsService.delete_goal(goal_id)
        flash('Xóa mục tiêu thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/goal/<goal_id>/add-amount', methods=['POST'])
def add_amount(goal_id):
    """Thêm tiền vào mục tiêu"""
    try:
        amount = validate_amount(request.form['amount'])
        SavingsService.add_amount_to_goal(goal_id, amount)
        flash(f'Đã thêm {format_currency(amount)} vào mục tiêu!', 'success')
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# ==================== API (JSON) ====================

@app.route('/api/goals')
def api_goals():
    """API lấy danh sách mục tiêu (JSON)"""
    try:
        summary = SavingsService.get_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ACCOUNTS ====================

@app.route('/accounts')
def accounts_list():
    """Danh sách tài khoản"""
    try:
        accounts = AccountService.get_all_accounts()
        return render_template('accounts_list.html', accounts=accounts)
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('accounts_list.html', accounts=[])

@app.route('/accounts/new')
def accounts_new():
    return render_template('accounts.html')

@app.route('/accounts/create', methods=['POST'])
def accounts_create():
    try:
        name = request.form['name']
        bank = request.form.get('bank')
        account_number = request.form.get('accountNumber')
        starting_balance = validate_amount(request.form.get('startingBalance', 0))
        AccountService.create_account(name, bank, account_number, starting_balance)
        flash('Tạo tài khoản thành công!', 'success')
        return redirect(url_for('accounts_list'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('accounts_new'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return "Không tìm thấy trang", 404

@app.errorhandler(500)
def internal_error(error):
    return "Lỗi server", 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Kiểm tra database tồn tại (dev.db used by init_db/models)
    if not os.path.exists('prisma/dev.db'):
         print("⚠️  Cảnh báo: Database chưa tồn tại")
         print("   Chạy: python init_db.py để tạo database")
     
    app.run(debug=True, host='0.0.0.0', port=5000)