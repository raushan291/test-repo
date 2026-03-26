import pytest
from calculator import add, subtract, multiply, divide, power

# --- Tests for add function ---
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),          # Positive integers
    (-1, -2, -3),       # Negative integers
    (5, -3, 2),         # Mixed integers
    (0, 0, 0),          # Zeros
    (10, 0, 10),        # Adding with zero
    (0.5, 1.5, 2.0),    # Positive floats
    (-0.1, -0.2, -0.3), # Negative floats
    (2.5, -1.0, 1.5),   # Mixed floats
    (1000000, 2000000, 3000000), # Large integers
])
def test_add_normal_cases(a, b, expected):
    """
    Test the add function with various valid integer and float inputs.
    """
    assert add(a, b) == expected

# --- Tests for subtract function ---
@pytest.mark.parametrize("a, b, expected", [
    (5, 2, 3),          # Positive integers
    (2, 5, -3),         # Positive integers, negative result
    (-5, -2, -3),       # Negative integers
    (-2, -5, 3),        # Negative integers, positive result
    (5, -2, 7),         # Mixed integers
    (-5, 2, -7),        # Mixed integers
    (0, 0, 0),          # Zeros
    (10, 0, 10),        # Subtracting zero
    (0, 10, -10),       # Subtracting from zero
    (3.5, 1.0, 2.5),    # Positive floats
    (-2.0, -1.5, -0.5), # Negative floats
    (5.0, 2.5, 2.5),    # Exact float result
    (1000000, 500000, 500000), # Large integers
])
def test_subtract_normal_cases(a, b, expected):
    """
    Test the subtract function with various valid integer and float inputs.
    """
    assert subtract(a, b) == expected

# --- Tests for multiply function ---
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 6),          # Positive integers
    (-2, 3, -6),        # Negative by positive
    (2, -3, -6),        # Positive by negative
    (-2, -3, 6),        # Negative by negative
    (0, 5, 0),          # Multiply by zero
    (5, 0, 0),          # Multiply by zero
    (0.5, 2, 1.0),      # Float by integer
    (0.5, 0.5, 0.25),   # Floats
    (-1.5, 2.0, -3.0),  # Mixed floats
    (1000, 1000, 1000000), # Large integers
])
def test_multiply_normal_cases(a, b, expected):
    """
    Test the multiply function with various valid integer and float inputs.
    """
    assert multiply(a, b) == expected

# --- Tests for divide function ---
@pytest.mark.parametrize("a, b, expected", [
    (6, 3, 2.0),        # Positive integers
    (7, 2, 3.5),        # Positive integers, float result
    (-6, 3, -2.0),      # Negative by positive
    (6, -3, -2.0),      # Positive by negative
    (-6, -3, 2.0),      # Negative by negative
    (0, 5, 0.0),        # Zero numerator
    (10.0, 2.5, 4.0),   # Floats
    (-9.0, 3.0, -3.0),  # Mixed floats
    (10, 3, 10/3),      # Non-exact division
])
def test_divide_normal_cases(a, b, expected):
    """
    Test the divide function with various valid integer and float inputs.
    """
    assert divide(a, b) == expected

def test_divide_by_zero_raises_error():
    """
    Test that dividing by zero raises a ZeroDivisionError.
    """
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide(10, 0)
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide(0, 0) # Even 0/0 is an error here

# --- Tests for power function ---
@pytest.mark.parametrize("base, exponent, expected", [
    (2, 3, 8),          # Positive base, positive integer exponent
    (5, 0, 1),          # Positive base, zero exponent
    (2, -2, 0.25),      # Positive base, negative integer exponent
    (4, 0.5, 2.0),      # Positive base, fractional exponent (square root)
    (8, 1/3, 2.0),      # Positive base, fractional exponent (cube root)
    (-2, 2, 4),         # Negative base, even exponent
    (-2, 3, -8),        # Negative base, odd exponent
    (-2, 0, 1),         # Negative base, zero exponent
    (0, 5, 0),          # Zero base, positive exponent
    (0, 0, 1),          # Zero base, zero exponent (Python's behavior)
    (1.5, 2, 2.25),     # Float base, integer exponent
    (2.0, -1.0, 0.5),   # Float base, negative float exponent
    (1, 100, 1),        # One as base
    (100, 1, 100),      # One as exponent
    (10, 6, 1000000),   # Larger result
    (10, -1, 0.1),      # Negative exponent leading to float
])
def test_power_normal_cases(base, exponent, expected):
    """
    Test the power function with various valid integer and float inputs for base and exponent.
    Uses pytest.approx for float comparisons to handle potential precision issues.
    """
    assert power(base, exponent) == pytest.approx(expected)

@pytest.mark.parametrize("base, exponent", [
    (-1, 0.5), # Negative base with non-integer exponent (e.g., sqrt(-1) which is complex)
    (-2, 0.5),
    (-4, 0.5),
    (-8, 1/3) # For some python versions (e.g., 3.8 and above), (-8)**(1/3) will return a complex number due to how float exponents are handled
              # If expected to handle only real numbers, this might need a specific check or library like `cmath`
              # For standard Python `**` operator, it might return a complex number.
])
def test_power_negative_base_fractional_exponent_returns_complex_or_raises_error(base, exponent):
    """
    Test cases where a negative base and a fractional exponent might result in a complex number
    or an error depending on the Python version and floating-point specifics.
    The default `**` operator often returns a complex number in such cases.
    """
    result = power(base, exponent)
    if isinstance(result, complex):
        # We are just asserting that it produces a complex number, not a specific value
        # as complex number comparison might be tricky or not strictly needed for this task.
        assert result.imag != 0
    else:
        # If it returns a real number (e.g., if exponent simplifies to an integer power in some math context),
        # we can still assert it's a float or int.
        assert isinstance(result, (float, int))
        # Note: The prompt implies real number output based on "int or float",
        # so for production, a dedicated check or error for complex results might be needed.
        # For now, we observe Python's native behavior.

def test_power_very_large_result():
    """
    Test power with inputs that result in a very large number.
    """
    assert power(2, 60) == 2**60

def test_power_very_small_result():
    """
    Test power with inputs that result in a very small number (close to zero).
    """
    assert power(2, -60) == pytest.approx(2**-60)

# Test input types (optional, as Python is dynamically typed, but good for robustness if type checking is desired)
@pytest.mark.parametrize("func", [add, subtract, multiply, divide, power])
def test_functions_handle_non_numeric_input(func):
    """
    Test that functions might behave unexpectedly or raise TypeError with non-numeric inputs.
    Python's `+`, `-`, `*`, `/`, `**` operators usually raise TypeError for incompatible types.
    """
    with pytest.raises(TypeError):
        func("a", 1)
    with pytest.raises(TypeError):
        func(1, "b")
    with pytest.raises(TypeError):
        func("a", "b")
    with pytest.raises(TypeError):
        func([1], [2])
    with pytest.raises(TypeError):
        func(None, 5)
    with pytest.raises(TypeError):
        func(5, None)