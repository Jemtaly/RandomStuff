def network(n):
    k = 2
    while k <= n:
        j = k // 2
        while j > 0:
            for i in range(n):
                l = i ^ j
                if l > i:
                    yield i, l, i & k == 0
            j //= 2
        k *= 2
def apply(arr, net):
    for i, j, b in net:
        if (arr[i] > arr[j]) if b else (arr[i] < arr[j]):
            arr[i], arr[j] = arr[j], arr[i]
