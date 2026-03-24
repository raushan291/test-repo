import pytest
from app import app
from auth import reset_users_for_tests, _users_db, get_user_by_username
from werkzeug.security import check_password_hash

# Test credentials
TEST_USERNAME = "testuser"
TEST_PASSWORD = "Password123"
TEST_USERNAME_2 = "anotheruser"
TEST_PASSWORD_2 = "StrongPass456"
INVALID_PASSWORD = "wrongpassword"
WEAK_PASSWORD = "pass"
MISSING_CHAR_PASSWORD = "password123" # Missing uppercase
MISSING_DIGIT_PASSWORD = "PasswordABC" # Missing digit

@pytest.fixture
def client():
    """
    Pytest fixture to configure the Flask app for testing and provide a test client.
    It ensures that the user database and app configuration are reset
    before and after each test to maintain test isolation and predictability.
    """
    app.config['TESTING'] = True  # Enable testing mode
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms if applicable
    app.config['SECRET_KEY'] = 'test_secret_key' # Ensure consistent secret key for sessions

    # Reset user database before the test starts
    reset_users_for_tests()

    with app.test_client() as client:
        with app.app_context():
            yield client             # Provide the test client to the test function

    # Reset user database after the test finishes (teardown)
    reset_users_for_tests()


def register_user(client, username, password):
    """Helper function to register a user."""
    return client.post('/auth/register', json={'username': username, 'password': password})

def login_user(client, username, password):
    """Helper function to log in a user."""
    return client.post('/auth/login', json={'username': username, 'password': password})

def logout_user(client):
    """Helper function to log out a user."""
    return client.post('/auth/logout')

# --- Test User Registration ---

def test_register_successful(client):
    """
    Tests successful user registration with valid credentials.
    Verifies status code, response message, and that the user is stored in the database.
    """
    response = register_user(client, TEST_USERNAME, TEST_PASSWORD)
    assert response.status_code == 201
    assert "User registered successfully" in response.json['message']
    assert "user_id" in response.json

    user_in_db = get_user_by_username(TEST_USERNAME)
    assert user_in_db is not None
    assert check_password_hash(user_in_db['password_hash'], TEST_PASSWORD)

def test_register_duplicate_username(client):
    """
    Tests that a user cannot register with an already existing username.
    """
    register_user(client, TEST_USERNAME, TEST_PASSWORD) # First registration
    response = register_user(client, TEST_USERNAME, TEST_PASSWORD_2) # Second registration
    assert response.status_code == 409
    assert "Username already exists" in response.json['message']
    assert len(_users_db) == 1 # Only one user should be in the DB

def test_register_missing_username(client):
    """
    Tests registration attempt with a missing username.
    """
    response = client.post('/auth/register', json={'password': TEST_PASSWORD})
    assert response.status_code == 400
    assert "Missing username or password" in response.json['message']

def test_register_missing_password(client):
    """
    Tests registration attempt with a missing password.
    """
    response = client.post('/auth/register', json={'username': TEST_USERNAME})
    assert response.status_code == 400
    assert "Missing username or password" in response.json['message']

def test_register_weak_password_length(client):
    """
    Tests registration with a password that is too short.
    """
    response = register_user(client, TEST_USERNAME, WEAK_PASSWORD)
    assert response.status_code == 400
    assert "Password does not meet complexity requirements" in response.json['message']

def test_register_weak_password_no_digit(client):
    """
    Tests registration with a password missing a digit.
    """
    response = register_user(client, TEST_USERNAME, MISSING_DIGIT_PASSWORD)
    assert response.status_code == 400
    assert "Password does not meet complexity requirements" in response.json['message']

def test_register_weak_password_no_uppercase(client):
    """
    Tests registration with a password missing an uppercase letter.
    """
    response = register_user(client, TEST_USERNAME, MISSING_CHAR_PASSWORD)
    assert response.status_code == 400
    assert "Password does not meet complexity requirements" in response.json['message']

# --- Test User Login ---

def test_login_successful(client):
    """
    Tests successful user login after registration.
    Verifies status code, response message, and that a user ID is stored in the session.
    """
    register_user(client, TEST_USERNAME, TEST_PASSWORD)
    response = login_user(client, TEST_USERNAME, TEST_PASSWORD)
    assert response.status_code == 200
    assert "Logged in successfully" in response.json['message']
    assert response.json['username'] == TEST_USERNAME

    with client.session_transaction() as sess:
        user_in_db = get_user_by_username(TEST_USERNAME)
        assert sess.get('user_id') == user_in_db['id']

def test_login_user_not_found(client):
    """
    Tests login attempt with a non-existent username.
    """
    response = login_user(client, "nonexistent", TEST_PASSWORD)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json['message']

    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_login_invalid_password(client):
    """
    Tests login attempt with a correct username but incorrect password.
    """
    register_user(client, TEST_USERNAME, TEST_PASSWORD)
    response = login_user(client, TEST_USERNAME, INVALID_PASSWORD)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json['message']

    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_login_missing_username(client):
    """
    Tests login attempt with a missing username.
    """
    response = client.post('/auth/login', json={'password': TEST_PASSWORD})
    assert response.status_code == 400
    assert "Missing username or password" in response.json['message']

def test_login_missing_password(client):
    """
    Tests login attempt with a missing password.
    """
    response = client.post('/auth/login', json={'username': TEST_USERNAME})
    assert response.status_code == 400
    assert "Missing username or password" in response.json['message']

# --- Test User Logout ---

def test_logout_successful(client):
    """
    Tests successful user logout after being logged in.
    Verifies status code, response message, and that the session is cleared.
    """
    register_user(client, TEST_USERNAME, TEST_PASSWORD)
    login_user(client, TEST_USERNAME, TEST_PASSWORD)

    with client.session_transaction() as sess:
        assert 'user_id' in sess

    response = logout_user(client)
    assert response.status_code == 200
    assert "Logged out successfully" in response.json['message']

    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_logout_when_not_logged_in(client):
    """
    Tests logout attempt when no user is currently logged in.
    The `login_required` decorator on `logout` means it should return 401.
    """
    # No prior login
    response = logout_user(client)
    assert response.status_code == 401
    assert "Authentication required" in response.json['message']

    with client.session_transaction() as sess:
        assert 'user_id' not in sess

# --- Test Protected Routes and Session Management ---

def test_access_protected_route_not_logged_in(client):
    """
    Tests accessing a protected route without logging in.
    Should return a 401 Unauthorized error.
    """
    response = client.get('/auth/protected-data')
    assert response.status_code == 401
    assert "Authentication required" in response.json['message']

def test_access_protected_route_logged_in(client):
    """
    Tests accessing a protected route after successfully logging in.
    Should return a 200 OK.
    """
    register_user(client, TEST_USERNAME, TEST_PASSWORD)
    login_user(client, TEST_USERNAME, TEST_PASSWORD)

    response = client.get('/auth/protected-data')
    assert response.status_code == 200
    assert f"Welcome, {TEST_USERNAME}! This is protected data." in response.json['message']

def test_access_protected_route_after_logout(client):
    """
    Tests accessing a protected route after logging out.
    Should return a 401 Unauthorized error.
    """
    register_user(client, TEST_USERNAME, TEST_PASSWORD)
    login_user(client, TEST_USERNAME, TEST_PASSWORD)
    logout_user(client)

    response = client.get('/auth/protected-data')
    assert response.status_code == 401
    assert "Authentication required" in response.json['message']

def test_session_cookie_management(client):
    """
    Verifies that session cookies are set on login and cleared on logout.
    """
    # 1. No session cookie initially
    response_no_session = client.get('/')
    assert 'Set-Cookie' not in response_no_session.headers or 'session' not in response_no_session.headers['Set-Cookie']

    # 2. Register and Login - session cookie should be set
    register_user(client, TEST_USERNAME, TEST_PASSWORD)
    login_response = login_user(client, TEST_USERNAME, TEST_PASSWORD)
    assert login_response.status_code == 200
    assert 'Set-Cookie' in login_response.headers
    assert 'session=' in login_response.headers['Set-Cookie']

    # 3. Access protected route with session cookie
    protected_response = client.get('/auth/protected-data')
    assert protected_response.status_code == 200

    # 4. Logout - session cookie should be cleared/expired
    logout_response = logout_user(client)
    assert logout_response.status_code == 200
    assert 'Set-Cookie' in logout_response.headers
    # Check for session cookie with 'expires=...' indicating removal
    assert 'session=' in logout_response.headers['Set-Cookie']
    assert 'expires=' in logout_response.headers['Set-Cookie'].lower() or 'max-age=0' in logout_response.headers['Set-Cookie'].lower()

    # 5. Access protected route after logout - should fail again
    re_protected_response = client.get('/auth/protected-data')
    assert re_protected_response.status_code == 401