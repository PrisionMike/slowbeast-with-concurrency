 ; init : zeroed
 ; llvm : @lock = dso_local global %union.pthread_mutex_t zeroinitializer, align 4, !dbg !0
g1 = global  lock of size 24:32b

 ; init : store (8b)0:8b to (*)g2
 ; llvm : @v = dso_local global i8 0, align 1, !dbg !5
g2 = global  v of size 1:32b

fun thread1(a4)
  ; [bblock 30]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a4 to (*)arg 
   ; llvm :   %3 = call i32 @pthread_mutex_lock(%union.pthread_mutex_t* noundef @lock) #4, !dbg !62
   ; dbgloc : ('drace_with_locks.c', 7, 5)
  x33: 32b = call pthread_mutex_lock((*)g1) 
   ; llvm :   store i8 49, i8* @v, align 1, !dbg !63
   ; dbgloc : ('drace_with_locks.c', 8, 7)
  store (8b)49:8b to (*)g2 
   ; llvm :   %4 = call i32 @pthread_mutex_unlock(%union.pthread_mutex_t* noundef @lock) #4, !dbg !64
   ; dbgloc : ('drace_with_locks.c', 9, 5)
  x35: 32b = call pthread_mutex_unlock((*)g1) 
   ; llvm :   ret i8* null, !dbg !65
   ; dbgloc : ('drace_with_locks.c', 10, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun llvm.dbg.declare(a6, a7, a8)

fun pthread_mutex_lock(a10)

fun pthread_mutex_unlock(a12)

fun thread2(a14)
  ; [bblock 37]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg_1 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a14 to (*)arg_1 
   ; llvm :   %3 = call i32 @pthread_mutex_lock(%union.pthread_mutex_t* noundef @lock) #4, !dbg !62
   ; dbgloc : ('drace_with_locks.c', 14, 5)
  x40: 32b = call pthread_mutex_lock((*)g1) 
   ; llvm :   store i8 50, i8* @v, align 1, !dbg !63
   ; dbgloc : ('drace_with_locks.c', 15, 7)
  store (8b)50:8b to (*)g2 
   ; llvm :   %4 = call i32 @pthread_mutex_unlock(%union.pthread_mutex_t* noundef @lock) #4, !dbg !64
   ; dbgloc : ('drace_with_locks.c', 16, 5)
  x42: 32b = call pthread_mutex_unlock((*)g1) 
   ; llvm :   ret i8* null, !dbg !65
   ; dbgloc : ('drace_with_locks.c', 17, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun main()
  ; [bblock 44]
   ; llvm :   %1 = alloca i32, align 4
  x45 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('t1', 'pthread_t')
  t1 = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('t2', 'pthread_t')
  t2 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x45 
   ; llvm :   %4 = call i32 @pthread_mutex_init(%union.pthread_mutex_t* noundef @lock, %union.pthread_mutexattr_t* noundef null) #4, !dbg !65
   ; dbgloc : ('drace_with_locks.c', 22, 5)
  x49: 32b = call pthread_mutex_init((*)g1, (*)ptr(0:32b, 0:32b)) 
   ; llvm :   %5 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #4, !dbg !66
   ; dbgloc : ('drace_with_locks.c', 24, 5)
  x51: 32b = call __thread_create_succeeded() 
  x52 = thread thread1(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x52 to (*)t1 
   ; llvm :   %6 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #4, !dbg !67
   ; dbgloc : ('drace_with_locks.c', 25, 5)
  x55: 32b = call __thread_create_succeeded() 
  x56 = thread thread2(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x56 to (*)t2 
   ; llvm :   %7 = load i32, i32* %2, align 4, !dbg !68
   ; dbgloc : ('drace_with_locks.c', 27, 18)
  x58: 32b = load (*)t1 
   ; llvm :   %8 = call i32 @pthread_join(i32 noundef %7, i8** noundef null), !dbg !69
   ; dbgloc : ('drace_with_locks.c', 27, 5)
  x60: 32b = call __join_succeeded() 
  x61 = thread join (x58) 
   ; llvm :   %9 = load i32, i32* %3, align 4, !dbg !70
   ; dbgloc : ('drace_with_locks.c', 28, 18)
  x62: 32b = load (*)t2 
   ; llvm :   %10 = call i32 @pthread_join(i32 noundef %9, i8** noundef null), !dbg !71
   ; dbgloc : ('drace_with_locks.c', 28, 5)
  x64: 32b = call __join_succeeded() 
  x65 = thread join (x62) 
   ; llvm :   %11 = call i32 @pthread_mutex_destroy(%union.pthread_mutex_t* noundef @lock) #4, !dbg !72
   ; dbgloc : ('drace_with_locks.c', 30, 5)
  x66: 32b = call pthread_mutex_destroy((*)g1) 
   ; llvm :   ret i32 0, !dbg !73
   ; dbgloc : ('drace_with_locks.c', 31, 5)
  ret (32b)0:32b 

nuf

fun pthread_mutex_init(a17, a18)

fun pthread_create(a20, a21, a22, a23)

fun pthread_join(a25, a26)

fun pthread_mutex_destroy(a28)

fun __thread_create_succeeded()

fun __thread_create_succeeded()

fun __join_succeeded()

fun __join_succeeded()

