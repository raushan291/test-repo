from flask import Blueprint, request, jsonify, session, redirect, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools
import uuid

# A Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# In-memory user database for demonstration and testing.
# In a real application, this would be a persistent database.
# Stores: {user_id: {'username': '...', 'password_hash': '...'}}
_users_db = {}

def reset_users_for_tests():
    """Resets the in-memory user database for test isolation."""
    _users_db.clear()

def get_user_by_id(user_id):
    """Retrieves a user by their ID."""
    return _users_db.get(user_id)

def get_user_by_username(username):
    """Retrieves a user by their username."""
    for user_id, user_data in _users_db.items():
        if user_data['username'] == username:
            return {'id': user_id, **user_data}
    return None

def login_required(view):
    """Decorator to protect routes that require authentication."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            # For API endpoints, return JSON error
            if request.path.startswith('/api/') or request.path.startswith('/auth/'):
                return jsonify({'message': 'Authentication required'}), 401
            # For web pages, redirect to login
            return redirect(url_for('auth.login'))
        g.user = get_user_by_id(session['user_id'])
        if not g.user:
            session.pop('user_id', None) # Remove invalid session
            if request.path.startswith('/api/') or request.path.startswith('/auth/'):
                return jsonify({'message': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registers a new user.
    Requires 'username' and 'password' in the request JSON.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    if get_user_by_username(username):
        return jsonify({'message': 'Username already exists'}), 409

    # Password policy: minimum 8 characters, at least one digit, one uppercase, one lowercase
    if len(password) < 8 or not any(char.isdigit() for char in password) \
       or not any(char.isupper() for char in password) or not any(char.islower() for char in password):
        return jsonify({'message': 'Password does not meet complexity requirements (min 8 chars, 1 digit, 1 upper, 1 lower)'}), 400

    user_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(password)

    _users_db[user_id] = {
        'username': username,
        'password_hash': hashed_password
    }

    return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Logs in a user.
    Requires 'username' and 'password' in the request JSON.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user_data = get_user_by_username(username)

    if user_data and check_password_hash(user_data['password_hash'], password):
        session['user_id'] = user_data['id']
        return jsonify({'message': 'Logged in successfully', 'username': username}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required # Ensure only logged-in users can logout
def logout():
    """
    Logs out the current user by clearing the session.
    """
    session.pop('user_id', None)
    g.pop('user', None) # Clear user from global context
    return jsonify({'message': 'Logged out successfully'}), 200

# Example protected route (can be in app.py or another blueprint)
@auth_bp.route('/protected-data', methods=['GET'])
@login_required
def protected_data():
    """
    An example route that requires a user to be logged in to access.
    """
    return jsonify({'message': f'Welcome, {g.user["username"]}! This is protected data.'}), 200