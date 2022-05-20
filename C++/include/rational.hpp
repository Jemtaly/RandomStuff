#pragma once
#include <algorithm>
#include <string>
#include <vector>
class Rational {
private:
	int n;
	unsigned int d;
	void reduce() {
		unsigned int t;
		for (unsigned int a = n < 0 ? -n : n, b = d; t = a, b; a = b, b = t % b)
			;
		if (t)
			n /= t, d /= t;
	}
	static constexpr char str36[36] = {
		'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B',
		'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
		'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
	};
public:
	Rational &set(int const &numerator = 0, int const &denominator = 1) {
		if (d < 0) {
			n = -numerator;
			d = -denominator;
		} else {
			n = numerator;
			d = denominator;
		}
		reduce();
		return *this;
	}
	Rational(int const &numerator = 0, int const &denominator = 1) {
		set(numerator, denominator);
	}
	Rational &operator=(int const &numerator) {
		return set(numerator);
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
	inline std::string decimal(char const &base = 10) const;
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
	friend inline bool operator>=(Rational const &, Rational const &);
	friend inline bool operator>=(Rational const &, int const &);
	friend inline bool operator>=(int const &, Rational const &);
	friend inline bool operator<=(Rational const &, Rational const &);
	friend inline bool operator<=(Rational const &, int const &);
	friend inline bool operator<=(int const &, Rational const &);
	friend inline bool operator!=(Rational const &, Rational const &);
	friend inline bool operator!=(Rational const &, int const &);
	friend inline bool operator!=(int const &, Rational const &);
	friend inline bool operator>(Rational const &, Rational const &);
	friend inline bool operator>(Rational const &, int const &);
	friend inline bool operator>(int const &, Rational const &);
	friend inline bool operator<(Rational const &, Rational const &);
	friend inline bool operator<(Rational const &, int const &);
	friend inline bool operator<(int const &, Rational const &);
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
Rational operator+(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d + r2.n * r1.d, r1.d * r2.d);
}
Rational operator+(Rational const &r, int const &n) {
	return Rational(r.n + n * r.d, r.d);
}
Rational operator+(int const &n, Rational const &r) {
	return Rational(r.n + n * r.d, r.d);
}
Rational operator-(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d - r2.n * r1.d, r1.d * r2.d);
}
Rational operator-(Rational const &r, int const &n) {
	return Rational(r.n - n * r.d, r.d);
}
Rational operator-(int const &n, Rational const &r) {
	return Rational(r.n - n * r.d, r.d);
}
Rational operator*(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.n, r1.d * r2.d);
}
Rational operator*(Rational const &r, int const &n) {
	return Rational(r.n * n, r.d);
}
Rational operator*(int const &n, Rational const &r) {
	return Rational(r.n * n, r.d);
}
Rational operator/(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d, r1.d * r2.n);
}
Rational operator/(Rational const &r, int const &n) {
	return Rational(r.n, r.d * n);
}
Rational operator/(int const &n, Rational const &r) {
	return Rational(r.n, r.d * n);
}
Rational operator%(Rational const &r1, Rational const &r2) {
	return r1 - (r1 / r2).floor() * r2;
}
Rational operator%(Rational const &r, int const &n) {
	return r % Rational(n);
}
Rational operator%(int const &n, Rational const &r) {
	return Rational(n) % r;
}
bool operator==(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n == 0;
}
bool operator==(Rational const &r, int const &n) {
	return (r - n).n == 0;
}
bool operator==(int const &n, Rational const &r) {
	return (r - n).n == 0;
}
bool operator!=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n != 0;
}
bool operator!=(Rational const &r, int const &n) {
	return (r - n).n != 0;
}
bool operator!=(int const &n, Rational const &r) {
	return (r - n).n != 0;
}
bool operator>=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n >= 0;
}
bool operator>=(Rational const &r, int const &n) {
	return (r - n).n >= 0;
}
bool operator>=(int const &n, Rational const &r) {
	return (r - n).n >= 0;
}
bool operator<=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n <= 0;
}
bool operator<=(Rational const &r, int const &n) {
	return (r - n).n <= 0;
}
bool operator<=(int const &n, Rational const &r) {
	return (r - n).n <= 0;
}
bool operator>(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n > 0;
}
bool operator>(Rational const &r, int const &n) {
	return (r - n).n > 0;
}
bool operator>(int const &n, Rational const &r) {
	return (r - n).n > 0;
}
bool operator<(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n < 0;
}
bool operator<(Rational const &r, int const &n) {
	return (r - n).n < 0;
}
bool operator<(int const &n, Rational const &r) {
	return (r - n).n < 0;
}
template <typename T>
Rational &operator+=(Rational &r, T const &x) {
	return r = r + x;
}
template <typename T>
Rational &operator-=(Rational &r, T const &x) {
	return r = r - x;
}
template <typename T>
Rational &operator*=(Rational &r, T const &x) {
	return r = r * x;
}
template <typename T>
Rational &operator/=(Rational &r, T const &x) {
	return r = r / x;
}
template <typename T>
Rational &operator%=(Rational &r, T const &x) {
	return r = r % x;
}
std::string Rational::decimal(char const &base) const {
	if (d == 0)
		return n == 0 ? "NaN" : n > 0 ? "Inf" : "-Inf";
	std::string result;
	int integer, decimal;
	if (n < 0) {
		integer = -n / d;
		decimal = -n % d;
	} else {
		integer = n / d;
		decimal = n % d;
	}
	if (integer == 0)
		result += '0';
	else
		do {
			result += str36[integer % base];
			integer /= base;
		} while (integer);
	if (n < 0)
		result += '-';
	reverse(result.begin(), result.end());
	if (decimal) {
		result += '.';
		std::vector<int> l;
		while (decimal and find(l.begin(), l.end(), decimal) == l.end()) {
			l.push_back(decimal);
			decimal *= base;
			decimal %= d;
		}
		for (auto i : l) {
			if (i == decimal)
				result += '(';
			result += str36[i * base / d];
		}
		if (decimal)
			result += ')';
	}
	return result;
}
Rational Rational::from_fra(std::string const &str) {
	int i;
	bool neg;
	if (str[0] == '-')
		i = 1, neg = true;
	else if (str[0] == '+')
		i = 1, neg = false;
	else
		i = 0, neg = false;
	int n = 0;
	unsigned int d = 0;
	for (; str[i] >= '0' && str[i] <= '9'; i++) {
		n *= 10;
		n += str[i] - '0';
	}
	if (str[i] == '/')
		for (i++; str[i] >= '0' && str[i] <= '9'; i++) {
			d *= 10;
			d += str[i] - '0';
		}
	else
		d = 1;
	return Rational(neg ? -n : n, d);
}
Rational Rational::from_dec(std::string const &str) {
	int i;
	bool neg;
	if (str[0] == '-')
		i = 1, neg = true;
	else if (str[0] == '+')
		i = 1, neg = false;
	else
		i = 0, neg = false;
	int integer = 0, a = 0, b = 0;
	unsigned int m = 1, n = 1;
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
		if (str[i] == '(')
			for (i++; str[i] >= '0' && str[i] <= '9'; i++) {
				n *= 10;
				b *= 10;
				b += str[i] - '0';
			}
		else
			n = 2;
	}
	return Rational(neg ? (integer * m + a) * (1 - n) - b : (integer * m + a) * (n - 1) + b, (n - 1) * m);
}
