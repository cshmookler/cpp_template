// Standard includes
#include <stdexcept>

// Local includes
#include "../my_lib/window.hpp"

namespace myl {

void initialize() {
    if (glfwInit() != GLFW_TRUE) {
        throw std::runtime_error("Failed to initialize GLFW");
    }
}

void terminate() {
    glfwTerminate();
}

void poll_events() {
    glfwPollEvents();
}

window::window(int width, int height, const char* title)
: window_ptr_(glfwCreateWindow(width, height, title, nullptr, nullptr)) {}

window::~window() {
    glfwDestroyWindow(this->window_ptr_);
}

bool window::is_open() {
    return glfwWindowShouldClose(this->window_ptr_) != GLFW_TRUE;
}

void window::set_title(const char* title) {
    glfwSetWindowTitle(this->window_ptr_, title);
}

void window::set_pos(int width, int height) {
    glfwSetWindowPos(this->window_ptr_, width, height);
}

} // namespace myl
