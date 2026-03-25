# app/models.py
# This file provides a basic User class.
# In a real Flask application, this would typically be an SQLAlchemy model
# integrated with a database. For this task, it serves as a simple
# data structure for demonstration and testing.

class User:
    """
    A simple User class to represent a user in the application.
    In a real application, this would be an ORM model (e.g., SQLAlchemy).
    """
    def __init__(self, id, username, email, password_hash=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash # Stored as a placeholder

    def __repr__(self):
        return f"<User {self.username} (ID: {self.id})>"

# Placeholder for a database instance.
# In a real Flask-SQLAlchemy app, this would be 'db = SQLAlchemy()'.
db = None