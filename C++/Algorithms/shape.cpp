#include <iostream>
#include <vector>

using data_t = int;

struct Square {
    size_t t;  // top
    size_t l;  // left
    size_t b;  // bottom
    size_t r;  // right
    data_t height;
};

using Shape = std::vector<Square>;

template<std::size_t M, std::size_t N>
using Matrix = data_t[M][N];

template<std::size_t M, std::size_t N>
void zeroMatrix(Matrix<M, N> &matrix) {
    for (size_t i = 0; i < M; ++i) {
        for (size_t j = 0; j < N; ++j) {
            matrix[i][j] = 0;
        }
    }
}

template<std::size_t M, std::size_t N>
void plotMatrix(Matrix<M, N> &matrix, Shape const &shape) {
    for (auto const &square : shape) {
        matrix[square.t][square.l] += square.height;
        matrix[square.t][square.r] -= square.height;
        matrix[square.b][square.l] -= square.height;
        matrix[square.b][square.r] += square.height;
    }
}

template<std::size_t M, std::size_t N>
void fillMatrix(Matrix<M, N> &matrix) {
    for (size_t i = 0; i < M; ++i) {
        for (size_t j = 1; j < N; ++j) {
            matrix[i][j] += matrix[i][j - 1];
        }
    }
    for (size_t i = 1; i < M; ++i) {
        for (size_t j = 0; j < N; ++j) {
            matrix[i][j] += matrix[i - 1][j];
        }
    }
}

template<std::size_t M, std::size_t N>
void lineMatrix(Matrix<M, N> &matrix) {
    for (size_t i = 0; i < M; ++i) {
        for (size_t j = N - 1; j > 0; --j) {
            matrix[i][j] -= matrix[i][j - 1];
        }
    }
    for (size_t i = M - 1; i > 0; --i) {
        for (size_t j = 0; j < N; ++j) {
            matrix[i][j] -= matrix[i - 1][j];
        }
    }
}

template<std::size_t M, std::size_t N>
void showMatrix(Matrix<M, N> const &matrix) {
    for (size_t i = 0; i < M; ++i) {
        for (size_t j = 0; j < N - 1; ++j) {
            std::cout << matrix[i][j] << " ";
        }
        std::cout << matrix[i][N - 1] << std::endl;
    }
}

int main() {
    Shape shape = {
        {1, 1, 4, 4, +1},
        {1, 1, 2, 2, -1},
        {3, 3, 4, 4, -1},
    };
    Matrix<5, 5> matrix = {
        {0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0},
        {0, 0, 1, 1, 1},
        {0, 0, 1, 1, 1},
        {0, 0, 1, 1, 1},
    };
    lineMatrix(matrix);
    showMatrix(matrix);
    std::cout << std::endl;
    zeroMatrix(matrix);
    plotMatrix(matrix, shape);
    fillMatrix(matrix);
    showMatrix(matrix);
    return 0;
}
