from flask import render_template, redirect, url_for, flash, session
from dashboard import dashboard_bp
from functools import wraps

# Dummy login_required decorator for demonstration
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@login_required
def index():
    # In a real app: display user-specific data, recent activity, etc.
    return render_template('dashboard/index.html', username=session.get('username'))

@dashboard_bp.route('/settings')
@login_required
def settings():
    # In a real app: allow users to update their profile settings
    return render_template('dashboard/settings.html', username=session.get('username'))