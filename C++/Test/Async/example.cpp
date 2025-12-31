#include <chrono>
#include <cstdint>
#include <format>
#include <iostream>
#include <string>
#include <thread>

#include "promise.hpp"

#define LOG(fmt, ...)                                                                                             \
    do {                                                                                                          \
        std::cout << std::format("{:%T} " fmt "\n",                                                               \
                                 std::chrono::floor<std::chrono::milliseconds>(std::chrono::system_clock::now()), \
                                 ##__VA_ARGS__);                                                                  \
    } while (0)

template<typename Result>
auto make_future_result(Result &&result, uint64_t ms) {
    auto [setter, getter] = make_async_pair<Result>();

    std::thread([setter = std::move(setter), result = std::move(result), ms]() mutable {
        LOG("[Future Task] Waiting for {} milliseconds...", ms);
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));

        LOG("[Future Task] Task completed, setting result...");
        setter.emplace_result(std::move(result));
    }).detach();

    return std::move(getter);
}

std::string sync_process(int value) {
    LOG("[Sync Process] Starting sync process for value: {}. Waiting for 2000ms...", value);
    std::this_thread::sleep_for(std::chrono::milliseconds(2000));

    LOG("[Sync Process] Sync process finished, returning result.");
    return std::format("Sync result: {}", value);
}

async_getter<std::string> async_process(int value) {
    auto [setter, getter] = make_async_pair<std::string>();

    std::thread([value, setter = std::move(setter)]() mutable {
        LOG("[Async Process] Starting async process for value: {}. Waiting for 2000ms...", value);
        std::this_thread::sleep_for(std::chrono::milliseconds(2000));

        LOG("[Async Process] Async process finished, setting result.");
        setter.emplace_result(std::format("Async result: {}", value));
    }).detach();

    return std::move(getter);
}

int main() {
    LOG("--- DEMO 0: RACE ---");
    {
        auto task1 = make_future_result<std::string>("Result from task 1", 3000);
        auto task2 = make_future_result<std::string>("Result from task 2", 2000);
        auto task3 = make_future_result<std::string>("Result from task 3", 1000);

        LOG("[Main thread] Waiting for the first completed task (race)...");
        std::string done = race({std::move(task1), std::move(task2), std::move(task3)});

        LOG("[Main thread] First completed result: {}", done);
    }

    LOG("--- DEMO 1: THEN WITH SYNC PROCESS ---");
    {
        LOG("[Main thread] Starting initial task...");
        auto todo = make_future_result<int>(42, 1000);

        LOG("[Main thread] Chaining a synchronous process with then()...");
        auto next = then<std::string>(
            std::move(todo),
            [](int value, async_setter<std::string> setter) -> void {
                LOG("[Then Processing] Received value: {}. Starting sync process.", value);
                auto result = sync_process(value);
                LOG("[Then Processing] Finished sync process. Setting final result.");
                setter.emplace_result(std::move(result));
            });

        LOG("[Main thread] Waiting for final result with wait()...");
        std::string done = wait(std::move(next));

        LOG("[Main thread] Final result: {}", done);
    }

    LOG("--- DEMO 2: THEN WITH ASYNC PROCESS ---");
    {
        LOG("[Main thread] Starting initial task...");
        auto todo = make_future_result<int>(42, 1000);

        LOG("[Main thread] Chaining an asynchronous process with then()...");
        auto next = then<std::string>(
            std::move(todo),
            [](int value) -> async_getter<std::string> {
                LOG("[Then Processing] Received value: {}. Starting async process.", value);
                auto getter = async_process(value);
                LOG("[Then Processing] Returned an async_getter. The chain will continue when it resolves.");
                return getter;
            });

        LOG("[Main thread] Waiting for final result with wait()...");
        std::string done = wait(std::move(next));

        LOG("[Main thread] Final result: {}", done);
    }

    return 0;
}
