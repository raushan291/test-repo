import pytest
from flask import session
from app import create_app
from app.dashboard.routes import dashboard_bp # Import blueprint to ensure routes are registered

# Dummy Blueprints and routes needed for base.html url_for calls
# In a real app, these would be in their respective files.
# For testing purposes, we define minimal versions here.
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')
payments_bp = Blueprint('payments', __name__, template_folder='templates')

@auth_bp.route('/login')
def login_route():
    return "Login Page"

@auth_bp.route('/register')
def register_route():
    return "Register Page"

@auth_bp.route('/logout')
def logout_route():
    return "Logout Page"

@payments_bp.route('/subscribe')
def subscribe_route():
    return "Subscribe Page"

@payments_bp.route('/history')
def history_route():
    return "History Page"


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms if any

    # Register dummy blueprints that base.html might link to
    # These are needed so url_for('auth.login') etc. don't raise BuildErrors
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(payments_bp, url_prefix='/payments')

    with app.test_client() as client:
        with app.app_context():
            yield client

def login_test_user(client, username='testuser', email='testuser@example.com', user_id=1):
    """Simulates a successful login by setting session variables."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['username'] = username
        sess['user_email'] = email
        sess['user_id'] = user_id
    # No actual POST to login route, direct session manipulation

def logout_test_user(client):
    """Clears session variables to simulate logout."""
    with client.session_transaction() as sess:
        sess.clear()

def test_profile_page_redirects_if_not_logged_in(client):
    """
    Test that accessing the profile page without being logged in
    redirects to the login page.
    """
    response = client.get('/dashboard/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
    # Check flash message if desired, but redirection is primary.
    # response = client.get('/dashboard/profile', follow_redirects=True)
    # assert b'Please log in to access this page.' in response.data

def test_profile_page_displays_user_and_active_subscription(client):
    """
    Test that the profile page correctly displays user details and
    an active subscription.
    """
    login_test_user(client, username='testuser', email='testuser@example.com', user_id=1)
    response = client.get('/dashboard/profile')
    assert response.status_code == 200
    assert b"User Profile" in response.data
    assert b"testuser@example.com" in response.data
    assert b"Username: testuser" in response.data
    assert b"Premium Plan" in response.data
    assert b"Status: <span class=\"badge bg-success\">Active</span>" in response.data
    assert b"Start Date: 2023-01-01" in response.data
    assert b"End Date: 2024-01-01" in response.data
    assert b"Manage Subscription" in response.data
    assert b"Browse Subscription Plans" not in response.data # Ensure 'no subscription' message is not present

def test_profile_page_displays_user_with_no_subscription(client):
    """
    Test that the profile page correctly displays user details and
    the message for no active subscription.
    """
    login_test_user(client, username='nosubuser', email='nosubuser@example.com', user_id=2)
    response = client.get('/dashboard/profile')
    assert response.status_code == 200
    assert b"User Profile" in response.data
    assert b"nosubuser@example.com" in response.data
    assert b"Username: nosubuser" in response.data
    assert b"You do not have an active subscription." in response.data
    assert b"Browse Subscription Plans" in response.data
    assert b"Premium Plan" not in response.data # Ensure subscription details are not present

def test_profile_page_displays_user_with_expired_subscription(client):
    """
    Test that the profile page correctly displays user details and
    an expired subscription.
    """
    login_test_user(client, username='pro_member', email='pro@example.com', user_id=3)
    response = client.get('/dashboard/profile')
    assert response.status_code == 200
    assert b"User Profile" in response.data
    assert b"pro@example.com" in response.data
    assert b"Username: pro_member" in response.data
    assert b"Pro Plan" in response.data
    assert b"Status: <span class=\"badge bg-danger\">Expired</span>" in response.data
    assert b"Start Date: 2022-06-15" in response.data
    assert b"End Date: 2023-06-15" in response.data
    assert b"Manage Subscription" in response.data
    assert b"You do not have an active subscription." not in response.data

def test_profile_page_handles_missing_user_data_in_session(client):
    """
    Test that the profile page redirects if essential user data
    (like username or email) is missing from the session.
    """
    with client.session_transaction() as sess:
        sess['logged_in'] = True # Only logged_in is set, no username/email
    
    response = client.get('/dashboard/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
    # Check flash message after redirection
    # response_followed = client.get('/dashboard/profile', follow_redirects=True)
    # assert b'User data not found in session.' in response_followed.data