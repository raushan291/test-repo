def add(a, b):
    """
    Adds two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of a and b.
    """
    return a + b

def subtract(a, b):
    """
    Subtracts the second number from the first.

    Args:
        a (int or float): The number to subtract from.
        b (int or float): The number to subtract.

    Returns:
        int or float: The difference between a and b.
    """
    return a - b

def multiply(a, b):
    """
    Multiplies two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of a and b.
    """
    return a * b

def divide(a, b):
    """
    Divides the first number by the second.

    Args:
        a (int or float): The dividend.
        b (int or float): The divisor.

    Returns:
        int or float: The quotient of a divided by b.

    Raises:
        ValueError: If the divisor b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b