 ; init : store (8b)0:8b to (*)g1
 ; llvm : @v = dso_local global i8 0, align 1, !dbg !0
g1 = global  v of size 1:32b

fun thread1(a3)
  ; [bblock 20]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a3 to (*)arg 
   ; llvm :   store i8 49, i8* @v, align 1, !dbg !23
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 6, 5)
  store (8b)49:8b to (*)g1 
   ; llvm :   ret i8* null, !dbg !24
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 7, 3)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun llvm.dbg.declare(a5, a6, a7)

fun thread2(a9)
  ; [bblock 25]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg_1 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a9 to (*)arg_1 
   ; llvm :   store i8 50, i8* @v, align 1, !dbg !23
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 11, 5)
  store (8b)50:8b to (*)g1 
   ; llvm :   ret i8* null, !dbg !24
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 12, 3)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun main()
  ; [bblock 30]
   ; llvm :   %1 = alloca i32, align 4
  x31 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('t1', 'pthread_t')
  t1 = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('t2', 'pthread_t')
  t2 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x31 
   ; llvm :   %4 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #4, !dbg !28
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 18, 3)
  x36: 32b = call __thread_create_succeeded() 
  x37 = thread thread1(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x37 to (*)t1 
   ; llvm :   %5 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #4, !dbg !29
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 19, 3)
  x40: 32b = call __thread_create_succeeded() 
  x41 = thread thread2(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x41 to (*)t2 
   ; llvm :   %6 = load i32, i32* %2, align 4, !dbg !30
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 21, 16)
  x43: 32b = load (*)t1 
   ; llvm :   %7 = call i32 @pthread_join(i32 noundef %6, i8** noundef null), !dbg !31
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 21, 3)
  x45: 32b = call __join_succeeded() 
  x46 = thread join (x43) 
   ; llvm :   %8 = load i32, i32* %3, align 4, !dbg !32
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 22, 16)
  x47: 32b = load (*)t2 
   ; llvm :   %9 = call i32 @pthread_join(i32 noundef %8, i8** noundef null), !dbg !33
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 22, 3)
  x49: 32b = call __join_succeeded() 
  x50 = thread join (x47) 
   ; llvm :   ret i32 0, !dbg !34
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/dryes.c', 24, 3)
  ret (32b)0:32b 

nuf

fun pthread_create(a12, a13, a14, a15)

fun pthread_join(a17, a18)

fun __thread_create_succeeded()

fun __thread_create_succeeded()

fun __join_succeeded()

fun __join_succeeded()

