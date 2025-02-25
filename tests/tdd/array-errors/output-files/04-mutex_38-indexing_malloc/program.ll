 ; init : zeroed
 ; llvm : @mutex = dso_local global { { i32, i32, i32, i32, i32, [4 x i8], { %struct.anon, [4 x i8] } } } { { i32, i32, i32, i32, i32, [4 x i8], { %struct.anon, [4 x i8] } } { i32 0, i32 0, i32 0, i32 0, i32 0, [4 x i8] undef, { %struct.anon, [4 x i8] } { %struct.anon zeroinitializer, [4 x i8] undef } } }, align 8, !dbg !0
g1 = global  mutex of size 32:64b

 ; init : store (*)ptr(0:64b, 0:64b) to (*)g2
 ; llvm : @s = dso_local global i32* null, align 8, !dbg !9
g2 = global  s of size 8:64b

fun t_fun(a4)
  ; [bblock 21]
   ; llvm :   %2 = alloca i8*, align 8
   ; dbgvar : ('arg', '')
  arg = alloc 8:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 8
  store (*)a4 to (*)arg 
   ; llvm :   %3 = load i32*, i32** @s, align 8, !dbg !60
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 990, 3)
   ; llvm :   %4 = getelementptr inbounds i32, i32* %3, i64 0, !dbg !60
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 990, 3)
  x24: * = load (*)g2 
   ; llvm :   store i32 8, i32* %4, align 4, !dbg !61
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 990, 8)
  store (32b)8:32b to (*)x24 
   ; llvm :   ret i8* null, !dbg !62
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 991, 3)
  ret (*)ptr(0:64b, 0:64b) 

nuf

fun llvm.dbg.declare(a6, a7, a8)

fun main()
  ; [bblock 27]
   ; llvm :   %1 = alloca i32, align 4
  x28 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i64, align 8
   ; dbgvar : ('id', 'pthread_t')
  id = alloc 8:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x28 
   ; llvm :   %3 = call noalias i8* @malloc(i32 noundef 4) #5, !dbg !62
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 995, 13)
  x31 = alloc 4:32b bytes on heap 
  x32:* = cast (*)x31 to signed * 
   ; llvm :   store i32* %4, i32** @s, align 8, !dbg !64
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 995, 5)
  store (*)x32 to (*)g2 
   ; llvm :   %5 = call i32 @pthread_create(i64* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @t_fun, i8* noundef null) #6, !dbg !65
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 996, 3)
  x35: 32b = call __thread_create_succeeded() 
  x36 = thread t_fun(ptr(0:64b, 0:64b)) -> 64b 
  store (64b)x36 to (*)id 
   ; llvm :   %6 = load i32*, i32** @s, align 8, !dbg !66
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 997, 3)
   ; llvm :   %7 = getelementptr inbounds i32, i32* %6, i64 0, !dbg !66
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 997, 3)
  x38: * = load (*)g2 
   ; llvm :   store i32 9, i32* %7, align 4, !dbg !67
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 997, 8)
  store (32b)9:32b to (*)x38 
   ; llvm :   %8 = load i64, i64* %2, align 8, !dbg !68
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 998, 17)
  x40: 64b = load (*)id 
   ; llvm :   %9 = call i32 @pthread_join(i64 noundef %8, i8** noundef null), !dbg !69
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 998, 3)
  x42: 32b = call __join_succeeded() 
  x43 = thread join (x40) 
   ; llvm :   ret i32 0, !dbg !70
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_38-indexing_malloc.i', 999, 3)
  ret (32b)0:32b 

nuf

fun malloc(a11)

fun pthread_create(a13, a14, a15, a16)

fun pthread_join(a18, a19)

fun __thread_create_succeeded()

fun __join_succeeded()

