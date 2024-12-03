#include <pthread.h>
#include <stdio.h>

char v, cond;

void *thread1(void *arg) {
    if (cond > 5) {  // Conditional race
        v = '1';
    }
    return 0;
}

void *thread2(void *arg) {
    if (cond > 5) {  // Conditional race
        v = '2';
    }
    return 0;
}

int main() {
    pthread_t t1, t2;

    cond = __VERIFIER_nondet_int();
    pthread_create(&t1, 0, thread1, 0);
    pthread_create(&t2, 0, thread2, 0);

    pthread_join(t1, 0);
    pthread_join(t2, 0);

    return 0;
}
