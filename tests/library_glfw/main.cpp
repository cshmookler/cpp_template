// Standard includes
#include <chrono>
#include <iostream>

// External includes
#include <my_lib/version.hpp>
#include <my_lib/window.hpp>

class timer {
    std::chrono::system_clock::time_point start_time_;
    std::chrono::seconds time_to_wait_;

  public:
    explicit timer(size_t seconds)
    : start_time_(std::chrono::system_clock::now()), time_to_wait_(seconds) {
    }

    bool done() {
        return std::chrono::system_clock::now() - this->start_time_
          > this->time_to_wait_;
    }
};

int main(int argc, char** argv) {
    myl::initialize();

    std::cout << "version: " << myl::get_runtime_version() << '\n';

    myl::window this_window{ 900, 600, "this is a test" };

    timer this_window_timer{ 3 };
    while (this_window.is_open() && ! this_window_timer.done()) {
        myl::poll_events();
    }

    myl::terminate();
    return 0;
}
