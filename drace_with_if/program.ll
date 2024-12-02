 ; init : store (8b)0:8b to (*)g1
 ; llvm : @cond = dso_local global i8 0, align 1, !dbg !0
g1 = global  cond of size 1:32b

 ; init : store (8b)0:8b to (*)g3
 ; llvm : @v = dso_local global i8 0, align 1, !dbg !5
g3 = global  v of size 1:32b

fun thread1(a5)
  ; [bblock 23]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a5 to (*)arg 
   ; llvm :   %3 = load i8, i8* @cond, align 1, !dbg !25
   ; dbgloc : ('drace_withif.c', 7, 9)
  x28: 8b = load (*)g1 
   ; llvm :   %4 = sext i8 %3 to i32, !dbg !25
   ; dbgloc : ('drace_withif.c', 7, 9)
  x29: 32b = extend signed (8b)x28 to 32 bits 
   ; llvm :   %5 = icmp sgt i32 %4, 5, !dbg !27
   ; dbgloc : ('drace_withif.c', 7, 14)
  x30: bool = cmp (32b)x29 > (32b)5:32b 
   ; llvm :   br i1 %5, label %6, label %7, !dbg !28
   ; dbgloc : ('drace_withif.c', 7, 9)
  branch x30 ? bblock 24 : bblock 25 

  ; [bblock 24]
   ; llvm :   store i8 49, i8* @v, align 1, !dbg !29
   ; dbgloc : ('drace_withif.c', 8, 11)
  store (8b)49:8b to (*)g3 
   ; llvm :   br label %7, !dbg !31
   ; dbgloc : ('drace_withif.c', 9, 5)
  branch True:bool ? bblock 25 : bblock 25 

  ; [bblock 25]
   ; llvm :   ret i8* null, !dbg !32
   ; dbgloc : ('drace_withif.c', 10, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun llvm.dbg.declare(a7, a8, a9)

fun thread2(a11)
  ; [bblock 35]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg_1 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a11 to (*)arg_1 
   ; llvm :   %3 = load i8, i8* @cond, align 1, !dbg !25
   ; dbgloc : ('drace_withif.c', 14, 9)
  x40: 8b = load (*)g1 
   ; llvm :   %4 = sext i8 %3 to i32, !dbg !25
   ; dbgloc : ('drace_withif.c', 14, 9)
  x41: 32b = extend signed (8b)x40 to 32 bits 
   ; llvm :   %5 = icmp sle i32 %4, 5, !dbg !27
   ; dbgloc : ('drace_withif.c', 14, 14)
  x42: bool = cmp (32b)x41 <= (32b)5:32b 
   ; llvm :   br i1 %5, label %6, label %7, !dbg !28
   ; dbgloc : ('drace_withif.c', 14, 9)
  branch x42 ? bblock 36 : bblock 37 

  ; [bblock 36]
   ; llvm :   store i8 50, i8* @v, align 1, !dbg !29
   ; dbgloc : ('drace_withif.c', 15, 11)
  store (8b)50:8b to (*)g3 
   ; llvm :   br label %7, !dbg !31
   ; dbgloc : ('drace_withif.c', 16, 5)
  branch True:bool ? bblock 37 : bblock 37 

  ; [bblock 37]
   ; llvm :   ret i8* null, !dbg !32
   ; dbgloc : ('drace_withif.c', 17, 5)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun main()
  ; [bblock 47]
   ; llvm :   %1 = alloca i32, align 4
  x48 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('t1', 'pthread_t')
  t1 = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('t2', 'pthread_t')
  t2 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x48 
   ; llvm :   %4 = call i32 bitcast (i32 (...)* @__VERIFIER_nondet_int to i32 ()*)(), !dbg !30
   ; dbgloc : ('drace_withif.c', 23, 12)
  x52: 32b = call __VERIFIER_nondet_int() 
   ; llvm :   %5 = trunc i32 %4 to i8, !dbg !30
   ; dbgloc : ('drace_withif.c', 23, 12)
  x53:8b = extractbits 0-7 from (32b)x52 
   ; llvm :   store i8 %5, i8* @cond, align 1, !dbg !31
   ; dbgloc : ('drace_withif.c', 23, 10)
  store (8b)x53 to (*)g1 
   ; llvm :   %6 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #4, !dbg !32
   ; dbgloc : ('drace_withif.c', 24, 5)
  x56: 32b = call __thread_create_succeeded() 
  x57 = thread thread1(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x57 to (*)t1 
   ; llvm :   %7 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #4, !dbg !33
   ; dbgloc : ('drace_withif.c', 25, 5)
  x60: 32b = call __thread_create_succeeded() 
  x61 = thread thread2(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x61 to (*)t2 
   ; llvm :   %8 = load i32, i32* %2, align 4, !dbg !34
   ; dbgloc : ('drace_withif.c', 27, 18)
  x63: 32b = load (*)t1 
   ; llvm :   %9 = call i32 @pthread_join(i32 noundef %8, i8** noundef null), !dbg !35
   ; dbgloc : ('drace_withif.c', 27, 5)
  x65: 32b = call __join_succeeded() 
  x66 = thread join (x63) 
   ; llvm :   %10 = load i32, i32* %3, align 4, !dbg !36
   ; dbgloc : ('drace_withif.c', 28, 18)
  x67: 32b = load (*)t2 
   ; llvm :   %11 = call i32 @pthread_join(i32 noundef %10, i8** noundef null), !dbg !37
   ; dbgloc : ('drace_withif.c', 28, 5)
  x69: 32b = call __join_succeeded() 
  x70 = thread join (x67) 
   ; llvm :   ret i32 0, !dbg !38
   ; dbgloc : ('drace_withif.c', 30, 5)
  ret (32b)0:32b 

nuf

fun __VERIFIER_nondet_int()

fun pthread_create(a15, a16, a17, a18)

fun pthread_join(a20, a21)

fun __thread_create_succeeded()

fun __thread_create_succeeded()

fun __join_succeeded()

fun __join_succeeded()

