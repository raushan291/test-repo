import pytest
from calculator import add, subtract, multiply, divide

# --- Test cases for add function ---

def test_add_two_positive_integers():
    """Test adding two positive integers."""
    assert add(2, 3) == 5

def test_add_positive_and_negative_integer():
    """Test adding a positive and a negative integer."""
    assert add(5, -3) == 2

def test_add_two_negative_integers():
    """Test adding two negative integers."""
    assert add(-2, -3) == -5

def test_add_zero_to_integer():
    """Test adding zero to an integer."""
    assert add(7, 0) == 7
    assert add(0, -4) == -4

def test_add_two_positive_floats():
    """Test adding two positive floating-point numbers."""
    assert add(2.5, 3.5) == 6.0

def test_add_integer_and_float():
    """Test adding an integer and a floating-point number."""
    assert add(2, 3.5) == 5.5
    assert add(3.5, 2) == 5.5

def test_add_large_numbers():
    """Test adding large numbers."""
    assert add(1000000, 2000000) == 3000000

# --- Test cases for subtract function ---

def test_subtract_two_positive_integers():
    """Test subtracting two positive integers."""
    assert subtract(5, 3) == 2

def test_subtract_positive_from_negative_integer():
    """Test subtracting a positive integer from a negative integer."""
    assert subtract(-5, 3) == -8

def test_subtract_negative_from_positive_integer():
    """Test subtracting a negative integer from a positive integer."""
    assert subtract(5, -3) == 8

def test_subtract_two_negative_integers():
    """Test subtracting two negative integers."""
    assert subtract(-5, -3) == -2

def test_subtract_zero_from_integer():
    """Test subtracting zero from an integer."""
    assert subtract(7, 0) == 7

def test_subtract_integer_from_zero():
    """Test subtracting an integer from zero."""
    assert subtract(0, 7) == -7

def test_subtract_two_positive_floats():
    """Test subtracting two positive floating-point numbers."""
    assert subtract(5.5, 2.5) == 3.0

def test_subtract_integer_and_float():
    """Test subtracting an integer and a float."""
    assert subtract(5, 2.5) == 2.5
    assert subtract(5.5, 2) == 3.5

# --- Test cases for multiply function ---

def test_multiply_two_positive_integers():
    """Test multiplying two positive integers."""
    assert multiply(2, 3) == 6

def test_multiply_positive_and_negative_integer():
    """Test multiplying a positive and a negative integer."""
    assert multiply(5, -3) == -15

def test_multiply_two_negative_integers():
    """Test multiplying two negative integers."""
    assert multiply(-2, -3) == 6

def test_multiply_by_zero():
    """Test multiplying by zero."""
    assert multiply(7, 0) == 0
    assert multiply(0, -4) == 0
    assert multiply(0.5, 0) == 0.0

def test_multiply_by_one():
    """Test multiplying by one."""
    assert multiply(7, 1) == 7
    assert multiply(-4, 1) == -4

def test_multiply_two_positive_floats():
    """Test multiplying two positive floating-point numbers."""
    assert multiply(2.5, 2.0) == 5.0

def test_multiply_integer_and_float():
    """Test multiplying an integer and a float."""
    assert multiply(2, 3.5) == 7.0
    assert multiply(3.5, 2) == 7.0

# --- Test cases for divide function ---

def test_divide_two_positive_integers():
    """Test dividing two positive integers."""
    assert divide(6, 3) == 2.0

def test_divide_positive_by_negative_integer():
    """Test dividing a positive by a negative integer."""
    assert divide(6, -3) == -2.0

def test_divide_negative_by_positive_integer():
    """Test dividing a negative by a positive integer."""
    assert divide(-6, 3) == -2.0

def test_divide_two_negative_integers():
    """Test dividing two negative integers."""
    assert divide(-6, -3) == 2.0

def test_divide_by_one():
    """Test dividing by one."""
    assert divide(7, 1) == 7.0
    assert divide(-4, 1) == -4.0

def test_divide_zero_by_nonzero():
    """Test dividing zero by a non-zero number."""
    assert divide(0, 5) == 0.0
    assert divide(0, -5.0) == 0.0

def test_divide_two_positive_floats():
    """Test dividing two positive floating-point numbers."""
    assert divide(7.5, 2.5) == 3.0

def test_divide_integer_by_float():
    """Test dividing an integer by a float."""
    assert divide(7, 2.0) == 3.5
    assert divide(7.0, 2) == 3.5

def test_divide_by_zero_raises_value_error():
    """Test that dividing by zero raises a ValueError."""
    with pytest.raises(ValueError) as excinfo:
        divide(5, 0)
    assert "Cannot divide by zero." in str(excinfo.value)

def test_divide_zero_by_zero_raises_value_error():
    """Test that dividing zero by zero raises a ValueError."""
    with pytest.raises(ValueError) as excinfo:
        divide(0, 0)
    assert "Cannot divide by zero." in str(excinfo.value)

def test_divide_result_precision():
    """Test division with results that are not whole numbers."""
    assert divide(10, 3) == pytest.approx(3.3333333333333335)
    assert divide(1, 7) == pytest.approx(0.14285714285714285)

def test_divide_large_numbers():
    """Test division with large numbers."""
    assert divide(1000000, 2) == 500000.0
    assert divide(123456789, 3) == 41152263.0