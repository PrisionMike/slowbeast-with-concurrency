 ; init : zeroed
 ; llvm : @mutex = dso_local global { { i32, i32, i32, i32, i32, [4 x i8], { %struct.anon, [4 x i8] } } } { { i32, i32, i32, i32, i32, [4 x i8], { %struct.anon, [4 x i8] } } { i32 0, i32 0, i32 0, i32 0, i32 0, [4 x i8] undef, { %struct.anon, [4 x i8] } { %struct.anon zeroinitializer, [4 x i8] undef } } }, align 8, !dbg !0
g1 = global  mutex of size 32:64b

 ; init : store (*)ptr(0:64b, 0:64b) to (*)g2
 ; llvm : @g1 = dso_local global i32* null, align 8, !dbg !11
g2 = global  g1 of size 8:64b

 ; init : store (32b)0:32b to (*)g4
 ; llvm : @g = dso_local global i32 0, align 4, !dbg !7
g4 = global  g of size 4:64b

 ; init : store (*)ptr(0:64b, 0:64b) to (*)g6
 ; llvm : @g2 = dso_local global i32* null, align 8, !dbg !14
g6 = global  g2 of size 8:64b

fun t_fun(a8)
  ; [bblock 27]
   ; llvm :   %2 = alloca i8*, align 8
   ; dbgvar : ('arg', '')
  arg = alloc 8:32b bytes 
   ; llvm :   store i8* %0, i8** %2, align 8
  store (*)a8 to (*)arg 
   ; llvm :   %3 = call i32 @pthread_mutex_lock(%union.pthread_mutex_t* noundef bitcast ({ { i32, i32, i32, i32, i32, [4 x i8], { %struct.anon, [4 x i8] } } }* @mutex to %union.pthread_mutex_t*)) #4, !dbg !64
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 684, 3)
  x30: 32b = call pthread_mutex_lock((*)g1) 
   ; llvm :   %4 = load i32*, i32** @g1, align 8, !dbg !65
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 685, 5)
  x31: * = load (*)g2 
   ; llvm :   %5 = load i32, i32* %4, align 4, !dbg !66
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 685, 8)
  x32: 32b = load (*)x31 
   ; llvm :   %6 = add nsw i32 %5, 1, !dbg !66
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 685, 8)
  x33:32b = (32b)x32 + (32b)1:32b 
   ; llvm :   store i32 %6, i32* %4, align 4, !dbg !66
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 685, 8)
  store (32b)x33 to (*)x31 
   ; llvm :   %7 = call i32 @pthread_mutex_unlock(%union.pthread_mutex_t* noundef bitcast ({ { i32, i32, i32, i32, i32, [4 x i8], { %struct.anon, [4 x i8] } } }* @mutex to %union.pthread_mutex_t*)) #4, !dbg !67
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 686, 3)
  x35: 32b = call pthread_mutex_unlock((*)g1) 
   ; llvm :   ret i8* null, !dbg !68
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 687, 3)
  ret (*)ptr(0:64b, 0:64b) 

nuf

fun llvm.dbg.declare(a10, a11, a12)

fun pthread_mutex_lock(a14)

fun pthread_mutex_unlock(a16)

fun main()
  ; [bblock 37]
   ; llvm :   %1 = alloca i32, align 4
  x38 = alloc 4:32b bytes 
   ; llvm :   %2 = alloca i64, align 8
   ; dbgvar : ('id', 'pthread_t')
  id = alloc 8:32b bytes 
   ; llvm :   %3 = alloca i32, align 4
   ; dbgvar : ('x', 'int')
  x = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x38 
   ; llvm :   store i32* @g, i32** @g2, align 8, !dbg !68
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 692, 11)
  store (*)g4 to (*)g6 
   ; llvm :   store i32* @g, i32** @g1, align 8, !dbg !69
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 692, 6)
  store (*)g4 to (*)g2 
   ; llvm :   %4 = call i32 @pthread_create(i64* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @t_fun, i8* noundef null) #4, !dbg !70
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 693, 3)
  x45: 32b = call __thread_create_succeeded() 
  x46 = thread t_fun(ptr(0:64b, 0:64b)) -> 64b 
  store (64b)x46 to (*)id 
   ; llvm :   %5 = load i32*, i32** @g2, align 8, !dbg !71
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 694, 5)
  x48: * = load (*)g6 
   ; llvm :   %6 = load i32, i32* %5, align 4, !dbg !72
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 694, 8)
  x49: 32b = load (*)x48 
   ; llvm :   %7 = add nsw i32 %6, 1, !dbg !72
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 694, 8)
  x50:32b = (32b)x49 + (32b)1:32b 
   ; llvm :   store i32 %7, i32* %5, align 4, !dbg !72
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 694, 8)
  store (32b)x50 to (*)x48 
   ; llvm :   %8 = load i64, i64* %2, align 8, !dbg !73
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 695, 17)
  x52: 64b = load (*)id 
   ; llvm :   %9 = call i32 @pthread_join(i64 noundef %8, i8** noundef null), !dbg !74
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 695, 3)
  x54: 32b = call __join_succeeded() 
  x55 = thread join (x52) 
   ; llvm :   ret i32 0, !dbg !75
   ; dbgloc : ('tests/tdd/array-errors/input-files/04-mutex_37-indirect_rc.i', 696, 3)
  ret (32b)0:32b 

nuf

fun pthread_create(a19, a20, a21, a22)

fun pthread_join(a24, a25)

fun __thread_create_succeeded()

fun __join_succeeded()

