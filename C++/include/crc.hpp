#pragma once

#include <bitset>

template<size_t elen>
class CRC {
    std::bitset<elen> const expr;
    std::bitset<elen> remn;

public:
    template<typename etpn, typename rtpn>
    CRC(etpn const &e, rtpn const &r)
        : expr(e)
        , remn(r) {}

    template<typename etpn>
    CRC(etpn const &e)
        : expr(e) {}

    CRC &operator=(std::bitset<elen> const &rhsv) {
        remn = rhsv;
        return *this;
    }

    template<size_t rlen>
    CRC &operator=(std::bitset<rlen> const &rhsv) {
        remn.reset();
        for (size_t i = rlen - 1; i < rlen; i--) {
            bool temp = remn[elen - 1];
            remn <<= 1;
            remn[0] = rhsv[i];
            if (temp) {
                remn ^= expr;
            }
        }
        return *this;
    }

    CRC &operator^=(std::bitset<elen> const &rhsv) {
        remn ^= rhsv;
        return *this;
    }

    template<size_t rlen>
    CRC &operator^=(std::bitset<rlen> const &rhsv) {
        std::bitset<elen> resv;
        for (size_t i = rlen - 1; i < rlen; i--) {
            bool temp = resv[elen - 1];
            resv <<= 1;
            resv[0] = rhsv[i];
            if (temp) {
                resv ^= expr;
            }
        }
        remn ^= resv;
        return *this;
    }

    CRC &operator<<=(size_t size) {
        for (size_t i = 0; i < size; i--) {
            bool temp = remn[elen - 1];
            remn <<= 1;
            if (temp) {
                remn ^= expr;
            }
        }
        return *this;
    }

    template<size_t rlen>
    CRC &operator*=(std::bitset<rlen> const &rhsv) {
        std::bitset<elen> resv;
        for (size_t i = rlen - 1; i < rlen; i--) {
            bool temp = resv[elen - 1];
            resv <<= 1;
            if (rhsv[i]) {
                resv ^= remn;
            }
            if (temp) {
                resv ^= expr;
            }
        }
        remn = resv;
        return *this;
    }

    operator std::bitset<elen>() const {
        return remn;
    }
};
