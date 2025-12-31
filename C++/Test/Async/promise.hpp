#pragma once

#include <cassert>
#include <cstdint>
#include <utility>

enum AsyncContextFlags : uint32_t {
    ASYNC_CONTEXT_NONE = 0,
    ASYNC_CONTEXT_RESULT_SET = 1 << 0,
    ASYNC_CONTEXT_HANDLER_SET = 1 << 1,
};

template<typename Result>
struct async_context {
    union HandlerStorage {
        void *ptr;
        char buf[sizeof(void *) * 4];
    };

    union ResultBuffer {
        Result result;

        ResultBuffer() {}

        ~ResultBuffer() {}
    };

    uint32_t ref_count;
    uint32_t flags;

    HandlerStorage storage;
    void (*process_handler_ptr)(HandlerStorage storage, Result *result_ptr);
    void (*cleanup_handler_ptr)(HandlerStorage storage);

    ResultBuffer buffer;

    async_context(async_context const &) = delete;
    async_context &operator=(async_context const &) = delete;
    async_context(async_context &&) = delete;
    async_context &operator=(async_context &&) = delete;

    async_context(uint32_t ref_count)
        : ref_count(ref_count)
        , flags(ASYNC_CONTEXT_NONE)
        , process_handler_ptr(nullptr)
        , cleanup_handler_ptr(nullptr) {}

    bool dec_ref() {
        return __atomic_sub_fetch(&ref_count, 1, __ATOMIC_ACQ_REL) == 0;
    }

    uint32_t set_flags(uint32_t new_flags) {
        return __atomic_or_fetch(&flags, new_flags, __ATOMIC_ACQ_REL);
    }

    void process_handler() {
        process_handler_ptr(storage, &buffer.result);
    }

    void cleanup_handler() {
        cleanup_handler_ptr(storage);
    }

    template<typename... Args>
    void emplace_result(Args &&...args) {
        assert(!(flags & ASYNC_CONTEXT_RESULT_SET) && "Result is already being set");
        new (&buffer.result) Result(std::forward<Args>(args)...);

        uint32_t old_flags = set_flags(ASYNC_CONTEXT_RESULT_SET);
        if (old_flags & ASYNC_CONTEXT_HANDLER_SET) {
            process_handler();
        }
    }

    template<typename SmallConstHandler, typename... Args>
    void emplace_handler(Args &&...args) {
        static_assert(sizeof(SmallConstHandler) <= sizeof(HandlerStorage::buf), "Handler type is too large for small storage");
        assert(!(flags & ASYNC_CONTEXT_HANDLER_SET) && "Handler is already being set");
        new (&storage.buf) SmallConstHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](HandlerStorage storage, Result *result_ptr) {
            reinterpret_cast<SmallConstHandler const *>(&storage.buf)->handle_result(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](HandlerStorage storage) {
            reinterpret_cast<SmallConstHandler const *>(&storage.buf)->~SmallConstHandler();
        };

        uint32_t old_flags = set_flags(ASYNC_CONTEXT_HANDLER_SET);
        if (old_flags & ASYNC_CONTEXT_RESULT_SET) {
            process_handler();
        }
    }

    template<typename LargeMutableHandler, typename... Args>
    void new_handler(Args &&...args) {
        assert(!(flags & ASYNC_CONTEXT_HANDLER_SET) && "Handler is already being set");
        storage.ptr = new LargeMutableHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](HandlerStorage storage, Result *result_ptr) {
            reinterpret_cast<LargeMutableHandler *>(storage.ptr)->handle_result(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](HandlerStorage storage) {
            delete reinterpret_cast<LargeMutableHandler *>(storage.ptr);
        };

        uint32_t old_flags = set_flags(ASYNC_CONTEXT_HANDLER_SET);
        if (old_flags & ASYNC_CONTEXT_RESULT_SET) {
            process_handler();
        }
    }

    bool is_ready() const {
        return flags & ASYNC_CONTEXT_RESULT_SET;
    }

    ~async_context() {
        if (flags & ASYNC_CONTEXT_RESULT_SET) {
            buffer.result.~Result();
        }
        if (flags & ASYNC_CONTEXT_HANDLER_SET) {
            cleanup_handler();
        }
    }
};

template<typename Result>
class async_setter;

template<typename Result>
class async_getter;

template<typename Result>
std::pair<async_setter<Result>, async_getter<Result>> make_async_pair();

template<typename Result>
class async_setter {
    async_context<Result> *ctx;

    async_setter(async_context<Result> *ctx)
        : ctx(ctx) {}

    friend std::pair<async_setter<Result>, async_getter<Result>> make_async_pair<Result>();

public:
    async_setter(async_setter const &) = delete;

    async_setter(async_setter &&other)
        : ctx(other.ctx) {
        other.ctx = nullptr;
    }

    async_setter &operator=(async_setter other) {
        std::swap(this->ctx, other.ctx);
        return *this;
    }

    ~async_setter() {
        if (ctx && ctx->dec_ref()) {
            delete ctx;
        }
    }

    template<typename... Args>
    void emplace_result(Args &&...args) const {
        ctx->emplace_result(std::forward<Args>(args)...);
    }
};

template<typename Result>
class async_getter {
    async_context<Result> *ctx;

    async_getter(async_context<Result> *ctx)
        : ctx(ctx) {}

    friend std::pair<async_setter<Result>, async_getter<Result>> make_async_pair<Result>();

public:
    async_getter(async_getter const &) = delete;

    async_getter(async_getter &&other)
        : ctx(other.ctx) {
        other.ctx = nullptr;
    }

    async_getter &operator=(async_getter other) {
        std::swap(this->ctx, other.ctx);
        return *this;
    }

    ~async_getter() {
        if (ctx && ctx->dec_ref()) {
            delete ctx;
        }
    }

    template<typename SmallConstHandler, typename... Args>
    void emplace_handler(Args &&...args) const {
        ctx->template emplace_handler<SmallConstHandler>(std::forward<Args>(args)...);
    }

    template<typename LargeMutableHandler, typename... Args>
    void new_handler(Args &&...args) const {
        ctx->template new_handler<LargeMutableHandler>(std::forward<Args>(args)...);
    }

    bool is_ready() const {
        return ctx->is_ready();
    }
};

template<typename Result>
std::pair<async_setter<Result>, async_getter<Result>> make_async_pair() {
    async_context<Result> *ctx = new async_context<Result>(2);
    return {
        async_setter<Result>(ctx),
        async_getter<Result>(ctx),
    };
}

// Utils

#include <condition_variable>
#include <mutex>
#include <optional>

template<typename Result>
Result wait(async_getter<Result> gotter) {
    struct WaitContext {
        std::mutex mtx;
        std::condition_variable cv;
        std::optional<Result> result;
    };

    struct WaitHandler {
        WaitContext &ctx;

        WaitHandler(WaitContext &ctx)
            : ctx(ctx) {}

        void handle_result(Result &&result) const {
            std::unique_lock<std::mutex> lock(ctx.mtx);
            ctx.result.emplace(std::forward<Result>(result));
            ctx.cv.notify_all();
        }
    };

    WaitContext ctx;
    gotter.template emplace_handler<WaitHandler>(ctx);

    std::unique_lock<std::mutex> lock(ctx.mtx);
    ctx.cv.wait(lock, [&ctx]() {
        return ctx.result.has_value();
    });

    return std::move(ctx.result.value());
}

template<typename Result>
Result race(std::initializer_list<async_getter<Result>> gotters) {
    struct RaceContext {
        std::mutex mtx;
        std::condition_variable cv;
        std::optional<Result> result;
    };

    struct RaceHandler {
        std::shared_ptr<RaceContext> ptr;

        RaceHandler(std::shared_ptr<RaceContext> ptr)
            : ptr(ptr) {}

        void handle_result(Result &&result) const {
            std::unique_lock<std::mutex> lock(ptr->mtx);
            if (!ptr->result.has_value()) {
                ptr->result.emplace(std::forward<Result>(result));
                ptr->cv.notify_all();
            }
        }
    };

    auto ptr = std::make_shared<RaceContext>();
    for (auto const &gotter : gotters) {
        gotter.template emplace_handler<RaceHandler>(ptr);
    }

    std::unique_lock<std::mutex> lock(ptr->mtx);
    ptr->cv.wait(lock, [ptr = ptr.get()]() {
        return ptr->result.has_value();
    });

    return std::move(ptr->result.value());
}

#include <type_traits>

template<typename Next, typename Last, typename Processor>
async_getter<Next> then(async_getter<Last> gotter, Processor &&processor) {
    auto [setter, getter] = make_async_pair<Next>();

    struct ThenHandler {
        async_setter<Next> setter;
        Processor processor;

        ThenHandler(Processor &&processor, async_setter<Next> setter)
            : processor(std::forward<Processor>(processor)), setter(std::move(setter)) {}

        struct NextHandler {
            async_setter<Next> setter;

            NextHandler(async_setter<Next> setter)
                : setter(std::move(setter)) {}

            void handle_result(Next &&result) const {
                setter.emplace_result(std::forward<Next>(result));
            }
        };

        void handle_result(Last &&result) {
            if constexpr (std::is_invocable_r_v<async_getter<Next>, Processor, Last>) {
                this->processor(std::forward<Last>(result)).template emplace_handler<NextHandler>(std::move(this->setter));
            } else if constexpr (std::is_invocable_v<Processor, Last, async_setter<Next>>) {
                this->processor(std::forward<Last>(result), std::move(this->setter));
            } else {
                static_assert(false, "Processor cannot handle result without setter or promise return type");
            }
        }
    };

    gotter.template new_handler<ThenHandler>(std::forward<Processor>(processor), std::move(setter));
    return std::move(getter);
}
