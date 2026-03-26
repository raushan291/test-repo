# app/app/models.py
# This file provides a basic User class.
# In a real Flask application, this would typically be an SQLAlchemy model
# integrated with a database. For this task, it serves as a simple
# data structure for demonstration and testing.

class User:
    """
    A simple User class to represent a user in the application.
    In a real application, this would be an ORM model (e.g., SQLAlchemy).
    """
    def __init__(self, id, name, email, password_hash=None):
        """
        Initializes a new User instance.

        Args:
            id (int): A unique identifier for the user.
            name (str): The user's name (formerly username).
            email (str): The user's email address.
            password_hash (str, optional): A hashed or plain password for authentication.
                                           Defaults to None.
        """
        self.id = id
        self.name = name  # Renamed from 'username' to 'name'
        self.email = email
        self.password_hash = password_hash  # Stored as a placeholder, could be a real hash
        self.is_logged_in = False  # New attribute to track login state

    def login(self, password):
        """
        Simulates user authentication by checking the provided password against
        the stored password_hash.

        In a real application with hashed passwords, this would use a library
        like `werkzeug.security.check_password_hash(self.password_hash, password)`.
        For this simple class, we perform a direct string comparison with `password_hash`.

        Args:
            password (str): The password provided by the user attempting to log in.

        Returns:
            bool: True if login is successful (password matches), False otherwise.
        """
        if self.password_hash and self.password_hash == password:
            self.is_logged_in = True
            return True
        self.is_logged_in = False  # Ensure state is false if login fails
        return False

    def logout(self):
        """
        Resets the user's logged-in state to False.
        """
        self.is_logged_in = False

    def __repr__(self):
        """
        Returns a string representation of the User object.
        """
        return f"<User {self.name} (ID: {self.id}, LoggedIn: {self.is_logged_in})>"

# Placeholder for a database instance.
# In a real Flask-SQLAlchemy app, this would be 'db = SQLAlchemy()'.
db = None