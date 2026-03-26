# app/tests/test_models.py
import pytest
from app.app.models import User

def test_user_initialization():
    """
    Test that a User object is initialized correctly with all attributes,
    including the renamed 'name' and default 'is_logged_in'.
    """
    user = User(id=1, name="Alice Smith", email="alice@example.com", password_hash="supersecret")

    assert user.id == 1
    assert user.name == "Alice Smith"
    assert user.email == "alice@example.com"
    assert user.password_hash == "supersecret"
    assert user.is_logged_in is False

def test_user_initialization_no_password_hash():
    """
    Test user initialization without providing a password hash.
    """
    user = User(id=2, name="Bob Johnson", email="bob@example.com")
    assert user.id == 2
    assert user.name == "Bob Johnson"
    assert user.email == "bob@example.com"
    assert user.password_hash is None
    assert user.is_logged_in is False

def test_login_successful():
    """
    Test the login method with a correct password.
    """
    user = User(id=3, name="Charlie Brown", email="charlie@example.com", password_hash="my_password")
    
    assert user.login("my_password") is True
    assert user.is_logged_in is True

def test_login_failed_incorrect_password():
    """
    Test the login method with an incorrect password.
    """
    user = User(id=4, name="David Lee", email="david@example.com", password_hash="correct_password")

    assert user.login("wrong_password") is False
    assert user.is_logged_in is False # State should remain False

def test_login_failed_no_password_hash():
    """
    Test the login method when the user object has no password_hash set.
    """
    user = User(id=5, name="Eve Green", email="eve@example.com", password_hash=None)

    assert user.login("any_password") is False
    assert user.is_logged_in is False # State should remain False

def test_login_already_logged_in_correct_password():
    """
    Test attempting to log in an already logged-in user with the correct password.
    The state should remain True.
    """
    user = User(id=6, name="Frank White", email="frank@example.com", password_hash="pass123")
    user.login("pass123") # First successful login
    assert user.is_logged_in is True

    assert user.login("pass123") is True # Attempt to login again
    assert user.is_logged_in is True # State should still be True

def test_login_already_logged_in_incorrect_password():
    """
    Test attempting to log in an already logged-in user with an incorrect password.
    The state should change to False.
    """
    user = User(id=7, name="Grace Hall", email="grace@example.com", password_hash="secret_key")
    user.login("secret_key") # First successful login
    assert user.is_logged_in is True

    assert user.login("wrong_secret_key") is False # Attempt to login again with wrong password
    assert user.is_logged_in is False # State should now be False

def test_logout_successful():
    """
    Test the logout method after a user has successfully logged in.
    """
    user = User(id=8, name="Heidi Clark", email="heidi@example.com", password_hash="secure_pass")
    user.login("secure_pass") # Log in first
    assert user.is_logged_in is True

    user.logout()
    assert user.is_logged_in is False

def test_logout_when_not_logged_in():
    """
    Test the logout method when the user is not currently logged in.
    The state should remain False.
    """
    user = User(id=9, name="Ivan Petrov", email="ivan@example.com")
    assert user.is_logged_in is False # Initially not logged in

    user.logout()
    assert user.is_logged_in is False # Should remain False

def test_repr_method_logged_out():
    """
    Test the __repr__ method for correct string representation when logged out.
    """
    user_logged_out = User(id=10, name="Judy Garland", email="judy@example.com", password_hash="pw")
    expected_repr_logged_out = "<User Judy Garland (ID: 10, LoggedIn: False)>"
    assert repr(user_logged_out) == expected_repr_logged_out

def test_repr_method_logged_in():
    """
    Test the __repr__ method for correct string representation when logged in.
    """
    user_logged_in = User(id=11, name="Karl Marx", email="karl@example.com", password_hash="pw")
    user_logged_in.login("pw")
    expected_repr_logged_in = "<User Karl Marx (ID: 11, LoggedIn: True)>"
    assert repr(user_logged_in) == expected_repr_logged_in