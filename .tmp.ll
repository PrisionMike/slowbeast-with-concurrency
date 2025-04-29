; ModuleID = '/workspaces/slowbeast-no-data-race/.file.under.test.i'
source_filename = "/workspaces/slowbeast-no-data-race/.file.under.test.i"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@gint = dso_local global i32 0, align 4, !dbg !0
@gintp = dso_local global i32* null, align 8, !dbg !5

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !18 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  store i32* @gint, i32** @gintp, align 8, !dbg !22
  call void @llvm.dbg.declare(metadata i32* %2, metadata !23, metadata !DIExpression()), !dbg !24
  call void @llvm.dbg.declare(metadata i32* %3, metadata !25, metadata !DIExpression()), !dbg !26
  store i32 7, i32* %2, align 4, !dbg !27
  %4 = load i32, i32* %2, align 4, !dbg !28
  store i32 %4, i32* %3, align 4, !dbg !29
  store i32 9, i32* @gint, align 4, !dbg !30
  %5 = load i32*, i32** @gintp, align 8, !dbg !31
  store i32 10, i32* %5, align 4, !dbg !32
  ret i32 0, !dbg !33
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!10, !11, !12, !13, !14, !15, !16}
!llvm.ident = !{!17}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "gint", scope: !2, file: !7, line: 1, type: !9, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C99, file: !3, producer: "Debian clang version 14.0.6", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, globals: !4, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "/workspaces/slowbeast-no-data-race/.file.under.test.i", directory: "/workspaces/slowbeast-no-data-race", checksumkind: CSK_MD5, checksum: "a02180c2820ea4f6ec296a85562cd357")
!4 = !{!0, !5}
!5 = !DIGlobalVariableExpression(var: !6, expr: !DIExpression())
!6 = distinct !DIGlobalVariable(name: "gintp", scope: !2, file: !7, line: 2, type: !8, isLocal: false, isDefinition: true)
!7 = !DIFile(filename: ".file.under.test.i", directory: "/workspaces/slowbeast-no-data-race", checksumkind: CSK_MD5, checksum: "a02180c2820ea4f6ec296a85562cd357")
!8 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !9, size: 64)
!9 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!10 = !{i32 7, !"Dwarf Version", i32 5}
!11 = !{i32 2, !"Debug Info Version", i32 3}
!12 = !{i32 1, !"wchar_size", i32 4}
!13 = !{i32 7, !"PIC Level", i32 2}
!14 = !{i32 7, !"PIE Level", i32 2}
!15 = !{i32 7, !"uwtable", i32 1}
!16 = !{i32 7, !"frame-pointer", i32 2}
!17 = !{!"Debian clang version 14.0.6"}
!18 = distinct !DISubprogram(name: "main", scope: !7, file: !7, line: 3, type: !19, scopeLine: 3, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !21)
!19 = !DISubroutineType(types: !20)
!20 = !{!9}
!21 = !{}
!22 = !DILocation(line: 4, column: 11, scope: !18)
!23 = !DILocalVariable(name: "i", scope: !18, file: !7, line: 5, type: !9)
!24 = !DILocation(line: 5, column: 9, scope: !18)
!25 = !DILocalVariable(name: "j", scope: !18, file: !7, line: 5, type: !9)
!26 = !DILocation(line: 5, column: 11, scope: !18)
!27 = !DILocation(line: 6, column: 7, scope: !18)
!28 = !DILocation(line: 7, column: 9, scope: !18)
!29 = !DILocation(line: 7, column: 7, scope: !18)
!30 = !DILocation(line: 8, column: 10, scope: !18)
!31 = !DILocation(line: 9, column: 6, scope: !18)
!32 = !DILocation(line: 9, column: 12, scope: !18)
!33 = !DILocation(line: 10, column: 5, scope: !18)
