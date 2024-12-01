 ; init : store (8b)0:8b to (*)g1
 ; llvm : @v = dso_local global i8 0, align 1, !dbg !0
g1 = global  v of size 1:32b

fun thread1(a3)
  ; [bblock 20]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('c1', 'int')
  c1 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a3 to (*)arg 
   ; llvm :   %4 = load i32, i32* %3, align 4, !dbg !26
   ; dbgloc : ('drace_withif.c', 8, 9)
  x26: 32b = load (*)c1 
   ; llvm :   %5 = icmp sgt i32 %4, 5, !dbg !28
   ; dbgloc : ('drace_withif.c', 8, 12)
  x27: bool = cmp (32b)x26 > (32b)5:32b 
   ; llvm :   br i1 %5, label %6, label %7, !dbg !29
   ; dbgloc : ('drace_withif.c', 8, 9)
  branch x27 ? bblock 21 : bblock 22 

  ; [bblock 21]
   ; llvm :   store i8 49, i8* @v, align 1, !dbg !30
   ; dbgloc : ('drace_withif.c', 9, 11)
  store (8b)49:8b to (*)g1 
   ; llvm :   br label %7, !dbg !32
   ; dbgloc : ('drace_withif.c', 10, 5)
  branch True:bool ? bblock 22 : bblock 22 

  ; [bblock 22]
   ; llvm :   ret i8* null, !dbg !33
   ; dbgloc : ('drace_withif.c', 11, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun llvm.dbg.declare(a5, a6, a7)

fun thread2(a9)
  ; [bblock 32]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg_1 = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('c2', 'int')
  c2 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a9 to (*)arg_1 
   ; llvm :   %4 = load i32, i32* %3, align 4, !dbg !26
   ; dbgloc : ('drace_withif.c', 16, 9)
  x38: 32b = load (*)c2 
   ; llvm :   %5 = icmp slt i32 %4, 5, !dbg !28
   ; dbgloc : ('drace_withif.c', 16, 12)
  x39: bool = cmp (32b)x38 < (32b)5:32b 
   ; llvm :   br i1 %5, label %6, label %7, !dbg !29
   ; dbgloc : ('drace_withif.c', 16, 9)
  branch x39 ? bblock 33 : bblock 34 

  ; [bblock 33]
   ; llvm :   store i8 50, i8* @v, align 1, !dbg !30
   ; dbgloc : ('drace_withif.c', 17, 11)
  store (8b)50:8b to (*)g1 
   ; llvm :   br label %7, !dbg !32
   ; dbgloc : ('drace_withif.c', 18, 5)
  branch True:bool ? bblock 34 : bblock 34 

  ; [bblock 34]
   ; llvm :   ret i8* null, !dbg !33
   ; dbgloc : ('drace_withif.c', 19, 5)
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
   ; llvm :   %4 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #4, !dbg !28
   ; dbgloc : ('drace_withif.c', 25, 5)
  x50: 32b = call __thread_create_succeeded() 
  x51 = thread thread1(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x51 to (*)t1 
   ; llvm :   %5 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #4, !dbg !29
   ; dbgloc : ('drace_withif.c', 26, 5)
  x54: 32b = call __thread_create_succeeded() 
  x55 = thread thread2(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x55 to (*)t2 
   ; llvm :   %6 = load i32, i32* %2, align 4, !dbg !30
   ; dbgloc : ('drace_withif.c', 28, 18)
  x57: 32b = load (*)t1 
   ; llvm :   %7 = call i32 @pthread_join(i32 noundef %6, i8** noundef null), !dbg !31
   ; dbgloc : ('drace_withif.c', 28, 5)
  x59: 32b = call __join_succeeded() 
  x60 = thread join (x57) 
   ; llvm :   %8 = load i32, i32* %3, align 4, !dbg !32
   ; dbgloc : ('drace_withif.c', 29, 18)
  x61: 32b = load (*)t2 
   ; llvm :   %9 = call i32 @pthread_join(i32 noundef %8, i8** noundef null), !dbg !33
   ; dbgloc : ('drace_withif.c', 29, 5)
  x63: 32b = call __join_succeeded() 
  x64 = thread join (x61) 
   ; llvm :   ret i32 0, !dbg !34
   ; dbgloc : ('drace_withif.c', 31, 5)
  ret (32b)0:32b 

nuf

fun pthread_create(a12, a13, a14, a15)

fun pthread_join(a17, a18)

fun __thread_create_succeeded()

fun __thread_create_succeeded()

fun __join_succeeded()

fun __join_succeeded()

