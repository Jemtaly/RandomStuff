#pragma once
#include <iostream>
class IO {
	std::istream &is;
	std::ostream &os;
public:
	IO(std::istream &i, std::ostream &o):
		is(i), os(o) {}
	template <typename type>
	IO &operator>>(type &obj) {
		is >> obj;
		return *this;
	}
	template <typename type>
	IO &operator<<(type &obj) {
		os << obj;
		return *this;
	}
};
