#pragma once
#include <algorithm>
#include <string>
#include <vector>
class Rational {
private:
	int n;
	int d;
	void reduce() {
		int a = n < 0 ? -n : n;
		int b = d;
		while (b) {
			int t = a;
			a = b;
			b = t % b;
		}
		if (a) {
			n /= a;
			d /= a;
		}
	}
	static constexpr char str36[36] = {
		'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B',
		'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
		'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
	};
public:
	Rational(int const &numerator = 0, int const &denominator = 1) {
		if (denominator < 0) {
			n = -numerator;
			d = -denominator;
		} else {
			n = numerator;
			d = denominator;
		}
		reduce();
	}
	auto const &numerator() const {
		return n;
	}
	auto const &denominator() const {
		return d;
	}
	int floor() const {
		return d ? n < 0 ? (n + 1) / d - 1 : n / d : 0;
	}
	double value() const {
		return (double)n / d;
	}
	operator int() const {
		return floor();
	}
	operator double() const {
		return value();
	}
	inline std::string decimal(uint8_t const &base = 10) const;
	static inline Rational from_dec(std::string const &str);
	static inline Rational from_fra(std::string const &str);
	friend inline Rational operator+(Rational const &);
	friend inline Rational operator-(Rational const &);
	friend inline Rational operator~(Rational const &);
	friend inline Rational operator+(Rational const &, Rational const &);
	friend inline Rational operator+(Rational const &, int const &);
	friend inline Rational operator+(int const &, Rational const &);
	friend inline Rational operator-(Rational const &, Rational const &);
	friend inline Rational operator-(Rational const &, int const &);
	friend inline Rational operator-(int const &, Rational const &);
	friend inline Rational operator*(Rational const &, Rational const &);
	friend inline Rational operator*(Rational const &, int const &);
	friend inline Rational operator*(int const &, Rational const &);
	friend inline Rational operator/(Rational const &, Rational const &);
	friend inline Rational operator/(Rational const &, int const &);
	friend inline Rational operator/(int const &, Rational const &);
	friend inline Rational operator%(Rational const &, Rational const &);
	friend inline Rational operator%(Rational const &, int const &);
	friend inline Rational operator%(int const &, Rational const &);
	friend inline bool operator==(Rational const &, Rational const &);
	friend inline bool operator==(Rational const &, int const &);
	friend inline bool operator==(int const &, Rational const &);
	friend inline auto operator<=>(Rational const &, Rational const &);
	friend inline auto operator<=>(Rational const &, int const &);
	friend inline auto operator<=>(int const &, Rational const &);
};
Rational operator+(Rational const &r) {
	return Rational(r.n, r.d);
}
Rational operator-(Rational const &r) {
	return Rational(-r.n, r.d);
}
Rational operator~(Rational const &r) {
	return Rational(r.d, r.n);
}
Rational operator+(Rational const &l, Rational const &r) {
	return Rational(l.n * r.d + r.n * l.d, l.d * r.d);
}
Rational operator+(Rational const &l, int const &n) {
	return Rational(l.n + l.d * n, l.d);
}
Rational operator+(int const &n, Rational const &r) {
	return Rational(r.n + r.d * n, r.d);
}
Rational operator-(Rational const &l, Rational const &r) {
	return Rational(l.n * r.d - r.n * l.d, l.d * r.d);
}
Rational operator-(Rational const &l, int const &n) {
	return Rational(l.n - l.d * n, l.d);
}
Rational operator-(int const &n, Rational const &r) {
	return Rational(r.d * n - r.n, r.d);
}
Rational operator*(Rational const &l, Rational const &r) {
	return Rational(l.n * r.n, l.d * r.d);
}
Rational operator*(Rational const &l, int const &n) {
	return Rational(l.n * n, l.d);
}
Rational operator*(int const &n, Rational const &r) {
	return Rational(r.n * n, r.d);
}
Rational operator/(Rational const &l, Rational const &r) {
	return Rational(l.n * r.d, r.n * l.d);
}
Rational operator/(Rational const &l, int const &n) {
	return Rational(l.n, l.d * n);
}
Rational operator/(int const &n, Rational const &r) {
	return Rational(r.d * n, r.n);
}
Rational operator%(Rational const &l, Rational const &r) {
	return l - (l / r).floor() * r;
}
Rational operator%(Rational const &l, int const &n) {
	return l % Rational(n);
}
Rational operator%(int const &n, Rational const &r) {
	return Rational(n) % r;
}
bool operator==(Rational const &l, Rational const &r) {
	return l.n * r.d == r.n * l.d;
}
bool operator==(Rational const &l, int const &n) {
	return l.n == n * l.d;
}
bool operator==(int const &n, Rational const &r) {
	return n * r.d == r.n;
}
auto operator<=>(Rational const &l, Rational const &r) {
	return l.n * r.d <=> r.n * l.d;
}
auto operator<=>(Rational const &l, int const &n) {
	return l.n <=> n * l.d;
}
auto operator<=>(int const &n, Rational const &r) {
	return n * r.d <=> r.n;
}
template <typename T>
Rational &operator+=(Rational &l, T const &x) {
	return l = l + x;
}
template <typename T>
Rational &operator-=(Rational &l, T const &x) {
	return l = l - x;
}
template <typename T>
Rational &operator*=(Rational &l, T const &x) {
	return l = l * x;
}
template <typename T>
Rational &operator/=(Rational &l, T const &x) {
	return l = l / x;
}
template <typename T>
Rational &operator%=(Rational &l, T const &x) {
	return l = l % x;
}
std::string Rational::decimal(uint8_t const &base) const {
	if (d == 0) {
		return n == 0 ? "NaN" : n > 0 ? "Inf" : "-Inf";
	}
	std::string result;
	int integer, decimal;
	if (n < 0) {
		integer = -n / d;
		decimal = -n % d;
	} else {
		integer = n / d;
		decimal = n % d;
	}
	do {
		result += str36[integer % base];
		integer /= base;
	} while (integer);
	if (n < 0) {
		result += '-';
	}
	reverse(result.begin(), result.end());
	if (decimal) {
		result += '.';
		std::vector<int> l;
		while (decimal && find(l.begin(), l.end(), decimal) == l.end()) {
			l.push_back(decimal);
			decimal *= base;
			decimal %= d;
		}
		for (auto i : l) {
			if (i == decimal) {
				result += '(';
			}
			result += str36[i * base / d];
		}
		if (decimal) {
			result += ')';
		}
	}
	return result;
}
Rational Rational::from_fra(std::string const &str) {
	bool neg = str[0] == '-';
	int i = str[0] == '-' || str[0] == '+';
	int n = 0;
	int d = 0;
	for (; str[i] >= '0' && str[i] <= '9'; i++) {
		n *= 10;
		n += str[i] - '0';
	}
	if (str[i] == '/') {
		for (i++; str[i] >= '0' && str[i] <= '9'; i++) {
			d *= 10;
			d += str[i] - '0';
		}
	} else {
		d = 1;
	}
	return Rational(neg ? -n : n, d);
}
Rational Rational::from_dec(std::string const &str) {
	bool neg = str[0] == '-';
	int i = str[0] == '-' || str[0] == '+';
	int a = 0, b = 0, integer = 0;
	int m = 1, n = 1;
	for (; str[i] >= '0' && str[i] <= '9'; i++) {
		integer *= 10;
		integer += str[i] - '0';
	}
	if (str[i] == '.') {
		for (i++; str[i] >= '0' && str[i] <= '9'; i++) {
			m *= 10;
			a *= 10;
			a += str[i] - '0';
		}
		if (str[i] == '(') {
			for (i++; str[i] >= '0' && str[i] <= '9'; i++) {
				n *= 10;
				b *= 10;
				b += str[i] - '0';
			}
			n--;
		}
	}
	return Rational(neg ? (-integer * m - a) * n - b : (integer * m + a) * n + b, n * m);
}
