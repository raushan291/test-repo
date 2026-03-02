def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

if __name__ == "__main__":
    while True:
        try:
            num_str = input("Enter a non-negative integer to calculate its factorial: ")
            num = int(num_str)
            if num < 0:
                print("Error: Please enter a non-negative integer.")
            else:
                print(f"The factorial of {num} is {factorial(num)}")
                break
        except ValueError:
            print("Error: Invalid input. Please enter an integer.")