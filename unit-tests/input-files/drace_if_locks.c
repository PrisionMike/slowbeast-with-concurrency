#include <pthread.h>
#include <stdio.h>

// Shared variable and condition
char v, cond;
// Mutex for synchronization
pthread_mutex_t mutex;

void *thread1(void *arg) {
    if (cond < 5) {
        // Lock the mutex for safe access
        pthread_mutex_lock(&mutex);
        v = '1';
        pthread_mutex_unlock(&mutex);
    } else {
        // No locking, potential data race
        v = '1';
    }
    return 0;
}

void *thread2(void *arg) {
    if (cond < 5) {
        // Lock the mutex for safe access
        pthread_mutex_lock(&mutex);
        v = '2';
        pthread_mutex_unlock(&mutex);
    } else {
        // No locking, potential data race
        v = '2';
    }
    return 0;
}

int main() {
    pthread_t t1, t2;

    // Initialize the mutex
    if (pthread_mutex_init(&mutex, NULL) != 0) {
        printf("Mutex initialization failed\n");
        return 1;
    }

    // Use a function or logic to determine the value of cond
    cond = __VERIFIER_nondet_int(); // Replace with your own logic if needed

    // Create threads
    pthread_create(&t1, NULL, thread1, NULL);
    pthread_create(&t2, NULL, thread2, NULL);

    // Wait for threads to complete
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    // Destroy the mutex
    pthread_mutex_destroy(&mutex);

    return 0;
}
