from flask import render_template, redirect, url_for, flash, session, Blueprint
from functools import wraps
from app.models import User # Import the User class from app/models.py

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

# Dummy login_required decorator for demonstration
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Dummy Subscription class for demonstration purposes
class Subscription:
    """
    A simple class to represent a user's subscription details.
    In a real application, this would likely be an ORM model.
    """
    def __init__(self, plan_name, start_date, end_date, status):
        self.plan_name = plan_name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

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

@dashboard_bp.route('/profile')
@login_required
def profile():
    """
    Displays the logged-in user's profile, including email and subscription details.
    """
    username = session.get('username')
    user_email = session.get('user_email') # Assuming email is stored in session upon login for simplicity

    # In a real application, you would typically fetch the User object from the database
    # using session.get('user_id') or similar, then access user.email.
    # For this dummy setup, we create a User object based on session data.
    if not username or not user_email:
        flash('User data not found in session. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    user = User(id=session.get('user_id', 1), username=username, email=user_email)

    # Simulate fetching subscription data based on the username
    subscription = None
    if username == 'testuser':
        subscription = Subscription(
            plan_name="Premium Plan",
            start_date="2023-01-01",
            end_date="2024-01-01",
            status="Active"
        )
    elif username == 'pro_member':
        subscription = Subscription(
            plan_name="Pro Plan",
            start_date="2022-06-15",
            end_date="2023-06-15",
            status="Expired"
        )
    # If username is 'nosubuser' or any other, subscription remains None

    return render_template('profile.html', user=user, subscription=subscription)