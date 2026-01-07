from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Import services và models
from services import SavingsService
from utils import format_currency, format_date, validate_amount
from models import User
from flask import abort
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
# session cookie settings for local dev
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Bắt buộc đăng nhập cho hầu hết các route
@app.before_request
def require_login():
    # các endpoint được phép truy cập khi chưa đăng nhập
    public_endpoints = {'login', 'register', 'static', 'not_found', 'internal_error'}
    endpoint = request.endpoint
    if endpoint is None:
        return
    if endpoint.split('.')[-1] in public_endpoints:
        return
    if not session.get('user_id'):
        return redirect(url_for('login'))

# Inject current_user into templates
@app.context_processor
def inject_user():
    user = None
    user_id = session.get('user_id')
    print(f"[DEBUG] inject_user: session user_id = {user_id}")
    if user_id:
        # if id is str/bytes/int, ensure passing the right type
        try:
            user = User.find_by_id(user_id)
        except Exception as _e:
            print(f"[DEBUG] inject_user: find_by_id error: {_e}")
            user = None
    print(f"[DEBUG] inject_user: current_user = {user}")
    return {'current_user': user}

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
        user_id = session.get('user_id')
        # lấy summary theo user; nếu user có none goals thì fallback lấy tất cả
        summary = SavingsService.get_summary(user_id)
        if user_id and (not summary or not summary.get('goals')):
            summary = SavingsService.get_summary(None)
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

# Chức năng liên kết tài khoản đã bị xóa — templates/accounts*.html không được route tới

# ==================== AUTH ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    try:
        username = request.form['username'].strip()
        name = request.form.get('name') or None
        email = request.form.get('email') or None
        password = request.form['password']
        phone = request.form.get('phone') or None

        if User.find_by_username(username):
            flash('Tên đăng nhập đã tồn tại', 'error')
            return redirect(url_for('register'))
        if email and User.find_by_email(email):
            flash('Email đã được sử dụng', 'error')
            return redirect(url_for('register'))

        user = User.create(username, name, email, password, phone)
        session['user_id'] = user['id']
        flash('Đăng ký thành công', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    try:
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.find_by_username(username)
        if not user or not User.verify_password(user['passwordHash'], password):
            flash('Email hoặc mật khẩu không đúng', 'error')
            return redirect(url_for('login'))
        # ensure session persists
        session.permanent = True
        session['user_id'] = user['id']
        print(f"[DEBUG] login: set session user_id = {session.get('user_id')}, user.id type={type(user['id'])}")
        flash('Đăng nhập thành công', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Đăng xuất người dùng"""
    session.pop('user_id', None)
    flash('Đã đăng xuất', 'success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.find_by_id(user_id)
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
def profile_update():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    new_name = request.form.get('name') or ''
    try:
        user = User.update_name(user_id, new_name)
        flash('Cập nhật thông tin thành công', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'error')
    return redirect(url_for('profile'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return "Không tìm thấy trang", 404

@app.errorhandler(500)
def internal_error(error):
    return "Lỗi server", 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Kiểm tra database tồn tại (đọc từ env DATABASE_PATH)
    db_path = os.getenv('DATABASE_PATH', 'prisma/dev.db')
    if not os.path.exists(db_path):
         print("⚠️  Cảnh báo: Database chưa tồn tại")
         print("   Chạy: python init_db.py để tạo database")
     
    app.run(debug=True, host='0.0.0.0', port=5000)