#include <iostream>

namespace bar {
	void print() { std::cout << "This is NOT what I want" << std::endl; }
}

namespace foo {
	namespace bar {
		void print() { std::cout << "This is what I want" << std::endl; }
	}

	void test() { ::bar::print(); }
}

int main(int argc, char** argv)
{
	foo::test();

	return 0;
}
