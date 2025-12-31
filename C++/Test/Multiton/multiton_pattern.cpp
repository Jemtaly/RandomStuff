#include <unordered_set>

template<typename value_t>
using Registry = std::unordered_set<value_t *>;

template<typename value_t, Registry<value_t> &registry>
struct Variable {
    value_t val;

    template<typename... Args>
    Variable(Args &&...args)
        : val(std::forward<Args>(args)...) {
        registry.insert(&val);
    }

    ~Variable() {
        registry.erase(&val);
    }
};

#include <iostream>
#include <source_location>
#include <string>

#define __LOCATION__ CTSrcLoc(__FILE__, std::source_location::current())

struct RTSrcLoc {
    std::string file;
    int line, column;

    friend std::ostream &operator<<(std::ostream &os, RTSrcLoc const &rtl) {
        return os << rtl.file << ":" << rtl.line << ":" << rtl.column;
    }

    auto operator<=>(RTSrcLoc const &) const = default;
};

template<size_t N>
struct CTSrcLoc {
    int line, column;
    char file_str[N];

    constexpr CTSrcLoc(char const (&str)[N], std::source_location loc)
        : line(loc.line())
        , column(loc.column()) {
        for (size_t i = 0; i < N; ++i) {
            file_str[i] = str[i];
        }
    }

    operator RTSrcLoc() const {
        return RTSrcLoc(file_str, line, column);
    }
};

Registry<std::pair<RTSrcLoc const, size_t>> registry;

template<CTSrcLoc ctl>
Variable<std::pair<RTSrcLoc const, size_t>, registry> recorder{ctl, 0};

void f() {
    for (int i = 0; i < 10; ++i, ++recorder<__LOCATION__>.val.second) {
        // ...
    }
}

int main() {
    for (int i = 0; i < 10; ++i, ++recorder<__LOCATION__>.val.second) {
        // ...
    }
    for (auto &p : registry) {
        std::cout << p->first << ": " << p->second << " iterations" << std::endl;
    }
    return 0;
}
