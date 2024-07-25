// Standard includes
#include <stdexcept>
#include <string>

// External includes
#include <argparse/argparse.hpp>

// Local includes
#include "version.hpp"

int main(int argc, char** argv) {
    std::string version = app::get_runtime_version();

    // Setup the command line argument parser
    argparse::ArgumentParser parser("my_app", version);
    parser.add_description("An example application that depends on argparse");
    parser.add_argument("-n", "--nothing").flag().help("do absolutely nothing");

    // Parse command line arguments
    try {
        parser.parse_args(argc, argv);
    }
    catch (const std::exception& err) {
        std::cerr << err.what() << "\n\n";
        std::cerr << parser;
        // NOLINTNEXTLINE(concurrency-mt-unsafe)
        std::exit(1);
    }

    if (! parser.is_used("--nothing")) {
        std::cout << "The test succeeded!\n";
    }

    return 0;
}
