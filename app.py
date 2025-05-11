from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from blockchain import Blockchain
from audit_log import AuditLog
from utils import hash_data
import uuid
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User file for persistent storage
USER_FILE = 'users.json'

def load_users():
    """Load users from users.json or initialize with default users."""
    default_users = {
        'student1': {'password': 'pass123', 'role': 'student', 'id': str(uuid.uuid4())},
        'faculty1': {'password': 'pass456', 'role': 'faculty', 'id': str(uuid.uuid4())},
        'admin1': {'password': 'pass789', 'role': 'admin', 'id': str(uuid.uuid4())},
        'developer1': {'password': 'pass101', 'role': 'developer', 'id': str(uuid.uuid4())}
    }
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as f:
                users = json.load(f)
                # Ensure all users have UUIDs
                for username, data in users.items():
                    if 'id' not in data:
                        data['id'] = str(uuid.uuid4())
                return users
        except (json.JSONDecodeError, IOError):
            print(f"Error loading users.json, using default users")
    # Initialize users.json with default users if file doesn't exist
    save_users(default_users)
    return default_users

def save_users(users):
    """Save users to users.json."""
    try:
        with open(USER_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except IOError as e:
        print(f"Error saving users: {e}")

users = load_users()
blockchain = Blockchain()
audit_log = AuditLog()

class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    for username, data in users.items():
        if data['id'] == user_id:
            return User(user_id, username, data['role'])
    return None

@app.template_filter('datetime')
def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(users[username]['id'], username, users[username]['role'])
            login_user(user)
            audit_log.log_action(username, 'login', f'User {username} logged in')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    audit_log.log_action(current_user.username, 'logout', f'User {current_user.username} logged out')
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return render_template('dashboard_student.html', records=blockchain.get_student_records())
    elif current_user.role == 'faculty':
        return render_template('dashboard_faculty.html', reports=blockchain.get_reports())
    elif current_user.role == 'admin':
        return render_template('dashboard_admin.html', users=users, logs=audit_log.get_logs())
    elif current_user.role == 'developer':
        attack_result = None
        attack_result_file = 'attack_results.json'
        if os.path.exists(attack_result_file):
            try:
                with open(attack_result_file, 'r') as f:
                    attack_result = json.load(f)
            except (json.JSONDecodeError, IOError):
                attack_result = None
        return render_template('dashboard_developer.html', 
                             validation=blockchain.validate_chain(), 
                             metrics=blockchain.get_quality_metrics(), 
                             logs=audit_log.get_logs(),
                             attack_result=attack_result)
    return 'Unauthorized', 403

@app.route('/student_view_records')
@login_required
def student_view_records():
    if current_user.role == 'student':
        audit_log.log_action(current_user.username, 'view_records', 'Viewed blockchain records')
        return render_template('dashboard_student.html', records=blockchain.get_student_records())
    return 'Unauthorized', 403

@app.route('/faculty_submit_report', methods=['POST'])
@login_required
def faculty_submit_report():
    if current_user.role == 'faculty':
        report_data = request.form['report_data']
        validation_result = blockchain.validate_report(report_data, current_user.username)
        if validation_result == 'valid':
            report_id = str(uuid.uuid4())
            block = blockchain.add_block(report_id, report_data, current_user.username)
            audit_log.log_action(current_user.username, 'submit_report', f'Report {report_id} submitted')
            flash('Report submitted successfully')
        else:
            flash(f'Report validation failed: {validation_result}')
    return redirect(url_for('dashboard'))

@app.route('/faculty_update_report', methods=['POST'])
@login_required
def faculty_update_report():
    if current_user.role == 'faculty':
        report_id = request.form['report_id']
        new_content = request.form['new_content']
        validation_result = blockchain.update_report(report_id, new_content, current_user.username)
        if validation_result == 'valid':
            audit_log.log_action(current_user.username, 'update_report', f'Report {report_id} updated')
            flash('Report updated successfully')
        else:
            flash(f'Report validation failed: {validation_result}')
    return redirect(url_for('dashboard'))

@app.route('/admin_add_user', methods=['POST'])
@login_required
def admin_add_user():
    if current_user.role == 'admin':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if username not in users:
            users[username] = {'password': password, 'role': role, 'id': str(uuid.uuid4())}
            save_users(users)  # Persist to users.json
            audit_log.log_action(current_user.username, 'add_user', f'User {username} added with role {role}')
            flash('User added successfully')
        else:
            flash('Username already exists')
    return redirect(url_for('dashboard'))

@app.route('/admin_remove_user', methods=['POST'])
@login_required
def admin_remove_user():
    if current_user.role == 'admin':
        username = request.form['username']
        if username in users and username != current_user.username:
            del users[username]
            save_users(users)  # Persist to users.json
            audit_log.log_action(current_user.username, 'remove_user', f'User {username} removed')
            flash('User removed successfully')
        else:
            flash('Cannot remove own account or invalid user')
    return redirect(url_for('dashboard'))

@app.route('/developer_validate_blockchain', methods=['POST'])
@login_required
def developer_validate_blockchain():
    if current_user.role == 'developer':
        attack_type = request.form.get('attack_type', 'tampering')
        attack_result = blockchain.simulate_attack(attack_type)
        audit_log.log_action(current_user.username, 'validate_blockchain', f'Blockchain validation performed: {attack_type}')
        attack_result_file = 'attack_results.json'
        try:
            with open(attack_result_file, 'w') as f:
                json.dump(attack_result, f, indent=4)
        except IOError as e:
            flash(f'Error saving attack result: {e}')
        flash(f'Validation result: {attack_result["result"]}')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)