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
    my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    target_element = 7
    result = binary_search(my_list, target_element)

    if result != -1:
        print(f"Element {target_element} is present at index {result}")
    else:
        print(f"Element {target_element} is not present in the list")
