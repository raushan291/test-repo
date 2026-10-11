def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

if __name__ == "__main__":
    # Test cases
    my_list = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    
    print(f"List: {my_list}")

    # Test 1: Target found
    target1 = 11
    result1 = binary_search(my_list, target1)
    if result1 != -1:
        print(f"Target {target1} found at index {result1}")
    else:
        print(f"Target {target1} not found")

    # Test 2: Target not found
    target2 = 4
    result2 = binary_search(my_list, target2)
    if result2 != -1:
        print(f"Target {target2} found at index {result2}")
    else:
        print(f"Target {target2} not found")

    # Test 3: Target at the beginning
    target3 = 1
    result3 = binary_search(my_list, target3)
    if result3 != -1:
        print(f"Target {target3} found at index {result3}")
    else:
        print(f"Target {target3} not found")

    # Test 4: Target at the end
    target4 = 19
    result4 = binary_search(my_list, target4)
    if result4 != -1:
        print(f"Target {target4} found at index {result4}")
    else:
        print(f"Target {target4} not found")

    # Test 5: Empty list
    empty_list = []
    target5 = 5
    result5 = binary_search(empty_list, target5)
    if result5 != -1:
        print(f"Target {target5} found in empty list at index {result5}")
    else:
        print(f"Target {target5} not found in empty list")

    # Test 6: Single element list - target found
    single_element_list = [42]
    target6 = 42
    result6 = binary_search(single_element_list, target6)
    if result6 != -1:
        print(f"Target {target6} found in single element list at index {result6}")
    else:
        print(f"Target {target6} not found in single element list")

    # Test 7: Single element list - target not found
    target7 = 100
    result7 = binary_search(single_element_list, target7)
    if result7 != -1:
        print(f"Target {target7} found in single element list at index {result7}")
    else:
        print(f"Target {target7} not found in single element list")
