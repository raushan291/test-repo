import pytest
from flask import url_for, session
from models import db, User

def test_config(app):
    """Test the application configuration."""
    assert app.config['TESTING'] is True
    assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']
    assert app.config['SECRET_KEY'] == 'your-very-secret-key-please-change-in-prod' # Default from config.py

def test_db_creation(app):
    """Test if the database tables are created."""
    with app.app_context():
        inspector = db.inspect(db.engine)
        assert 'user' in inspector.get_table_names()
        assert User.query.count() > 0 # At least the dummy user from conftest

def test_index_redirects_to_login_when_not_logged_in(client):
    """Test that the root URL redirects to login when no user is logged in."""
    response = client.get('/')
    assert response.status_code == 302
    assert 'login' in response.headers['Location'] # Checks for redirection to /auth/login

def test_index_redirects_to_dashboard_when_logged_in(client):
    """Test that the root URL redirects to dashboard when a user is logged in."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['username'] = 'test'
    
    response = client.get('/')
    assert response.status_code == 302
    assert 'dashboard' in response.headers['Location'] # Checks for redirection to /dashboard/

def test_404_error_handler(client):
    """Test the global 404 error handler."""
    response = client.get('/non-existent-page')
    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data
    assert b"Go to Homepage" in response.data

def test_500_error_handler(app, client):
    """
    Test the global 500 error handler.
    This requires simulating an internal server error.
    """
    @app.route('/cause-500')
    def cause_500():
        raise Exception("Simulated internal server error")

    response = client.get('/cause-500')
    assert response.status_code == 500
    assert b"500 - Internal Server Error" in response.data
    assert b"Something went wrong on our end" in response.data

def test_static_files_served(client):
    """Test that static files (e.g., CSS) are served correctly."""
    response = client.get('/static/style.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css; charset=utf-8'
    assert b'body {' in response.data
    assert b'.navbar {' in response.data