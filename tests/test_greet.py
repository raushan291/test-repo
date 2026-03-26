import pytest
from app.greet import greet

def test_greet_with_no_argument():
    """
    Test that calling greet() without any arguments returns the default greeting.
    """
    assert greet() == 'Hello, World!'

def test_greet_with_none_argument():
    """
    Test that calling greet(None) explicitly returns the default greeting.
    """
    assert greet(None) == 'Hello, World!'

def test_greet_with_empty_string_argument():
    """
    Test that calling greet('') returns the default greeting, as an empty string
    is considered a "falsey" value similar to None.
    """
    assert greet('') == 'Hello, World!'

def test_greet_with_a_name():
    """
    Test that calling greet('Alice') returns a personalized greeting for Alice.
    """
    assert greet('Alice') == 'Hello, Alice!'

def test_greet_with_another_name():
    """
    Test with a different name to ensure the personalization works generally.
    """
    assert greet('Bob') == 'Hello, Bob!'

def test_greet_with_name_containing_spaces():
    """
    Test that greet handles names with spaces correctly.
    """
    assert greet('John Doe') == 'Hello, John Doe!'

def test_greet_return_type_default():
    """
    Test that the greet function returns a string when no argument is provided.
    """
    result = greet()
    assert isinstance(result, str)
    assert result == 'Hello, World!'

def test_greet_return_type_personalized():
    """
    Test that the greet function returns a string when a name is provided.
    """
    result = greet('Charlie')
    assert isinstance(result, str)
    assert result == 'Hello, Charlie!'

def test_greet_with_numeric_truthy_input():
    """
    Test that a truthy non-string input (like an integer) is handled by the f-string
    and produces a personalized greeting. While not a typical 'name', it verifies behavior.
    """
    assert greet(123) == 'Hello, 123!'

def test_greet_with_numeric_falsy_input():
    """
    Test that a falsy non-string input (like 0) correctly triggers the default greeting.
    """
    assert greet(0) == 'Hello, World!'