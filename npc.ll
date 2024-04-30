; ModuleID = '/tmp/notpthread.c.bc'
source_filename = "/home/xshandil/ben_shandilya/slowbeast/notpthread.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @alok(i32* noundef %0) #0 !dbg !10 {
  %2 = alloca i8*, align 8
  %3 = alloca i32*, align 8
  store i32* %0, i32** %3, align 8
  call void @llvm.dbg.declare(metadata i32** %3, metadata !18, metadata !DIExpression()), !dbg !19
  %4 = load i32*, i32** %3, align 8, !dbg !20
  store i32 8, i32* %4, align 4, !dbg !21
  %5 = load i8*, i8** %2, align 8, !dbg !22
  ret i8* %5, !dbg !22
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !23 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  call void @llvm.dbg.declare(metadata i32* %2, metadata !26, metadata !DIExpression()), !dbg !27
  %3 = call i8* @alok(i32* noundef %2), !dbg !28
  ret i32 0, !dbg !29
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "Ubuntu clang version 14.0.0-1ubuntu1.1", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "/home/xshandil/ben_shandilya/slowbeast/notpthread.c", directory: "/home/xshandil/ben_shandilya/slowbeast", checksumkind: CSK_MD5, checksum: "faf46fd87243495ce607a8320db3c79a")
!2 = !{i32 7, !"Dwarf Version", i32 5}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 7, !"PIC Level", i32 2}
!6 = !{i32 7, !"PIE Level", i32 2}
!7 = !{i32 7, !"uwtable", i32 1}
!8 = !{i32 7, !"frame-pointer", i32 2}
!9 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!10 = distinct !DISubprogram(name: "alok", scope: !11, file: !11, line: 2, type: !12, scopeLine: 2, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !17)
!11 = !DIFile(filename: "notpthread.c", directory: "/home/xshandil/ben_shandilya/slowbeast", checksumkind: CSK_MD5, checksum: "faf46fd87243495ce607a8320db3c79a")
!12 = !DISubroutineType(types: !13)
!13 = !{!14, !15}
!14 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!15 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !16, size: 64)
!16 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!17 = !{}
!18 = !DILocalVariable(name: "a", arg: 1, scope: !10, file: !11, line: 2, type: !15)
!19 = !DILocation(line: 2, column: 17, scope: !10)
!20 = !DILocation(line: 3, column: 6, scope: !10)
!21 = !DILocation(line: 3, column: 8, scope: !10)
!22 = !DILocation(line: 4, column: 1, scope: !10)
!23 = distinct !DISubprogram(name: "main", scope: !11, file: !11, line: 6, type: !24, scopeLine: 6, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !17)
!24 = !DISubroutineType(types: !25)
!25 = !{!16}
!26 = !DILocalVariable(name: "b", scope: !23, file: !11, line: 7, type: !16)
!27 = !DILocation(line: 7, column: 9, scope: !23)
!28 = !DILocation(line: 8, column: 5, scope: !23)
!29 = !DILocation(line: 9, column: 5, scope: !23)
