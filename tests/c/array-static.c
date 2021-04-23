#include <assert.h>

// RUN: clang %s -emit-llvm -g -c -o %t.bc
// RUN: rm -rf %t-out
// RUN: timeout 30 sb -out-dir=%t-out %opts %t.bc &>%t.log
// RUN: cat %t.log | FileCheck %s

int __VERIFIER_nondet_int();

unsigned x[100];

int main() {  
  int k = __VERIFIER_nondet_int();
  unsigned i = 0;
  assert(x[i] == 0);
  // CHECK-NOT: assertion failed!
  // CHECK-NOT: Error found.
  // CHECK: Found errors: 0
  return 0;
}
