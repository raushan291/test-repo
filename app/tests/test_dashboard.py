import pytest
from flask import Flask
from flask_login import current_user, logout_user
import os
import sys

# Add the parent directory to the system path to allow importing 'dashboard'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dashboard import app, USERS, login_manager, User # Import the Flask app, USERS, login_manager, and User class

@pytest.fixture
def client():
    """
    Configures the Flask application for testing and provides a test client.
    It ensures that Flask-Login is in a predictable state before and after each test.
    """
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for easier testing of POST forms
    app.config['LOGIN_DISABLED'] = False # Ensure login is not globally disabled

    with app.test_client() as client:
        with app.app_context():
            # Ensure no user is logged in at the start of each test
            if current_user.is_authenticated:
                logout_user() # Attempt to log out if a user somehow persisted from a previous test

        yield client # Provide the client to the tests

        with app.app_context():
            # Ensure logout after each test to clean up session
            if current_user.is_authenticated:
                logout_user()

def login_test_user(client, username, password):
    """
    Helper function to log in a user by sending a POST request to the /login endpoint.
    It follows redirects by default.
    """
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

def logout_test_user(client):
    """
    Helper function to log out a user by sending a GET request to the /logout endpoint.
    It follows redirects by default.
    """
    return client.get('/logout', follow_redirects=True)

def test_index_page_redirects_authenticated_to_dashboard(client):
    """
    Test that the root URL ('/') redirects an authenticated user to the dashboard.
    """
    login_test_user(client, "testuser1", "password1")
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, testuser1!' in response.data
    assert b'Your Dashboard' in response.data

def test_index_page_shows_login_for_unauthenticated(client):
    """
    Test that the root URL ('/') shows the login page for an unauthenticated user.
    """
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'username' in response.data
    assert b'password' in response.data

def test_dashboard_access_unauthenticated_redirects_to_login(client):
    """
    Test that accessing the dashboard without authentication redirects to the login page
    and displays a flash message.
    """
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302 # Expect a redirect
    assert '/login?next=' in response.headers['Location'] # Expect redirect to login with next parameter

    # Follow the redirect to check the content of the login page
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Please log in to access this page.' in response.data # Verify flash message

def test_login_page_loads_correctly(client):
    """
    Test that the /login page loads successfully and contains the necessary form elements.
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'<form method="POST" action="/login">' in response.data
    assert b'username' in response.data
    assert b'password' in response.data
    assert b'Log In</button>' in response.data

def test_login_successful_redirects_to_dashboard_with_flash(client):
    """
    Test that a successful login with valid credentials redirects to the dashboard
    and displays a success flash message.
    """
    username = "testuser1"
    password = "password1"
    response = login_test_user(client, username, password)

    assert response.status_code == 200 # After following redirect to dashboard
    assert f'Welcome, {username}!'.encode() in response.data
    assert b'Subscription Status:' in response.data
    assert b'Logged in successfully.' in response.data # Check for flash message

def test_login_unsuccessful_shows_error_flash(client):
    """
    Test that an unsuccessful login with invalid credentials shows an error message
    on the login page.
    """
    username = "testuser1"
    invalid_password = "wrong_password"
    response = client.post('/login', data={'username': username, 'password': invalid_password}, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data # Should be back on the login page
    assert b'Invalid username or password.' in response.data # Check for flash message
    assert b'Welcome,' not in response.data # Should not be on dashboard

def test_dashboard_access_authenticated_loads_correctly(client):
    """
    Test that an authenticated user can access their dashboard and it loads correctly.
    """
    login_test_user(client, "testuser1", "password1")
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Welcome, testuser1!' in response.data
    assert b'Your Dashboard' in response.data
    assert b'Manage Subscription' in response.data

def test_dashboard_displays_correct_user_specific_data(client):
    """
    Test that the dashboard displays the correct user-specific data (email, subscription status,
    and payment history) for 'testuser1'.
    """
    username = "testuser1"
    password = "password1"
    user_data = USERS[username]

    login_test_user(client, username, password)
    response = client.get('/dashboard')

    assert response.status_code == 200
    assert f'Welcome, {username}!'.encode() in response.data
    assert f'Email: {user_data["email"]}'.encode() in response.data
    assert f'Subscription Status: {user_data["subscription_status"].capitalize()}'.encode() in response.data

    # Check for payment history specific to testuser1
    if user_data["payment_history"]:
        for item in user_data["payment_history"]:
            assert item.encode() in response.data
    else:
        assert b'No payment history available.' in response.data

def test_dashboard_displays_correct_data_for_user_with_no_payments(client):
    """
    Test that the dashboard correctly handles and displays data for a user
    with an inactive subscription and no payment history ('testuser2').
    """
    username2 = "testuser2"
    password2 = "password2"
    user_data2 = USERS[username2]

    login_test_user(client, username2, password2)
    response2 = client.get('/dashboard')

    assert response2.status_code == 200
    assert f'Welcome, {username2}!'.encode() in response2.data
    assert f'Email: {user_data2["email"]}'.encode() in response2.data
    assert f'Subscription Status: {user_data2["subscription_status"].capitalize()}'.encode() in response2.data
    assert b'No payment history available.' in response2.data # Verify text for no history

def test_logout_successful_redirects_to_login_with_flash(client):
    """
    Test that logging out redirects to the login page and displays a logout flash message.
    """
    login_test_user(client, "testuser1", "password1") # Log in first

    response = logout_test_user(client)
    assert response.status_code == 200 # After following redirect to login
    assert b'Login' in response.data
    assert b'You have been logged out.' in response.data # Check for flash message

    # Verify that the user is indeed logged out by trying to access dashboard
    response_after_logout = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in response_after_logout.data # Should be redirected back to login
    assert b'Please log in to access this page.' in response_after_logout.data # Unauthorized flash

def test_logout_when_not_authenticated_redirects_to_login(client):
    """
    Test that attempting to access the /logout endpoint when not authenticated
    redirects to the login page with an unauthorized message.
    """
    # Ensure no user is logged in
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302 # Expect redirect

    response = client.get('/logout', follow_redirects=True) # Follow redirect
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Please log in to access this page.' in response.data # Unauthorized flash message

def test_interactive_element_present_on_dashboard(client):
    """
    Test that the 'Manage Subscription' interactive button is present on the dashboard,
    ensuring core interactive elements are rendered.
    """
    login_test_user(client, "testuser1", "password1")
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'<button id="manage-subscription-button"' in response.data
    assert b'Manage Subscription</button>' in response.data

# --- New Test Cases for User Profile Page ---

def test_profile_access_unauthenticated_redirects_to_login(client):
    """
    Test that accessing the /profile page without authentication redirects to the login page (HTTP 302).
    """
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302 # Expect a redirect
    assert '/login?next=http%3A%2F%2Flocalhost%2Fprofile' in response.headers['Location'] # Expect redirect to login with next parameter

    # Follow the redirect to check the content of the login page
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Please log in to access this page.' in response.data # Verify flash message

def test_profile_access_authenticated_loads_correctly_active_subscription(client):
    """
    Test that a logged-in user with an active subscription can access /profile
    and that their email and 'Active' subscription status are displayed.
    """
    username = "testuser1"
    password = "password1"
    user_data = USERS[username]

    login_test_user(client, username, password)
    response = client.get('/profile')

    assert response.status_code == 200
    assert f'User Profile for {username}'.encode() in response.data
    assert f'Email: {user_data["email"]}'.encode() in response.data
    assert b'Subscription Status: <span class="badge badge-success">Active</span>' in response.data
    assert b'Invoice-2023-01' in response.data # Check for payment history

def test_profile_access_authenticated_loads_correctly_inactive_subscription(client):
    """
    Test that a logged-in user with an inactive subscription can access /profile
    and that their email and 'Inactive' subscription status are displayed.
    """
    username = "testuser2"
    password = "password2"
    user_data = USERS[username]

    login_test_user(client, username, password)
    response = client.get('/profile')

    assert response.status_code == 200
    assert f'User Profile for {username}'.encode() in response.data
    assert f'Email: {user_data["email"]}'.encode() in response.data
    assert b'Subscription Status: <span class="badge badge-warning">Inactive</span>' in response.data
    assert b'No payment history available.' in response.data # Check for no payment history