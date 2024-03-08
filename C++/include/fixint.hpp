#pragma once
#include <cstdint>
#include <utility>
template <class InnInt>
class FixInt {
    InnInt lo, hi;
public:
    FixInt():
        lo(), hi() {}
    FixInt(InnInt l, InnInt h):
        lo(l), hi(h) {}
    FixInt(FixInt const &f):
        lo(f.lo), hi(f.hi) {}
    FixInt &operator=(FixInt const &f) {
        lo = f.lo;
        hi = f.hi;
        return *this;
    }
    friend bool add_with_carry(FixInt &r, FixInt const &a, FixInt const &b, bool carryin) {
        bool carrylo = add_with_carry(r.lo, a.lo, b.lo, carryin);
        bool carryhi = add_with_carry(r.hi, a.hi, b.hi, carrylo);
        return carryhi;
    }
    friend bool sub_with_borrow(FixInt &r, FixInt const &a, FixInt const &b, bool borrowin) {
        bool borrowlo = sub_with_borrow(r.lo, a.lo, b.lo, borrowin);
        bool borrowhi = sub_with_borrow(r.hi, a.hi, b.hi, borrowlo);
        return borrowhi;
    }
    friend void mul_with_carry(FixInt &l, FixInt &h, FixInt const &a, FixInt const &b, FixInt const &c, FixInt const &d) {
        InnInt x_hi, y_lo, y_hi, z_hi;
        mul_with_carry(l.lo, x_hi, a.lo, b.lo, c.lo, d.lo);
        mul_with_carry(y_lo, y_hi, a.hi, b.lo, c.hi, d.hi);
        mul_with_carry(l.hi, z_hi, a.lo, b.hi, x_hi, y_lo);
        mul_with_carry(h.lo, h.hi, a.lo, b.lo, y_hi, z_hi);
    }
};
class u32 {
    uint32_t val;
public:
    u32():
        val() {}
    u32(uint32_t v):
        val(v) {}
    u32(u32 const &u):
        val(u.val) {}
    u32 &operator=(u32 const &u) {
        val = u.val;
        return *this;
    }
    friend bool add_with_carry(u32 &r, u32 const &a, u32 const &b, bool carryin) {
        uint64_t sum = uint64_t(a.val) + uint64_t(b.val) + uint64_t(carryin);
        r.val = sum;
        return sum >> 32;
    }
    friend bool sub_with_borrow(u32 &r, u32 const &a, u32 const &b, bool borrowin) {
        uint64_t diff = uint64_t(a.val) - uint64_t(b.val) - uint64_t(borrowin);
        r.val = diff;
        return diff >> 32;
    }
    friend void mul_with_carry(u32 &l, u32 &h, u32 const &a, u32 const &b, u32 const &c, u32 const &d) {
        uint64_t prod = uint64_t(a.val) * uint64_t(b.val) + uint64_t(c.val) + uint64_t(d.val);
        l.val = prod & 0xffffffff;
        h.val = prod >> 32;
    }
};
using u64 = FixInt<u32>;
using u128 = FixInt<u64>;
using u256 = FixInt<u128>;
using u512 = FixInt<u256>;
using u1024 = FixInt<u512>;
using u2048 = FixInt<u1024>;
using u4096 = FixInt<u2048>;
