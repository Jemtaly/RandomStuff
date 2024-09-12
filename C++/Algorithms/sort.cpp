#include <iostream>
#include <utility>

void bubbleSort(int a[], int n) {
    // time complexity: O(n^2)
    for (int i = 0; i < n; i++) {
        for (int j = i; j > 0 && a[j] < a[j - 1]; j--) {
            std::swap(a[j], a[j - 1]);
        }
    }
}

void chooseSort(int a[], int n) {
    // time complexity: O(n^2)
    for (int i = 0; i < n; i++) {
        int k = i;
        for (int j = i; j < n; j++) {
            if (a[j] < a[k]) {
                k = j;
            }
        }
        std::swap(a[i], a[k]);
    }
}

void shiftUp(int a[], int i) {
    // time complexity: O(logn)
    while (i > 0) {
        int p = (i - 1) / 2;
        if (a[p] < a[i]) {
            std::swap(a[p], a[i]);
            i = p;
        } else {
            break;
        }
    }
}

void shiftDown(int a[], int n, int i) {
    // time complexity: O(logn)
    while (1) {
        int l = 2 * i + 1;
        int r = 2 * i + 2;
        int k = i;
        if (l < n && a[l] > a[k]) {
            k = l;
        }
        if (r < n && a[r] > a[k]) {
            k = r;
        }
        if (k != i) {
            std::swap(a[k], a[i]);
            i = k;
        } else {
            break;
        }
    }
}

void heapSort(int a[], int n) {
    // time complexity: O(n)
    for (int i = n - 1; i >= 0; i--) {
        shiftDown(a, n, i);
    }
    // time complexity: O(nlogn)
    for (int i = n - 1; i >= 0; i--) {
        std::swap(a[0], a[i]);
        shiftDown(a, i, 0);
    }
}

int main() {
    int a[] = {3, 2, 1, 4, 5, 6, 7};
    heapSort(a, 7);
    for (auto i : a) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return 0;
}
