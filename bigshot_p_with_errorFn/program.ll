 ; init : store ([i8; 2])[48:8b, 0:8b]:[i8; 2] to (*)g1
 ; llvm : @.str = private unnamed_addr constant [2 x i8] c"0\00", align 1
g1 = global constant  .str of size 2:32b

 ; init : store ([i8; 51])[47:8b, 104:8b, 111:8b, 109:8b, 101:8b, 47:8b, 120:8b, 115:8b, 104:8b, 97:8b, 110:8b, 100:8b, 105:8b, 108:8b, 47:8b, 98:8b, 101:8b, 110:8b, 95:8b, 115:8b, 104:8b, 97:8b, 110:8b, 100:8b, 105:8b, 108:8b, 121:8b, 97:8b, 47:8b, 115:8b, 108:8b, 111:8b, 119:8b, 98:8b, 101:8b, 97:8b, 115:8b, 116:8b, 47:8b, 98:8b, 105:8b, 103:8b, 115:8b, 104:8b, 111:8b, 116:8b, 95:8b, 112:8b, 46:8b, 99:8b, 0:8b]:[i8; 51] to (*)g3
 ; llvm : @.str.1 = private unnamed_addr constant [51 x i8] c"/home/xshandil/ben_shandilya/slowbeast/bigshot_p.c\00", align 1
g3 = global constant  .str.1 of size 51:32b

 ; init : store ([i8; 19])[118:8b, 111:8b, 105:8b, 100:8b, 32:8b, 114:8b, 101:8b, 97:8b, 99:8b, 104:8b, 95:8b, 101:8b, 114:8b, 114:8b, 111:8b, 114:8b, 40:8b, 41:8b, 0:8b]:[i8; 19] to (*)g5
 ; llvm : @__PRETTY_FUNCTION__.reach_error = private unnamed_addr constant [19 x i8] c"void reach_error()\00", align 1
g5 = global constant  __PRETTY_FUNCTION__.reach_error of size 19:32b

 ; init : store (*)ptr(0:32b, 0:32b) to (*)g7
 ; llvm : @v = dso_local global i8* null, align 4, !dbg !0
g7 = global  v of size 4:32b

 ; init : store ([i8; 8])[66:8b, 105:8b, 103:8b, 115:8b, 104:8b, 111:8b, 116:8b, 0:8b]:[i8; 8] to (*)g9
 ; llvm : @.str.2 = private unnamed_addr constant [8 x i8] c"Bigshot\00", align 1
g9 = global constant  .str.2 of size 8:32b

fun reach_error()
  ; [bblock 45]
   ; llvm :   call void @__assert_fail(i8* noundef getelementptr inbounds ([2 x i8], [2 x i8]* @.str, i32 0, i32 0), i8* noundef getelementptr inbounds ([51 x i8], [51 x i8]* @.str.1, i32 0, i32 0), i32 noundef 11, i8* noundef getelementptr inbounds ([19 x i8], [19 x i8]* @__PRETTY_FUNCTION__.reach_error, i32 0, i32 0)) #5, !dbg !21
   ; dbgloc : ('bigshot_p.c', 11, 22)
  assume False:bool 
   ; llvm :   unreachable, !dbg !21
   ; dbgloc : ('bigshot_p.c', 11, 22)
  assert False:bool, "unreachable" 

nuf

fun __assert_fail(a12, a13, a14, a15)

fun __VERIFIER_assert(a17)
  ; [bblock 48]
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('expression', 'int')
  expression = alloc 4:32b bytes 
   ; llvm :   store i32 %0, i32* %2, align 4
  store (32b)a17 to (*)expression 
   ; llvm :   %3 = load i32, i32* %2, align 4, !dbg !24
   ; dbgloc : ('bigshot_p.c', 16, 47)
  x54: 32b = load (*)expression 
   ; llvm :   %4 = icmp ne i32 %3, 0, !dbg !24
   ; dbgloc : ('bigshot_p.c', 16, 47)
  x55: bool = cmp (32b)x54 != (32b)0:32b 
   ; llvm :   br i1 %4, label %7, label %5, !dbg !26
   ; dbgloc : ('bigshot_p.c', 16, 46)
  branch x55 ? bblock 51 : bblock 49 

  ; [bblock 49]
   ; llvm :   br label %6, !dbg !27
   ; dbgloc : ('bigshot_p.c', 16, 59)
  branch True:bool ? bblock 50 : bblock 50 

  ; [bblock 50]
   ; llvm :   call void @reach_error(), !dbg !31
   ; dbgloc : ('bigshot_p.c', 16, 69)
  assert False:bool, "error function called!" 
   ; llvm :   call void @abort() #5, !dbg !33
   ; dbgloc : ('bigshot_p.c', 16, 83)
  call abort() 
   ; llvm :   unreachable, !dbg !33
   ; dbgloc : ('bigshot_p.c', 16, 83)
  assert False:bool, "unreachable" 

  ; [bblock 51]
   ; llvm :   ret void, !dbg !34
   ; dbgloc : ('bigshot_p.c', 16, 95)
  ret 

nuf

fun llvm.dbg.declare(a19, a20, a21)

fun llvm.dbg.label(a23)

fun abort()

fun _strcpy(a26, a27)
  ; [bblock 62]
   ; llvm :   %3 = alloca i8*, align 4
   ; dbgvar : ('dest', '')
  dest = alloc 4:32b bytes 
   ; llvm :   %4 = alloca i8*, align 4
   ; dbgvar : ('src', '')
  src = alloc 4:32b bytes 
   ; llvm :   %5 = alloca i8*, align 4
   ; dbgvar : ('save', '')
  save = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %3, align 4
  store (*)a26 to (*)dest 
   ; llvm :   store i8* %1, i8** %4, align 4
  store (*)a27 to (*)src 
   ; llvm :   %6 = load i8*, i8** %3, align 4, !dbg !29
   ; dbgloc : ('bigshot_p.c', 19, 18)
  x71: * = load (*)dest 
   ; llvm :   store i8* %6, i8** %5, align 4, !dbg !28
   ; dbgloc : ('bigshot_p.c', 19, 11)
  store (*)x71 to (*)save 
   ; llvm :   br label %7, !dbg !30
   ; dbgloc : ('bigshot_p.c', 20, 5)
  branch True:bool ? bblock 63 : bblock 63 

  ; [bblock 63]
   ; llvm :   %8 = load i8*, i8** %4, align 4, !dbg !31
   ; dbgloc : ('bigshot_p.c', 20, 27)
  x74: * = load (*)src 
   ; llvm :   %9 = getelementptr inbounds i8, i8* %8, i32 1, !dbg !31
   ; dbgloc : ('bigshot_p.c', 20, 27)
  x75:* = (*)x74 + (32b)1:32b 
   ; llvm :   store i8* %9, i8** %4, align 4, !dbg !31
   ; dbgloc : ('bigshot_p.c', 20, 27)
  store (*)x75 to (*)src 
   ; llvm :   %10 = load i8, i8* %8, align 1, !dbg !32
   ; dbgloc : ('bigshot_p.c', 20, 23)
  x77: 8b = load (*)x74 
   ; llvm :   %11 = load i8*, i8** %3, align 4, !dbg !33
   ; dbgloc : ('bigshot_p.c', 20, 18)
  x78: * = load (*)dest 
   ; llvm :   %12 = getelementptr inbounds i8, i8* %11, i32 1, !dbg !33
   ; dbgloc : ('bigshot_p.c', 20, 18)
  x79:* = (*)x78 + (32b)1:32b 
   ; llvm :   store i8* %12, i8** %3, align 4, !dbg !33
   ; dbgloc : ('bigshot_p.c', 20, 18)
  store (*)x79 to (*)dest 
   ; llvm :   store i8 %10, i8* %11, align 1, !dbg !34
   ; dbgloc : ('bigshot_p.c', 20, 21)
  store (8b)x77 to (*)x78 
   ; llvm :   %13 = icmp ne i8 %10, 0, !dbg !30
   ; dbgloc : ('bigshot_p.c', 20, 5)
  x82: bool = cmp (8b)x77 != (8b)0:8b 
   ; llvm :   br i1 %13, label %14, label %15, !dbg !30
   ; dbgloc : ('bigshot_p.c', 20, 5)
  branch x82 ? bblock 64 : bblock 65 

  ; [bblock 64]
   ; llvm :   br label %7, !dbg !30, !llvm.loop !35
   ; dbgloc : ('bigshot_p.c', 20, 5)
  branch True:bool ? bblock 63 : bblock 63 

  ; [bblock 65]
   ; llvm :   %16 = load i8*, i8** %5, align 4, !dbg !38
   ; dbgloc : ('bigshot_p.c', 21, 12)
  x85: * = load (*)save 
   ; llvm :   ret i8* %16, !dbg !39
   ; dbgloc : ('bigshot_p.c', 21, 5)
  ret (*)x85 

nuf

fun thread1(a29)
  ; [bblock 87]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a29 to (*)arg 
  x90:32b = (32b)8:32b * (32b)1:32b 
   ; llvm :   %3 = call noalias i8* @calloc(i32 noundef 8, i32 noundef 1) #5, !dbg !24
   ; dbgloc : ('bigshot_p.c', 28, 7)
  x91 = alloc x90 bytes on heap zeroed 
   ; llvm :   store i8* %3, i8** @v, align 4, !dbg !25
   ; dbgloc : ('bigshot_p.c', 28, 5)
  store (*)x91 to (*)g7 
   ; llvm :   ret i8* null, !dbg !26
   ; dbgloc : ('bigshot_p.c', 29, 3)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun calloc(a31, a32)

fun thread2(a34)
  ; [bblock 94]
   ; llvm :   %2 = alloca i8*, align 4
   ; dbgvar : ('arg', '')
  arg_1 = alloc 4:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 4
  store (*)a34 to (*)arg_1 
   ; llvm :   %3 = load i8*, i8** @v, align 4, !dbg !24
   ; dbgloc : ('bigshot_p.c', 34, 7)
  x99: * = load (*)g7 
   ; llvm :   %4 = icmp ne i8* %3, null, !dbg !24
   ; dbgloc : ('bigshot_p.c', 34, 7)
  x100: bool = cmp (*)x99 != (*)ptr(0:32b, 0:32b) 
   ; llvm :   br i1 %4, label %5, label %8, !dbg !26
   ; dbgloc : ('bigshot_p.c', 34, 7)
  branch x100 ? bblock 95 : bblock 96 

  ; [bblock 95]
   ; llvm :   %6 = load i8*, i8** @v, align 4, !dbg !27
   ; dbgloc : ('bigshot_p.c', 34, 18)
  x102: * = load (*)g7 
   ; llvm :   %7 = call i8* @_strcpy(i8* noundef %6, i8* noundef getelementptr inbounds ([8 x i8], [8 x i8]* @.str.2, i32 0, i32 0)), !dbg !28
   ; dbgloc : ('bigshot_p.c', 34, 10)
  x103: * = call _strcpy((*)x102, (*)g9) 
   ; llvm :   br label %8, !dbg !28
   ; dbgloc : ('bigshot_p.c', 34, 10)
  branch True:bool ? bblock 96 : bblock 96 

  ; [bblock 96]
   ; llvm :   ret i8* null, !dbg !29
   ; dbgloc : ('bigshot_p.c', 35, 3)
  ret (*)ptr(0:32b, 0:32b) 

nuf

fun main()
  ; [bblock 106]
   ; llvm :   %1 = alloca i32, align 4
  x109 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('t1', 'pthread_t')
  t1 = alloc 4:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('t2', 'pthread_t')
  t2 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x109 
   ; llvm :   %4 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #5, !dbg !29
   ; dbgloc : ('bigshot_p.c', 43, 3)
  x114: 32b = call __thread_create_succeeded() 
  x115 = thread thread1(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x115 to (*)t1 
   ; llvm :   %5 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #5, !dbg !30
   ; dbgloc : ('bigshot_p.c', 44, 3)
  x118: 32b = call __thread_create_succeeded() 
  x119 = thread thread2(ptr(0:32b, 0:32b)) -> 32b 
  store (32b)x119 to (*)t2 
   ; llvm :   %6 = load i32, i32* %2, align 4, !dbg !31
   ; dbgloc : ('bigshot_p.c', 45, 16)
  x121: 32b = load (*)t1 
   ; llvm :   %7 = call i32 @pthread_join(i32 noundef %6, i8** noundef null), !dbg !32
   ; dbgloc : ('bigshot_p.c', 45, 3)
  x123: 32b = call __join_succeeded() 
  x124 = thread join (x121) 
   ; llvm :   %8 = load i32, i32* %3, align 4, !dbg !33
   ; dbgloc : ('bigshot_p.c', 46, 16)
  x125: 32b = load (*)t2 
   ; llvm :   %9 = call i32 @pthread_join(i32 noundef %8, i8** noundef null), !dbg !34
   ; dbgloc : ('bigshot_p.c', 46, 3)
  x127: 32b = call __join_succeeded() 
  x128 = thread join (x125) 
   ; llvm :   %10 = load i8*, i8** @v, align 4, !dbg !35
   ; dbgloc : ('bigshot_p.c', 48, 22)
  x129: * = load (*)g7 
   ; llvm :   %11 = icmp ne i8* %10, null, !dbg !35
   ; dbgloc : ('bigshot_p.c', 48, 22)
  x130: bool = cmp (*)x129 != (*)ptr(0:32b, 0:32b) 
  x137 = alloc 1:32b bytes 
  store (1b)True:bool to (*)x137 
   ; llvm :   br i1 %11, label %12, label %18, !dbg !36
   ; dbgloc : ('bigshot_p.c', 48, 24)
  branch x130 ? bblock 107 : bblock 108 

  ; [bblock 107]
   ; llvm :   %13 = load i8*, i8** @v, align 4, !dbg !37
   ; dbgloc : ('bigshot_p.c', 48, 27)
   ; llvm :   %14 = getelementptr inbounds i8, i8* %13, i32 0, !dbg !37
   ; dbgloc : ('bigshot_p.c', 48, 27)
  x132: * = load (*)g7 
   ; llvm :   %15 = load i8, i8* %14, align 1, !dbg !37
   ; dbgloc : ('bigshot_p.c', 48, 27)
  x133: 8b = load (*)x132 
   ; llvm :   %16 = sext i8 %15 to i32, !dbg !37
   ; dbgloc : ('bigshot_p.c', 48, 27)
  x134: 32b = extend signed (8b)x133 to 32 bits 
   ; llvm :   %17 = icmp eq i32 %16, 66, !dbg !38
   ; dbgloc : ('bigshot_p.c', 48, 32)
  x135: bool = cmp (32b)x134 == (32b)66:32b 
  store (1b)x135 to (*)x137 
   ; llvm :   br label %18, !dbg !36
   ; dbgloc : ('bigshot_p.c', 48, 24)
  branch True:bool ? bblock 108 : bblock 108 

  ; [bblock 108]
   ; llvm :   %19 = phi i1 [ true, %0 ], [ %17, %12 ]
  x138: 1b = load (1b)x137 
   ; llvm :   %20 = zext i1 %19 to i32, !dbg !36
   ; dbgloc : ('bigshot_p.c', 48, 24)
  x139: 32b = extend unsigned (1b)x138 to 32 bits 
   ; llvm :   call void @__VERIFIER_assert(i32 noundef %20), !dbg !39
   ; dbgloc : ('bigshot_p.c', 48, 3)
  call __VERIFIER_assert((32b)x139) 
   ; llvm :   ret i32 0, !dbg !40
   ; dbgloc : ('bigshot_p.c', 50, 3)
  ret (32b)0:32b 

nuf

fun pthread_create(a37, a38, a39, a40)

fun pthread_join(a42, a43)

fun __thread_create_succeeded()

fun __thread_create_succeeded()

fun __join_succeeded()

fun __join_succeeded()

