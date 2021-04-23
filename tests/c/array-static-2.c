#include <assert.h>

// UNSUPPORTED: se
// UNSUPPORTED: kind
// UNSUPPORTED: kindse
// RUN: clang %s -emit-llvm -g -c -o %t.bc
// RUN: rm -rf %t-out
// RUN: timeout 30 sb -out-dir=%t-out %opts %t.bc &>%t.log
// RUN: cat %t.log | FileCheck %s

unsigned int nondet();

unsigned x[100];

int main() {  
  unsigned int k = nondet();
  if (k < 0 || k >= 100)
      return 0;
  assert(x[k] == 0);
  // CHECK-NOT: assertion failed!
  // CHECK-NOT: Error found.
  // CHECK: Found errors: 0
  return 0;
}
