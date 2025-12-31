#pragma once

#include <format>

template<std::size_t N = 0>
struct fixed_string {
    char value[N];

    constexpr fixed_string(char const (&sv)[N]) {
        for (std::size_t i = 0; i < N; ++i) {
            value[i] = sv[i];
        }
    }

    constexpr char const *c_str() const {
        return value;
    }
};

template<std::basic_format_string str>
struct formatter_t {
    template<typename... Args>
    constexpr auto operator()(Args &&...args) const {
        return std::format(str.c_str(), std::forward<Args>(args)...);
    }
};

template<fixed_string str>
static constexpr formatter_t<str> formatter;

template<fixed_string str>
constexpr formatter_t<str> operator""_format() {
    return formatter<str>;
}
