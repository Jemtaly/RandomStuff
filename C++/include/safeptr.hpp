#pragma once
template <typename data_t>
class SafePtr {
	struct SafeGroup {
		size_t count;
		data_t data;
	} *ptr;
public:
	template <class... vals_t>
	SafePtr(vals_t const &...vals) : ptr(new SafeGroup{1, {vals...}}) {}
	SafePtr(SafePtr const &src) : ptr(src.ptr) {
		++ptr->count;
	}
	SafePtr &operator=(SafePtr const &src) {
		++src.ptr->count;
		if (--ptr->count == 0)
			delete ptr;
		ptr = src.ptr;
		return *this;
	}
	data_t &operator*() const {
		return ptr->data;
	}
	~SafePtr() {
		if (--ptr->count == 0)
			delete ptr;
	}
};
