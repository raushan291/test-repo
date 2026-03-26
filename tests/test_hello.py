import pytest
from hello import hello_world

def test_hello_world_returns_expected_string():
    """
    Test that the hello_world function returns the exact string 'Hello, World!'.
    """
    assert hello_world() == "Hello, World!"

def test_hello_world_is_callable():
    """
    Test that the hello_world function can be called without errors.
    """
    try:
        hello_world()
    except Exception as e:
        pytest.fail(f"hello_world() raised an unexpected exception: {e}")

def test_hello_world_return_type():
    """
    Test that the hello_world function returns a string.
    """
    result = hello_world()
    assert isinstance(result, str), f"Expected return type str, but got {type(result)}"

def test_hello_world_no_arguments():
    """
    Test that the hello_world function does not accept any arguments.
    Attempting to call it with arguments should raise a TypeError.
    """
    with pytest.raises(TypeError) as excinfo:
        # Pylint might warn about too many arguments, but this is intentional for the test.
        # pylint: disable=too-many-function-args
        hello_world("some_arg")
    assert "takes 0 positional arguments but 1 was given" in str(excinfo.value) or \
           "takes no arguments but 1 was given" in str(excinfo.value)