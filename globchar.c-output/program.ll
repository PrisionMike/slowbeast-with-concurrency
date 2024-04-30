 ; init : store (8b)0:8b to (*)g1
 ; llvm : @c = dso_local global i8 0, align 1, !dbg !0
g1 = global  c of size 1:32b

fun main()
  ; [bblock 4]
   ; llvm :   %1 = alloca i32, align 4
  x5 = alloc 4:32b bytes 
   ; llvm :   store i32 0, i32* %1, align 4
  store (32b)0:32b to (*)x5 
   ; llvm :   ret i32 0, !dbg !21
   ; dbgloc : ('/home/xshandil/ben_shandilya/slowbeast/globchar.c', 4, 5)
  ret (32b)0:32b 

nuf

