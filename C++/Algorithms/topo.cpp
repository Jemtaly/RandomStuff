#include <iostream>
#include <functional>
template <int N>
bool topologicalSort(bool e[N][N], int r[N]) {
    int d[N] = {}; // in-degree
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (e[i][j]) {
                d[j]++;
            }
        }
    }
    int h = 0, t = 0;
    for (int i = 0; i < N; i++) {
        if (d[i] == 0) {
            r[t++] = i;
        }
    }
    while (h < t) {
        int i = r[h++];
        for (int j = 0; j < N; j++) {
            if (e[i][j] && --d[j] == 0) {
                r[t++] = j;
            }
        }
    }
    return t == N;
}
template <int N>
bool topologicalFind(bool e[N][N]) {
    char vis[N] = {}; // 0: unvisited, 1: visiting, 2: visited
    std::function<bool(int)> dfs = [&](int i) {
        vis[i] = 1;
        for (int j = 0; j < N; j++) {
            if (e[i][j] && (vis[j] == 1 || vis[j] == 0 && dfs(j) == false)) {
                return false;
            }
        }
        vis[i] = 2;
        return true;
    };
    for (int i = 0; i < N; i++) {
        if (vis[i] == 0 && dfs(i) == false) {
            return false;
        }
    }
    return true;
}
int main() {
    bool e[6][6] = {
        {0, 0, 0, 1, 1, 0},
        {0, 0, 1, 0, 0, 0},
        {0, 0, 0, 1, 0, 0},
        {0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 1},
        {0, 0, 0, 1, 0, 0},
    };
    int r[6];
    std::cout << std::boolalpha << topologicalFind<6>(e) << std::endl;
    std::cout << std::boolalpha << topologicalSort<6>(e, r) << std::endl;
    for (int i = 0; i < 6; i++) {
        std::cout << r[i] << ' ';
    }
    std::cout << std::endl;
    return 0;
}
