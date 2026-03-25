from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os

# Initialize the Flask application
app = Flask(__name__)

# A strong secret key is crucial for session security in production.
# For testing, a placeholder is used.
app.config['SECRET_KEY'] = 'a_very_secret_key_for_testing'
app.config['LOGIN_DISABLED'] = False  # Ensure Flask-Login is enabled by default

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the view function for logging in

# --- Mock User Data (In a real application, this would come from a database) ---
USERS = {
    "testuser1": {
        "id": "testuser1",
        "password": "password1",
        "email": "test1@example.com",
        "subscription_status": "active",
        "payment_history": ["Invoice-2023-01", "Invoice-2023-02", "Invoice-2023-03"],
        "is_active": True,
        "is_authenticated": True
    },
    "testuser2": {
        "id": "testuser2",
        "password": "password2",
        "email": "test2@example.com",
        "subscription_status": "inactive",
        "payment_history": [],
        "is_active": True,
        "is_authenticated": True
    }
}

class User(UserMixin):
    """
    Custom User class for Flask-Login, representing a user from our mock database.
    """
    def __init__(self, user_id):
        self.id = user_id
        self.username = user_id
        self.data = USERS.get(user_id, {})
        # UserMixin properties
        self.is_active = self.data.get("is_active", False)
        self.is_authenticated = self.data.get("is_authenticated", False)

    def get_id(self):
        """Returns the unique ID of the user for Flask-Login."""
        return str(self.id)

    @property
    def subscription_status(self):
        """Returns the user's subscription status."""
        return self.data.get('subscription_status', 'unknown')

    @property
    def payment_history(self):
        """Returns the user's payment history."""
        return self.data.get('payment_history', [])

    @property
    def email(self):
        """Returns the user's email."""
        return self.data.get('email', 'N/A')

# Flask-Login user_loader callback
@login_manager.user_loader
def load_user(user_id):
    """
    Given a user ID, return the corresponding User object.
    This is used by Flask-Login to reload the user object from the session.
    """
    if user_id in USERS:
        return User(user_id)
    return None

# --- Routes ---
@app.route('/')
def index():
    """
    Handles the root URL. Redirects authenticated users to their dashboard,
    otherwise shows the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    - GET: Displays the login form.
    - POST: Processes login credentials. On success, logs in the user and
            redirects to the dashboard or a `next` page. On failure, flashes an error.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = USERS.get(username)
        if user_data and user_data['password'] == password:
            user = User(username)
            login_user(user) # Log the user in
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required # Ensures only logged-in users can access this
def logout():
    """
    Handles user logout. Logs the current user out and redirects to the login page.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required # Ensures only logged-in users can access this
def dashboard():
    """
    Displays the user's dashboard. This route is protected and requires authentication.
    """
    # current_user is available because of the @login_required decorator
    return render_template('dashboard.html', user=current_user)

@app.route('/profile')
@login_required # Ensures only logged-in users can access this
def profile():
    """
    Displays the user's profile information. This route is protected and requires authentication.
    """
    return render_template('profile.html', user=current_user)

@login_manager.unauthorized_handler
def unauthorized():
    """
    Callback for Flask-Login when an unauthenticated user tries to access a @login_required route.
    Flashes a message and redirects them to the login page, preserving the intended destination.
    """
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login', next=request.url))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist for local running
    os.makedirs('templates', exist_ok=True)
    # This block allows the Flask application to be run directly using `python dashboard.py`.\
    # `debug=True` enables the debugger and auto-reloader for development.
    # For production deployment, a WSGI server (e.g., Gunicorn, uWSGI) should be used.
    app.run(debug=True, port=5001)