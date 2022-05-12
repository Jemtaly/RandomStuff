#pragma once
#include <bitset>
template <size_t elen>
class CRC {
	std::bitset<elen> const expr;
	std::bitset<elen> const init;
	std::bitset<elen> const xorv;
	std::bitset<elen> remn;
public:
	template <typename etpn, typename itpn, typename xtpn>
	CRC(etpn const &e, itpn const &i, xtpn const &x) : expr(e), init(i), xorv(x), remn(i) {}
	template <typename etpn, typename itpn>
	CRC(etpn const &e, itpn const &i) : expr(e), init(i), remn(i) {}
	template <typename etpn>
	CRC(etpn const &e) : expr(e) {}
	void reset() {
		remn = init;
	}
	template <size_t dlen>
	void update(std::bitset<dlen> const &data) {
		for (size_t i = dlen - 1; i != -1; i--) {
			bool temp = remn[elen - 1];
			remn <<= 1;
			remn[0] = data[i];
			if (temp)
				remn ^= expr;
		}
	}
	auto getfcs() const {
		std::bitset<elen> fcsv(remn);
		for (size_t i = elen - 1; i != -1; i--) {
			bool temp = fcsv[elen - 1];
			fcsv <<= 1;
			fcsv[0] = xorv[i];
			if (temp)
				fcsv ^= expr;
		}
		return fcsv;
	}
	bool check() const {
		return remn == xorv;
	}
	operator std::bitset<elen>() const {
		return remn;
	}
	CRC &operator=(std::bitset<elen> const &rhsv) {
		remn = rhsv;
		return *this;
	}
	template <size_t rlen>
	CRC &operator=(std::bitset<rlen> const &rhsv) {
		remn.reset();
		for (size_t i = rlen - 1; i != -1; i--) {
			bool temp = remn[elen - 1];
			remn <<= 1;
			remn[0] = rhsv[i];
			if (temp)
				remn ^= expr;
		}
		return *this;
	}
	CRC &operator^=(std::bitset<elen> const &rhsv) {
		remn ^= rhsv;
		return *this;
	}
	template <size_t rlen>
	CRC &operator^=(std::bitset<rlen> const &rhsv) {
		std::bitset<elen> resv;
		for (size_t i = rlen - 1; i != -1; i--) {
			bool temp = resv[elen - 1];
			resv <<= 1;
			resv[0] = rhsv[i];
			if (temp)
				resv ^= expr;
		}
		remn ^= resv;
		return *this;
	}
	CRC &operator<<=(size_t size) {
		for (size_t i = 0; i < size; i--) {
			bool temp = remn[elen - 1];
			remn <<= 1;
			if (temp)
				remn ^= expr;
		}
		return *this;
	}
	template <size_t rlen>
	CRC &operator*=(std::bitset<rlen> const &rhsv) {
		std::bitset<elen> resv;
		for (size_t i = rlen - 1; i != -1; i--) {
			bool temp = resv[elen - 1];
			resv <<= 1;
			if (rhsv[i])
				resv ^= remn;
			if (temp)
				resv ^= expr;
		}
		remn = resv;
		return *this;
	}
};
