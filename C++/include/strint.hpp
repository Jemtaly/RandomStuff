#pragma once
#include <stdint.h>
class StrInt {
	size_t len;
	int8_t *abs;
	size_t *ctr;
	auto const &get(size_t const &i) const {
		return abs[i < len ? i : len];
	}
	/*
	StrInt(size_t const &rlen, int8_t *const &rabs) : len(rlen), abs(rabs) {
		while (len && abs[len - 1] == abs[len])
			len--;
	}
	*/
	StrInt(size_t const &rlen, int8_t *const &rabs) : len(rlen), abs(rabs), ctr(new size_t(1)) {
		while (len && abs[len - 1] == abs[len])
			len--;
	}
public:
	/*
	StrInt(StrInt const &rval) : len(rval.len), abs(new int8_t[rval.len + 1]) {
		for (size_t i = 0; i <= rval.len; i++)
			abs[i] = rval.abs[i];
	}
	StrInt(StrInt &&rval) : len(-1), abs(nullptr) {
		std::swap(len, rval.len);
		std::swap(abs, rval.abs);
	}
	StrInt &operator=(StrInt const &rval) {
		if (&rval != this) {
			delete[] abs;
			len = rval.len;
			abs = new int8_t[rval.len + 1];
			for (size_t i = 0; i <= rval.len; i++)
				abs[i] = rval.abs[i];
		}
		return *this;
	}
	StrInt &operator=(StrInt &&rval) {
		std::swap(len, rval.len);
		std::swap(abs, rval.abs);
		return *this;
	}
	~StrInt() {
		delete[] abs;
	}
	*/
	StrInt(StrInt const &rval) : len(rval.len), abs(aval.abs), ctr(rval.ctr) {
		++*ctr;
	}
	StrInt &operator=(StrInt const &rval) {
		++*rval.ctr;
		if (--*ctr == 0) {
			delete[] abs;
			delete ctr;
		}
		len = rval.len;
		abs = rval.abs;
		ctr = rval.ctr;
		return *this;
	}
	~StrInt() {
		if (--*ctr == 0) {
			delete[] abs;
			delete ctr;
		}
	}
	friend StrInt operator+(StrInt const &, StrInt const &);
	friend StrInt operator-(StrInt const &, StrInt const &);
	friend StrInt operator*(StrInt const &, StrInt const &);
	friend StrInt divmod(StrInt const &, StrInt const &, bool const &);
	friend StrInt operator/(StrInt const &, StrInt const &);
	friend StrInt operator%(StrInt const &, StrInt const &);
	friend bool operator>(StrInt const &, StrInt const &);
	friend bool operator<(StrInt const &, StrInt const &);
	friend bool operator>=(StrInt const &, StrInt const &);
	friend bool operator<=(StrInt const &, StrInt const &);
	friend bool operator==(StrInt const &, StrInt const &);
	friend bool operator!=(StrInt const &, StrInt const &);
};
StrInt operator+(StrInt const &lhs, StrInt const &rhs) {
	size_t len = (lhs.len > rhs.len ? lhs.len : rhs.len) + 1;
	int8_t *abs = new int8_t[len + 1];
	int8_t s = 0;
	for (size_t i = 0; i <= len; i++) {
		s = lhs.get(i) + rhs.get(i) + (s >= 10);
		abs[i] = s % 10;
	}
	return StrInt(len, abs);
}
StrInt operator-(StrInt const &lhs, StrInt const &rhs) {
	size_t len = (lhs.len > rhs.len ? lhs.len : rhs.len) + 1;
	int8_t *abs = new int8_t[len + 1];
	int8_t d = 0;
	for (size_t i = 0; i <= len; i++) {
		d = lhs.get(i) - rhs.get(i) - (d < 0);
		abs[i] = d < 0 ? d + 10 : d;
	}
	return StrInt(len, abs);
}
StrInt operator*(StrInt const &lhs, StrInt const &rhs) {
	size_t len = lhs.len + rhs.len + 1;
	int8_t *abs = new int8_t[len + 1]();
	for (size_t i = 0; i <= len; i++) {
		int8_t p = 0, s = 0;
		for (size_t j = 0; i + j <= len; j++) {
			p = lhs.get(j) * rhs.get(i) + p / 10;
			s = p % 10 + abs[i + j] + (s >= 10);
			abs[i + j] = s % 10;
		}
	}
	return StrInt(len, abs);
}
StrInt divmod(StrInt const &lhs, StrInt const &rhs, bool const &select) {
	size_t len = lhs.len + rhs.len;
	int8_t *pabs = new int8_t[len + 1], *tabs = new int8_t[len + 1];
	int8_t *qabs = new int8_t[lhs.len + 1], *rabs = new int8_t[rhs.len + 1];
	for (size_t i = 0; i <= len; i++)
		pabs[i] = lhs.get(i);
	if (lhs.abs[lhs.len] == rhs.abs[rhs.len]) {
		for (size_t i = 0; i <= lhs.len; i++)
			qabs[i] = 0;
		for (size_t i = lhs.len; i != -1; i--)
			for (;;) {
				int8_t d = 0;
				for (size_t j = 0; i + j <= len; j++) {
					d = pabs[i + j] - rhs.get(j) - (d < 0);
					tabs[i + j] = d < 0 ? d + 10 : d;
				}
				if (tabs[len] != pabs[len])
					break;
				qabs[i]++;
				for (size_t j = 0; i + j <= len; j++)
					pabs[i + j] = tabs[i + j];
			}
		for (size_t i = 0; i <= rhs.len; i++)
			rabs[i] = pabs[i];
	} else {
		for (size_t i = 0; i <= lhs.len; i++)
			qabs[i] = 9;
		for (size_t i = lhs.len; i != -1; i--)
			for (;;) {
				int8_t s = 0;
				for (size_t j = 0; i + j <= len; j++) {
					s = pabs[i + j] + rhs.get(j) + (s >= 10);
					tabs[i + j] = s % 10;
				}
				if (tabs[len] != pabs[len])
					break;
				qabs[i]--;
				for (size_t j = 0; i + j <= len; j++)
					pabs[i + j] = tabs[i + j];
			}
		for (size_t i = 0; i <= rhs.len; i++)
			rabs[i] = tabs[i];
	}
	delete[] pabs;
	delete[] tabs;
	if (select) {
		delete[] qabs;
		return StrInt(rhs.len, rabs);
	} else {
		delete[] rabs;
		return StrInt(lhs.len, qabs);
	}
}
StrInt operator/(StrInt const &lhs, StrInt const &rhs) {
	return divmod(lhs, rhs, 0);
}
StrInt operator%(StrInt const &lhs, StrInt const &rhs) {
	return divmod(lhs, rhs, 1);
}
bool operator>(StrInt const &lhs, StrInt const &rhs) {
	if (lhs.abs[lhs.len] < rhs.abs[rhs.len])
		return true;
	if (lhs.abs[lhs.len] > rhs.abs[rhs.len])
		return false;
	for (size_t i = (lhs.len > rhs.len ? lhs.len : rhs.len) - 1; i != -1; i--) {
		if (lhs.get(i) > rhs.get(i))
			return true;
		if (lhs.get(i) < rhs.get(i))
			return false;
	}
	return false;
}
bool operator>=(StrInt const &lhs, StrInt const &rhs) {
	if (lhs.abs[lhs.len] < rhs.abs[rhs.len])
		return true;
	if (lhs.abs[lhs.len] > rhs.abs[rhs.len])
		return false;
	for (size_t i = (lhs.len > rhs.len ? lhs.len : rhs.len) - 1; i != -1; i--) {
		if (lhs.get(i) > rhs.get(i))
			return true;
		if (lhs.get(i) < rhs.get(i))
			return false;
	}
	return true;
}
bool operator<(StrInt const &lhs, StrInt const &rhs) {
	if (lhs.abs[lhs.len] > rhs.abs[rhs.len])
		return true;
	if (lhs.abs[lhs.len] < rhs.abs[rhs.len])
		return false;
	for (size_t i = (lhs.len > rhs.len ? lhs.len : rhs.len) - 1; i != -1; i--) {
		if (lhs.get(i) < rhs.get(i))
			return true;
		if (lhs.get(i) > rhs.get(i))
			return false;
	}
	return false;
}
bool operator<=(StrInt const &lhs, StrInt const &rhs) {
	if (lhs.abs[lhs.len] > rhs.abs[rhs.len])
		return true;
	if (lhs.abs[lhs.len] < rhs.abs[rhs.len])
		return false;
	for (size_t i = (lhs.len > rhs.len ? lhs.len : rhs.len) - 1; i != -1; i--) {
		if (lhs.get(i) < rhs.get(i))
			return true;
		if (lhs.get(i) > rhs.get(i))
			return false;
	}
	return true;
}
bool operator!=(StrInt const &lhs, StrInt const &rhs) {
	for (size_t i = lhs.len > rhs.len ? lhs.len : rhs.len; i != -1; i--)
		if (lhs.get(i) != rhs.get(i))
			return true;
	return false;
}
bool operator==(StrInt const &lhs, StrInt const &rhs) {
	for (size_t i = lhs.len > rhs.len ? lhs.len : rhs.len; i != -1; i--)
		if (lhs.get(i) != rhs.get(i))
			return false;
	return true;
}
StrInt &operator+=(StrInt &lhs, StrInt const &rhs) {
	return lhs = lhs + rhs;
}
StrInt &operator-=(StrInt &lhs, StrInt const &rhs) {
	return lhs = lhs - rhs;
}
StrInt &operator*=(StrInt &lhs, StrInt const &rhs) {
	return lhs = lhs * rhs;
}
StrInt &operator/=(StrInt &lhs, StrInt const &rhs) {
	return lhs = lhs / rhs;
}
StrInt &operator%=(StrInt &lhs, StrInt const &rhs) {
	return lhs = lhs % rhs;
}
