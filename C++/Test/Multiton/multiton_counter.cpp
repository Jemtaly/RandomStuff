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

#include <map>

struct Recorder {
private:
    static inline std::map<RTSrcLoc, Recorder const *> registry;

    Recorder(RTSrcLoc &&rtl) {
        registry.emplace(rtl, this);
    }

public:
    size_t val = 0;
    template<CTSrcLoc ctl>
    static inline Recorder recorder{ctl};

    static auto const &all() {
        return registry;
    }
};

void f() {
    for (int i = 0; i < 10; ++i, ++Recorder::recorder<__LOCATION__>.val) {
        // ...
    }
}

int main() {
    for (int i = 0; i < 10; ++i, ++Recorder::recorder<__LOCATION__>.val) {
        // ...
    }
    for (auto &p : Recorder::all()) {
        std::cout << p.first << ": " << p.second->val << " iterations" << std::endl;
    }
    return 0;
}
