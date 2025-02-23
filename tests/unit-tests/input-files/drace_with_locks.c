#include <pthread.h>

char v;
pthread_mutex_t lock;

void *thread1(void *arg) {
    pthread_mutex_lock(&lock);
    v = '1';
    pthread_mutex_unlock(&lock);
    return 0;
}

void *thread2(void *arg) {
    pthread_mutex_lock(&lock);
    v = '2';
    pthread_mutex_unlock(&lock);
    return 0;
}

int main() {
    pthread_t t1, t2;
    pthread_mutex_init(&lock, 0);

    pthread_create(&t1, 0, thread1, 0);
    pthread_create(&t2, 0, thread2, 0);

    pthread_join(t1, 0);
    pthread_join(t2, 0);

    pthread_mutex_destroy(&lock);
    return 0;
}
