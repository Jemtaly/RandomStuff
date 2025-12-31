#pragma once

#include <compare>

template<typename N>
class Rational {
private:
    N n;
    N d;

    void reduce() {
        N a = n < 0 ? -n : n;
        N b = d < 0 ? -d : d;
        while (b) {
            N t = a;
            a = b;
            b = t % b;
        }
        if (d < 0) {
            a = -a;
        }
        if (a) {
            n = n / a;
            d = d / a;
        }
    }

public:
    Rational(N numerator = 0, N denominator = 1)
        : n(numerator), d(denominator) {
        reduce();
    }

    auto numerator() const {
        return n;
    }

    auto denominator() const {
        return d;
    }

    N floor() const {
        return d ? n < 0 ? (n + 1) / d - 1 : n / d : 0;
    }

    double value() const {
        return (double)n / d;
    }

    operator N() const {
        return floor();
    }

    operator double() const {
        return value();
    }

    friend Rational operator+(Rational const &r) {
        return Rational(r.n, r.d);
    }

    friend Rational operator-(Rational const &r) {
        return Rational(-r.n, r.d);
    }

    friend Rational operator~(Rational const &r) {
        return Rational(r.d, r.n);
    }

    friend Rational operator+(Rational const &l, Rational const &r) {
        return Rational(l.n * r.d + r.n * l.d, l.d * r.d);
    }

    friend Rational operator-(Rational const &l, Rational const &r) {
        return Rational(l.n * r.d - r.n * l.d, l.d * r.d);
    }

    friend Rational operator*(Rational const &l, Rational const &r) {
        return Rational(l.n * r.n, l.d * r.d);
    }

    friend Rational operator/(Rational const &l, Rational const &r) {
        return Rational(l.n * r.d, r.n * l.d);
    }

    friend Rational operator%(Rational const &l, Rational const &r) {
        return l - (l / r).floor() * r;
    }

    friend bool operator==(Rational const &l, Rational const &r) {
        return l.n * r.d == r.n * l.d;
    }

    friend auto operator<=>(Rational const &l, Rational const &r) {
        return l.n * r.d <=> r.n * l.d;
    }

    template<typename T>
    Rational &operator+=(T const &r) {
        return *this = *this + r;
    }

    template<typename T>
    Rational &operator-=(T const &r) {
        return *this = *this - r;
    }

    template<typename T>
    Rational &operator*=(T const &r) {
        return *this = *this * r;
    }

    template<typename T>
    Rational &operator/=(T const &r) {
        return *this = *this / r;
    }

    template<typename T>
    Rational &operator%=(T const &r) {
        return *this = *this % r;
    }
};
