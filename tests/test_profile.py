import pytest
from app import app, USERS, login_user
from flask import url_for
from unittest.mock import patch

# Fixture for the Flask test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms
    with app.test_client() as client:
        with app.app_context():
            # Any app-context specific setup can go here if needed
            yield client

# Helper function to log in a user using the test client
def login_test_user(client, username, password):
    """Simulates a POST request to the login route."""
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

def test_profile_unauthenticated_redirects_to_login(client):
    """
    Test that an unauthenticated user is redirected to the login page when accessing /profile.
    """
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/login?next=' in response.headers['Location']

    # Test with follow_redirects to check flash message on the login page
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data
    assert b'Login' in response.data # Assuming login page has "Login" text in its content

def test_profile_authenticated_displays_user_info(client):
    """
    Test that an authenticated user can access /profile and sees their information.
    """
    username = "testuser1"
    password = USERS[username]['password']
    email = USERS[username]['email']
    subscription_status = USERS[username]['subscription_status']
    payment_history = USERS[username]['payment_history']

    login_response = login_test_user(client, username, password)
    assert b'Logged in successfully!' in login_response.data
    assert b'Dashboard' in login_response.data # Should redirect to dashboard after login

    response = client.get('/profile')
    assert response.status_code == 200
    assert b'User Profile' in response.data
    assert f'Username: {username}'.encode('utf-8') in response.data
    assert f'Email: {email}'.encode('utf-8') in response.data
    assert f'Subscription Status: {subscription_status.capitalize()}'.encode('utf-8') in response.data # Check capitalized status
    
    # Check payment history details
    assert b'Payment History' in response.data
    for item in payment_history:
        assert item.encode('utf-8') in response.data

def test_profile_authenticated_no_payment_history(client):
    """
    Test that a user with no payment history sees the appropriate message.
    """
    username = "testuser2"
    password = USERS[username]['password']
    email = USERS[username]['email']
    subscription_status = USERS[username]['subscription_status']

    login_response = login_test_user(client, username, password)
    assert b'Logged in successfully!' in login_response.data

    response = client.get('/profile')
    assert response.status_code == 200
    assert b'User Profile' in response.data
    assert f'Username: {username}'.encode('utf-8') in response.data
    assert f'Email: {email}'.encode('utf-8') in response.data
    assert f'Subscription Status: {subscription_status.capitalize()}'.encode('utf-8') in response.data
    assert b'No payment history available.' in response.data # Check specific message for no history

def test_profile_logout_then_access(client):
    """
    Test that after logging out, accessing /profile correctly redirects to login.
    """
    username = "testuser1"
    password = USERS[username]['password']

    login_test_user(client, username, password)

    logout_response = client.get('/logout', follow_redirects=True)
    assert b'You have been logged out.' in logout_response.data

    profile_response = client.get('/profile', follow_redirects=True)
    assert b'Please log in to access this page.' in profile_response.data
    assert b'Login' in profile_response.data # Verify redirection to login page

@patch('app.current_user')
def test_profile_template_mock_current_user_data(mock_current_user, client):
    """
    Edge case: Test profile display with mocked current_user data to simulate various states.
    This also covers scenarios where specific data might be missing or different.
    """
    # Simulate an authenticated user with specific profile data
    mock_current_user.is_authenticated = True
    mock_current_user.username = "mockuser"
    mock_current_user.email = "mock@example.com"
    mock_current_user.subscription_status = "trial" # Custom status
    mock_current_user.payment_history = ["Trial-Invoice-001"] # Custom history

    response = client.get('/profile')
    assert response.status_code == 200
    assert b'User Profile' in response.data
    assert b'Username: mockuser' in response.data
    assert b'Email: mock@example.com' in response.data
    assert b'Subscription Status: Trial' in response.data
    assert b'Trial-Invoice-001' in response.data

@patch('app.current_user')
def test_profile_template_mock_current_user_minimal_data(mock_current_user, client):
    """
    Edge case: Test profile display with minimal mock current_user data.
    Ensures gracefully handles potentially missing data (though User class has defaults).
    """
    mock_current_user.is_authenticated = True
    mock_current_user.username = "minimal_user"
    mock_current_user.email = "N/A" # Default from User class property
    mock_current_user.subscription_status = "unknown" # Default from User class property
    mock_current_user.payment_history = [] # Default from User class property

    response = client.get('/profile')
    assert response.status_code == 200
    assert b'User Profile' in response.data
    assert b'Username: minimal_user' in response.data
    assert b'Email: N/A' in response.data
    assert b'Subscription Status: Unknown' in response.data
    assert b'No payment history available.' in response.data