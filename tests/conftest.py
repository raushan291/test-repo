import pytest
from app import create_app
from models import db, User
from config import TestingConfig
import os

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    _app = create_app(config_name='testing')

    with _app.app_context():
        # Ensure the test database is clean
        db.drop_all()
        db.create_all()

        # Add a dummy user for testing
        dummy_user = User(username='test', email='test@example.com', password_hash='password')
        db.session.add(dummy_user)
        db.session.commit()

        yield _app

        # Clean up after all tests are done
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        # Before each test function, clear the session
        with client.session_transaction() as sess:
            sess.clear()
        yield client