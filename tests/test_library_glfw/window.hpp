#pragma once

// Standard includes
#include <memory>

// External includes
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

namespace myl {

// Initialize GLFW
void initialize();

// Terminate GLFW
void terminate();

// Poll GLFW events
void poll_events();

// Object-oriented wrapper for a GLFW window
class window {
    GLFWwindow* window_ptr_;

  public:
    // Create a new window
    window(int width, int height, const char* title);

    // Deleted constructors
    window(const window&) = delete;
    window(window&&) = delete;
    window& operator=(const window&) = delete;
    window& operator=(window&&) = delete;

    // Close this window
    ~window();

    // true if this window should stay open and false otherwise
    [[nodiscard]] bool is_open();

    // Set the title of this window
    void set_title(const char* title);

    // Set the position of this window
    void set_pos(int width, int height);
};

} // namespace myl
