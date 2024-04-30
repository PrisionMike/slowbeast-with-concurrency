; ModuleID = '/tmp/pthread-create.c.bc'
source_filename = "/home/xshandil/ben_shandilya/slowbeast/pthread-create.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%union.pthread_attr_t = type { i64, [48 x i8] }

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @thread1() #0 !dbg !10 {
  ret i8* null, !dbg !16
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !17 {
  %1 = alloca i32, align 4
  %2 = alloca i64, align 8
  store i32 0, i32* %1, align 4
  call void @llvm.dbg.declare(metadata i64* %2, metadata !21, metadata !DIExpression()), !dbg !25
  %3 = call i32 @pthread_create(i64* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef bitcast (i8* ()* @thread1 to i8* (i8*)*), i8* noundef null) #4, !dbg !26
  %4 = load i64, i64* %2, align 8, !dbg !27
  %5 = call i32 @pthread_join(i64 noundef %4, i8** noundef null), !dbg !28
  ret i32 0, !dbg !29
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: nounwind
declare i32 @pthread_create(i64* noundef, %union.pthread_attr_t* noundef, i8* (i8*)* noundef, i8* noundef) #2

declare i32 @pthread_join(i64 noundef, i8** noundef) #3

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "Ubuntu clang version 14.0.0-1ubuntu1.1", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "/home/xshandil/ben_shandilya/slowbeast/pthread-create.c", directory: "/home/xshandil/ben_shandilya/slowbeast", checksumkind: CSK_MD5, checksum: "1a240b0dd6c84df72b2a3a3daa336cda")
!2 = !{i32 7, !"Dwarf Version", i32 5}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 7, !"PIC Level", i32 2}
!6 = !{i32 7, !"PIE Level", i32 2}
!7 = !{i32 7, !"uwtable", i32 1}
!8 = !{i32 7, !"frame-pointer", i32 2}
!9 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!10 = distinct !DISubprogram(name: "thread1", scope: !11, file: !11, line: 3, type: !12, scopeLine: 3, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !15)
!11 = !DIFile(filename: "pthread-create.c", directory: "/home/xshandil/ben_shandilya/slowbeast", checksumkind: CSK_MD5, checksum: "1a240b0dd6c84df72b2a3a3daa336cda")
!12 = !DISubroutineType(types: !13)
!13 = !{!14}
!14 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!15 = !{}
!16 = !DILocation(line: 4, column: 5, scope: !10)
!17 = distinct !DISubprogram(name: "main", scope: !11, file: !11, line: 7, type: !18, scopeLine: 7, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !15)
!18 = !DISubroutineType(types: !19)
!19 = !{!20}
!20 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!21 = !DILocalVariable(name: "t1", scope: !17, file: !11, line: 8, type: !22)
!22 = !DIDerivedType(tag: DW_TAG_typedef, name: "pthread_t", file: !23, line: 27, baseType: !24)
!23 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/pthreadtypes.h", directory: "", checksumkind: CSK_MD5, checksum: "735e3bf264ff9d8f5d95898b1692fbdb")
!24 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!25 = !DILocation(line: 8, column: 15, scope: !17)
!26 = !DILocation(line: 9, column: 5, scope: !17)
!27 = !DILocation(line: 10, column: 18, scope: !17)
!28 = !DILocation(line: 10, column: 5, scope: !17)
!29 = !DILocation(line: 11, column: 5, scope: !17)
