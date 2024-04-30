fun fun(a1)
  ; [bblock 8]
   ; llvm :   %2 = alloca i32, align 4
   ; dbgvar : ('arg', 'int')
  arg = alloc 4:32b bytes 
   ; llvm :   store i32 %0, i32* %2, align 4
  store (32b)a1 to (*)arg 
   ; llvm :   %3 = load i32, i32* %2, align 4, !dbg !19
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/howFunitis.c', 2, 12)
  x11: 32b = load (*)arg 
   ; llvm :   %4 = add nsw i32 %3, 5, !dbg !20
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/howFunitis.c', 2, 15)
  x12:32b = (32b)x11 + (32b)5:32b 
   ; llvm :   ret i32 %4, !dbg !21
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/howFunitis.c', 2, 5)
  ret (32b)x12 

nuf

fun llvm.dbg.declare(a3, a4, a5)

fun main()
  ; [bblock 14]
   ; llvm :   %1 = alloca i32, align 4
  x15 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x15 
   ; llvm :   %2 = call i32 @fun(i32 noundef 8), !dbg !17
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/howFunitis.c', 6, 3)
  x17: 32b = call fun((32b)8:32b) 
   ; llvm :   ret i32 0, !dbg !18
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/howFunitis.c', 7, 3)
  ret (32b)0:32b 

nuf

