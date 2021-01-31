import logging
logger = logging.getLogger(__name__)
def binary_search(arr, l, r, x):
    if r >= l:
        mid = int(l + (r - l) / 2)

        if arr[mid][0] == x:
            return mid, True

        if arr[mid][0] > x:
            return binary_search(arr, l, mid - 1, x)

        return binary_search(arr, mid + 1, r, x)

    return l, False


