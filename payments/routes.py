from flask import render_template, redirect, url_for, flash, session
from payments import payments_bp
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

@payments_bp.route('/')
@login_required
def index():
    return redirect(url_for('payments.subscribe'))

@payments_bp.route('/subscribe')
@login_required
def subscribe():
    # In a real app: display subscription plans, handle payment processing
    return render_template('payments/subscribe.html', username=session.get('username'))

@payments_bp.route('/history')
@login_required
def history():
    # In a real app: display user's payment history
    transactions = [
        {'id': 1, 'amount': 9.99, 'date': '2023-01-01', 'status': 'Completed'},
        {'id': 2, 'amount': 9.99, 'date': '2023-02-01', 'status': 'Completed'},
    ]
    return render_template('payments/history.html', transactions=transactions, username=session.get('username'))