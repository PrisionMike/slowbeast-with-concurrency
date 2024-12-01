 ; init : zeroed
 ; llvm : @v = dso_local global [2 x i8] zeroinitializer, align 1, !dbg !0
g1 = global  v of size 2:32b

fun thread1(a2)
  ; [bblock 19]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a2 to (*)arg 
   ; llvm :   store i8 49, i8* getelementptr inbounds ([2 x i8], [2 x i8]* @v, i32 0, i32 1), align 1, !dbg !26
   ; dbgloc : ('datarace_with_offset.c', 6, 10)
  store (8b)49:8b to (*)x22 
   ; llvm :   ret i8* null, !dbg !27
   ; dbgloc : ('datarace_with_offset.c', 7, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun llvm.dbg.declare(a4, a5, a6)

fun thread2(a8)
  ; [bblock 25]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg_1 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a8 to (*)arg_1 
   ; llvm :   store i8 50, i8* getelementptr inbounds ([2 x i8], [2 x i8]* @v, i32 0, i32 1), align 1, !dbg !26
   ; dbgloc : ('datarace_with_offset.c', 11, 10)
  store (8b)50:8b to (*)x28 
   ; llvm :   ret i8* null, !dbg !27
   ; dbgloc : ('datarace_with_offset.c', 12, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun main()
  ; [bblock 31]
   ; llvm :   %1 = alloca i32, align 4
  x32 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('t1', 'pthread_t')
  t1 = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('t2', 'pthread_t')
  t2 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x32 
   ; llvm :   %4 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #4, !dbg !31
   ; dbgloc : ('datarace_with_offset.c', 18, 5)
  x37: 32b = call __thread_create_succeeded() 
  x38 = thread thread1(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x38 to (*)t1 
   ; llvm :   %5 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #4, !dbg !32
   ; dbgloc : ('datarace_with_offset.c', 19, 5)
  x41: 32b = call __thread_create_succeeded() 
  x42 = thread thread2(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x42 to (*)t2 
   ; llvm :   %6 = load i32, i32* %2, align 4, !dbg !33
   ; dbgloc : ('datarace_with_offset.c', 21, 18)
  x44: 32b = load (*)t1 
   ; llvm :   %7 = call i32 @pthread_join(i32 noundef %6, i8** noundef null), !dbg !34
   ; dbgloc : ('datarace_with_offset.c', 21, 5)
  x46: 32b = call __join_succeeded() 
  x47 = thread join (x44) 
   ; llvm :   %8 = load i32, i32* %3, align 4, !dbg !35
   ; dbgloc : ('datarace_with_offset.c', 22, 18)
  x48: 32b = load (*)t2 
   ; llvm :   %9 = call i32 @pthread_join(i32 noundef %8, i8** noundef null), !dbg !36
   ; dbgloc : ('datarace_with_offset.c', 22, 5)
  x50: 32b = call __join_succeeded() 
  x51 = thread join (x48) 
   ; llvm :   ret i32 0, !dbg !37
   ; dbgloc : ('datarace_with_offset.c', 24, 5)
  ret (32b)0:32b 

nuf

fun pthread_create(a11, a12, a13, a14)

fun pthread_join(a16, a17)

fun __thread_create_succeeded()

fun __thread_create_succeeded()

fun __join_succeeded()

fun __join_succeeded()

