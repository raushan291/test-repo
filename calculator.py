"""
A module providing basic arithmetic operations including addition, subtraction,
multiplication, division, and power calculation.
"""

def add(a, b):
    """
    Returns the sum of two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of a and b.
    """
    return a + b

def subtract(a, b):
    """
    Returns the difference between two numbers (a - b).

    Args:
        a (int or float): The number to subtract from.
        b (int or float): The number to subtract.

    Returns:
        int or float: The difference of a and b.
    """
    return a - b

def multiply(a, b):
    """
    Returns the product of two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of a and b.
    """
    return a * b

def divide(a, b):
    """
    Returns the division of two numbers (a / b).

    Args:
        a (int or float): The numerator.
        b (int or float): The denominator.

    Returns:
        int or float: The result of a divided by b.

    Raises:
        ZeroDivisionError: If the denominator b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def power(base, exponent):
    """
    Returns the result of a base raised to the power of an exponent (base ** exponent).

    Args:
        base (int or float): The base number.
        exponent (int or float): The exponent.

    Returns:
        int or float: The result of base raised to the power of exponent.
    """
    return base ** exponent