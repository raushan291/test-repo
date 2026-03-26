import pytest
from app.greet import greet

def test_greet_default_name():
    """
    Test that the greet function returns the default greeting
    when no name is provided.
    """
    assert greet() == "Hello, World!"

def test_greet_with_provided_name():
    """
    Test that the greet function returns a greeting with a
    specific name when provided.
    """
    assert greet("Alice") == "Hello, Alice!"

def test_greet_with_another_name():
    """
    Test the greet function with a different name to ensure
    it correctly incorporates the given name.
    """
    assert greet("Bob") == "Hello, Bob!"

def test_greet_with_empty_string_name():
    """
    Test that the greet function handles an empty string as a name
    by greeting the empty string.
    """
    assert greet("") == "Hello, !"

def test_greet_with_numeric_name():
    """
    Test that the greet function can handle a numeric input as a name,
    converting it to a string for the greeting.
    """
    assert greet(123) == "Hello, 123!"

def test_greet_with_special_characters_name():
    """
    Test that the greet function correctly handles names with special characters.
    """
    assert greet("Ch@rlie!") == "Hello, Ch@rlie!!"