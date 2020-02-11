#include <assert.h>

// UNSUPPORTED: kind
// RUN: clang %s -emit-llvm -g -c -o %t.bc
// RUN: rm -rf %t-out
// RUN: sb -out-dir=%t-out %opts %t.bc &>%t.log
// RUN: cat %t.log | FileCheck %s


int a;

int main() {
	a = nondet_int();
	if (a > 3) {
		a += 1;
	} else {
		a -= 1;
	}

	// CHECK: Executed paths: 2
	// CHECK: Paths that reached exit: 2
	// CHCEK: Number of forks on branches: 1
	// CHECK: Found errors: 0
}
