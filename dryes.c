#include <pthread.h>
char v;
void *thread1(void * arg){
  v = '1';
  return 0;}
void *thread2(void *arg){
  v = '2';
  return 0;}
int main(){
  pthread_t t1, t2;
  pthread_create(&t1, 0, thread1, 0);
  pthread_create(&t2, 0, thread2, 0);
  pthread_join(t1, 0);
  pthread_join(t2, 0);
  return 0;}