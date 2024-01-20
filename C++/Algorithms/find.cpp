#include <iostream>
#include <utility>
void getNthNum(int *beg, int *end, int *idx) {
    // time complexity: O(n)
    int pivot = *beg;
    int *l = beg;
    int *r = end;
    int *m = beg;
    while (m < r) {
        if (*m == pivot) {
            m++;
        } else if (*m < pivot) {
            std::swap(*m, *l);
            l++;
            m++;
        } else if (*m > pivot) {
            r--;
            std::swap(*m, *r);
        }
    }
    if (idx <  l) {
        getNthNum(beg, l, idx);
    }
    if (idx >= r) {
        getNthNum(r, end, idx);
    }
}
void quickSort(int *beg, int *end) {
    // time complexity: O(nlogn)
    if (end == beg) {
        return;
    }
    int pivot = *beg;
    int *l = beg;
    int *r = end;
    int *m = beg;
    while (m < r) {
        if (*m == pivot) {
            m++;
        } else if (*m < pivot) {
            std::swap(*m, *l);
            l++;
            m++;
        } else if (*m > pivot) {
            r--;
            std::swap(*m, *r);
        }
    }
    quickSort(beg, l);
    quickSort(r, end);
}
int *lowerBound(int *beg, int *end, int tar) {
    // time complexity: O(logn)
    if (end == beg) {
        return beg;
    }
    int *mid = beg + (end - beg) / 2;
    if (*mid < tar) {
        return lowerBound(mid + 1, end, tar);
    } else {
        return lowerBound(beg, mid + 0, tar);
    }
}
int *upperBound(int *beg, int *end, int tar) {
    // time complexity: O(logn)
    if (end == beg) {
        return beg;
    }
    int *mid = beg + (end - beg) / 2;
    if (*mid > tar) {
        return upperBound(beg, mid + 0, tar);
    } else {
        return upperBound(mid + 1, end, tar);
    }
}
int main() {
    int arr[] = {3, 6, 4, 2, 3, 2, 5, 0, 2};
    int *beg = arr;
    int *end = arr + sizeof(arr) / sizeof(int);
    quickSort(beg, end);
    for (auto i : arr) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    std::cout << "lowerBound(1) = " << lowerBound(beg, end, 1) - beg << std::endl;
    std::cout << "upperBound(1) = " << upperBound(beg, end, 1) - beg << std::endl;
    std::cout << "lowerBound(3) = " << lowerBound(beg, end, 3) - beg << std::endl;
    std::cout << "upperBound(3) = " << upperBound(beg, end, 3) - beg << std::endl;
    return 0;
}
