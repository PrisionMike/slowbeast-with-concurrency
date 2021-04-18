#include <assert.h>

// UNSUPPORTED: kind
// UNSUPPORTED: kindse
// RUN: clang %s -emit-llvm -g -c -o %t.bc
// RUN: rm -rf %t-out
// RUN: timeout 30 sb -out-dir=%t-out %opts %t.bc &>%t.log
// RUN: cat %t.log | FileCheck %s



void foo(int y) {
    assert(y != 5);
}

int main(void) {
    int x = 5;
    foo(x);

	// CHECK: Error found.
	// CHECK: Found errors: 1
}
