// Standard includes
#include <array>
#include <iostream>

// Package includes
#include <cpp_template/version.hpp>

int main() {
    std::cout << "\nCompiletime Version: \t"
              << cpp_template::compiletime_version << "\nRuntime Version: \t"
              << cpp_template::get_runtime_version()
              << "\n\nThe test succeeded!\n";
}
