; ModuleID = '/tmp/bigshot_s.c.bc'
source_filename = "/home/xshandil/ben_shandilya/slowbeast/bigshot_s.c"
target datalayout = "e-m:e-p:32:32-p270:32:32-p271:32:32-p272:64:64-f64:32:64-f80:32-n8:16:32-S128"
target triple = "i386-pc-linux-gnu"

%union.pthread_attr_t = type { i32, [32 x i8] }

@.str = private unnamed_addr constant [2 x i8] c"0\00", align 1
@.str.1 = private unnamed_addr constant [51 x i8] c"/home/xshandil/ben_shandilya/slowbeast/bigshot_s.c\00", align 1
@__PRETTY_FUNCTION__.reach_error = private unnamed_addr constant [19 x i8] c"void reach_error()\00", align 1
@v = dso_local global i8* null, align 4, !dbg !0
@.str.2 = private unnamed_addr constant [8 x i8] c"Bigshot\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @reach_error() #0 !dbg !17 {
  call void @__assert_fail(i8* noundef getelementptr inbounds ([2 x i8], [2 x i8]* @.str, i32 0, i32 0), i8* noundef getelementptr inbounds ([51 x i8], [51 x i8]* @.str.1, i32 0, i32 0), i32 noundef 11, i8* noundef getelementptr inbounds ([19 x i8], [19 x i8]* @__PRETTY_FUNCTION__.reach_error, i32 0, i32 0)) #5, !dbg !21
  unreachable, !dbg !21
}

; Function Attrs: noreturn nounwind
declare void @__assert_fail(i8* noundef, i8* noundef, i32 noundef, i8* noundef) #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @__VERIFIER_assert(i32 noundef %0) #0 !dbg !24 {
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  call void @llvm.dbg.declare(metadata i32* %2, metadata !28, metadata !DIExpression()), !dbg !29
  %3 = load i32, i32* %2, align 4, !dbg !30
  %4 = icmp ne i32 %3, 0, !dbg !30
  br i1 %4, label %7, label %5, !dbg !32

5:                                                ; preds = %1
  br label %6, !dbg !33

6:                                                ; preds = %5
  call void @llvm.dbg.label(metadata !34), !dbg !36
  call void @reach_error(), !dbg !37
  call void @abort() #5, !dbg !39
  unreachable, !dbg !39

7:                                                ; preds = %1
  ret void, !dbg !40
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #2

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.label(metadata) #2

; Function Attrs: noreturn nounwind
declare void @abort() #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @_strcpy(i8* noundef %0, i8* noundef %1) #0 !dbg !41 {
  %3 = alloca i8*, align 4
  %4 = alloca i8*, align 4
  %5 = alloca i8*, align 4
  store i8* %0, i8** %3, align 4
  call void @llvm.dbg.declare(metadata i8** %3, metadata !46, metadata !DIExpression()), !dbg !47
  store i8* %1, i8** %4, align 4
  call void @llvm.dbg.declare(metadata i8** %4, metadata !48, metadata !DIExpression()), !dbg !49
  call void @llvm.dbg.declare(metadata i8** %5, metadata !50, metadata !DIExpression()), !dbg !51
  %6 = load i8*, i8** %3, align 4, !dbg !52
  store i8* %6, i8** %5, align 4, !dbg !51
  br label %7, !dbg !53

7:                                                ; preds = %14, %2
  %8 = load i8*, i8** %4, align 4, !dbg !54
  %9 = getelementptr inbounds i8, i8* %8, i32 1, !dbg !54
  store i8* %9, i8** %4, align 4, !dbg !54
  %10 = load i8, i8* %8, align 1, !dbg !55
  %11 = load i8*, i8** %3, align 4, !dbg !56
  %12 = getelementptr inbounds i8, i8* %11, i32 1, !dbg !56
  store i8* %12, i8** %3, align 4, !dbg !56
  store i8 %10, i8* %11, align 1, !dbg !57
  %13 = icmp ne i8 %10, 0, !dbg !53
  br i1 %13, label %14, label %15, !dbg !53

14:                                               ; preds = %7
  br label %7, !dbg !53, !llvm.loop !58

15:                                               ; preds = %7
  %16 = load i8*, i8** %5, align 4, !dbg !61
  ret i8* %16, !dbg !62
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @thread1(i8* noundef %0) #0 !dbg !63 {
  %2 = alloca i8*, align 4
  store i8* %0, i8** %2, align 4
  call void @llvm.dbg.declare(metadata i8** %2, metadata !67, metadata !DIExpression()), !dbg !68
  %3 = call noalias i8* @malloc(i32 noundef 8) #6, !dbg !69
  store i8* %3, i8** @v, align 4, !dbg !70
  ret i8* null, !dbg !71
}

; Function Attrs: nounwind
declare noalias i8* @malloc(i32 noundef) #3

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @thread2(i8* noundef %0) #0 !dbg !72 {
  %2 = alloca i8*, align 4
  store i8* %0, i8** %2, align 4
  call void @llvm.dbg.declare(metadata i8** %2, metadata !73, metadata !DIExpression()), !dbg !74
  %3 = load i8*, i8** @v, align 4, !dbg !75
  %4 = icmp ne i8* %3, null, !dbg !75
  br i1 %4, label %5, label %8, !dbg !77

5:                                                ; preds = %1
  %6 = load i8*, i8** @v, align 4, !dbg !78
  %7 = call i8* @_strcpy(i8* noundef %6, i8* noundef getelementptr inbounds ([8 x i8], [8 x i8]* @.str.2, i32 0, i32 0)), !dbg !79
  br label %8, !dbg !79

8:                                                ; preds = %5, %1
  ret i8* null, !dbg !80
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !81 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  call void @llvm.dbg.declare(metadata i32* %2, metadata !84, metadata !DIExpression()), !dbg !88
  call void @llvm.dbg.declare(metadata i32* %3, metadata !89, metadata !DIExpression()), !dbg !90
  %4 = call i32 @pthread_create(i32* noundef %2, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread1, i8* noundef null) #6, !dbg !91
  %5 = load i32, i32* %2, align 4, !dbg !92
  %6 = call i32 @pthread_join(i32 noundef %5, i8** noundef null), !dbg !93
  %7 = call i32 @pthread_create(i32* noundef %3, %union.pthread_attr_t* noundef null, i8* (i8*)* noundef @thread2, i8* noundef null) #6, !dbg !94
  %8 = load i32, i32* %3, align 4, !dbg !95
  %9 = call i32 @pthread_join(i32 noundef %8, i8** noundef null), !dbg !96
  %10 = load i8*, i8** @v, align 4, !dbg !97
  %11 = icmp ne i8* %10, null, !dbg !97
  br i1 %11, label %12, label %18, !dbg !98

12:                                               ; preds = %0
  %13 = load i8*, i8** @v, align 4, !dbg !99
  %14 = getelementptr inbounds i8, i8* %13, i32 0, !dbg !99
  %15 = load i8, i8* %14, align 1, !dbg !99
  %16 = sext i8 %15 to i32, !dbg !99
  %17 = icmp eq i32 %16, 66, !dbg !100
  br label %18, !dbg !98

18:                                               ; preds = %12, %0
  %19 = phi i1 [ true, %0 ], [ %17, %12 ]
  %20 = zext i1 %19 to i32, !dbg !98
  call void @__VERIFIER_assert(i32 noundef %20), !dbg !101
  ret i32 0, !dbg !102
}

; Function Attrs: nounwind
declare i32 @pthread_create(i32* noundef, %union.pthread_attr_t* noundef, i8* (i8*)* noundef, i8* noundef) #3

declare i32 @pthread_join(i32 noundef, i8** noundef) #4

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="i686" "target-features"="+cx8,+x87" "tune-cpu"="generic" }
attributes #1 = { noreturn nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="i686" "target-features"="+cx8,+x87" "tune-cpu"="generic" }
attributes #2 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #3 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="i686" "target-features"="+cx8,+x87" "tune-cpu"="generic" }
attributes #4 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="i686" "target-features"="+cx8,+x87" "tune-cpu"="generic" }
attributes #5 = { noreturn nounwind }
attributes #6 = { nounwind }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!8, !9, !10, !11, !12, !13, !14, !15}
!llvm.ident = !{!16}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "v", scope: !2, file: !5, line: 24, type: !6, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C99, file: !3, producer: "Ubuntu clang version 14.0.0-1ubuntu1.1", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, globals: !4, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "/home/xshandil/ben_shandilya/slowbeast/bigshot_s.c", directory: "/home/xshandil/ben_shandilya/slowbeast", checksumkind: CSK_MD5, checksum: "032a765df9f7312ce5d8eb16f0064079")
!4 = !{!0}
!5 = !DIFile(filename: "bigshot_s.c", directory: "/home/xshandil/ben_shandilya/slowbeast", checksumkind: CSK_MD5, checksum: "032a765df9f7312ce5d8eb16f0064079")
!6 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !7, size: 32)
!7 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!8 = !{i32 1, !"NumRegisterParameters", i32 0}
!9 = !{i32 7, !"Dwarf Version", i32 5}
!10 = !{i32 2, !"Debug Info Version", i32 3}
!11 = !{i32 1, !"wchar_size", i32 4}
!12 = !{i32 7, !"PIC Level", i32 2}
!13 = !{i32 7, !"PIE Level", i32 2}
!14 = !{i32 7, !"uwtable", i32 1}
!15 = !{i32 7, !"frame-pointer", i32 2}
!16 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!17 = distinct !DISubprogram(name: "reach_error", scope: !5, file: !5, line: 11, type: !18, scopeLine: 11, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !20)
!18 = !DISubroutineType(types: !19)
!19 = !{null}
!20 = !{}
!21 = !DILocation(line: 11, column: 22, scope: !22)
!22 = distinct !DILexicalBlock(scope: !23, file: !5, line: 11, column: 22)
!23 = distinct !DILexicalBlock(scope: !17, file: !5, line: 11, column: 22)
!24 = distinct !DISubprogram(name: "__VERIFIER_assert", scope: !5, file: !5, line: 16, type: !25, scopeLine: 16, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !20)
!25 = !DISubroutineType(types: !26)
!26 = !{null, !27}
!27 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!28 = !DILocalVariable(name: "expression", arg: 1, scope: !24, file: !5, line: 16, type: !27)
!29 = !DILocation(line: 16, column: 28, scope: !24)
!30 = !DILocation(line: 16, column: 47, scope: !31)
!31 = distinct !DILexicalBlock(scope: !24, file: !5, line: 16, column: 46)
!32 = !DILocation(line: 16, column: 46, scope: !24)
!33 = !DILocation(line: 16, column: 59, scope: !31)
!34 = !DILabel(scope: !35, name: "ERROR", file: !5, line: 16)
!35 = distinct !DILexicalBlock(scope: !31, file: !5, line: 16, column: 59)
!36 = !DILocation(line: 16, column: 61, scope: !35)
!37 = !DILocation(line: 16, column: 69, scope: !38)
!38 = distinct !DILexicalBlock(scope: !35, file: !5, line: 16, column: 68)
!39 = !DILocation(line: 16, column: 83, scope: !38)
!40 = !DILocation(line: 16, column: 95, scope: !24)
!41 = distinct !DISubprogram(name: "_strcpy", scope: !5, file: !5, line: 18, type: !42, scopeLine: 18, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !20)
!42 = !DISubroutineType(types: !43)
!43 = !{!6, !6, !44}
!44 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !45, size: 32)
!45 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !7)
!46 = !DILocalVariable(name: "dest", arg: 1, scope: !41, file: !5, line: 18, type: !6)
!47 = !DILocation(line: 18, column: 21, scope: !41)
!48 = !DILocalVariable(name: "src", arg: 2, scope: !41, file: !5, line: 18, type: !44)
!49 = !DILocation(line: 18, column: 39, scope: !41)
!50 = !DILocalVariable(name: "save", scope: !41, file: !5, line: 19, type: !6)
!51 = !DILocation(line: 19, column: 11, scope: !41)
!52 = !DILocation(line: 19, column: 18, scope: !41)
!53 = !DILocation(line: 20, column: 5, scope: !41)
!54 = !DILocation(line: 20, column: 27, scope: !41)
!55 = !DILocation(line: 20, column: 23, scope: !41)
!56 = !DILocation(line: 20, column: 18, scope: !41)
!57 = !DILocation(line: 20, column: 21, scope: !41)
!58 = distinct !{!58, !53, !59, !60}
!59 = !DILocation(line: 20, column: 31, scope: !41)
!60 = !{!"llvm.loop.mustprogress"}
!61 = !DILocation(line: 21, column: 12, scope: !41)
!62 = !DILocation(line: 21, column: 5, scope: !41)
!63 = distinct !DISubprogram(name: "thread1", scope: !5, file: !5, line: 26, type: !64, scopeLine: 27, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !20)
!64 = !DISubroutineType(types: !65)
!65 = !{!66, !66}
!66 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 32)
!67 = !DILocalVariable(name: "arg", arg: 1, scope: !63, file: !5, line: 26, type: !66)
!68 = !DILocation(line: 26, column: 22, scope: !63)
!69 = !DILocation(line: 28, column: 7, scope: !63)
!70 = !DILocation(line: 28, column: 5, scope: !63)
!71 = !DILocation(line: 29, column: 3, scope: !63)
!72 = distinct !DISubprogram(name: "thread2", scope: !5, file: !5, line: 32, type: !64, scopeLine: 33, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !20)
!73 = !DILocalVariable(name: "arg", arg: 1, scope: !72, file: !5, line: 32, type: !66)
!74 = !DILocation(line: 32, column: 21, scope: !72)
!75 = !DILocation(line: 34, column: 7, scope: !76)
!76 = distinct !DILexicalBlock(scope: !72, file: !5, line: 34, column: 7)
!77 = !DILocation(line: 34, column: 7, scope: !72)
!78 = !DILocation(line: 34, column: 18, scope: !76)
!79 = !DILocation(line: 34, column: 10, scope: !76)
!80 = !DILocation(line: 35, column: 3, scope: !72)
!81 = distinct !DISubprogram(name: "main", scope: !5, file: !5, line: 39, type: !82, scopeLine: 40, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !20)
!82 = !DISubroutineType(types: !83)
!83 = !{!27}
!84 = !DILocalVariable(name: "t1", scope: !81, file: !5, line: 41, type: !85)
!85 = !DIDerivedType(tag: DW_TAG_typedef, name: "pthread_t", file: !86, line: 27, baseType: !87)
!86 = !DIFile(filename: "/usr/include/bits/pthreadtypes.h", directory: "", checksumkind: CSK_MD5, checksum: "735e3bf264ff9d8f5d95898b1692fbdb")
!87 = !DIBasicType(name: "unsigned long", size: 32, encoding: DW_ATE_unsigned)
!88 = !DILocation(line: 41, column: 13, scope: !81)
!89 = !DILocalVariable(name: "t2", scope: !81, file: !5, line: 41, type: !85)
!90 = !DILocation(line: 41, column: 17, scope: !81)
!91 = !DILocation(line: 43, column: 3, scope: !81)
!92 = !DILocation(line: 44, column: 16, scope: !81)
!93 = !DILocation(line: 44, column: 3, scope: !81)
!94 = !DILocation(line: 46, column: 3, scope: !81)
!95 = !DILocation(line: 47, column: 16, scope: !81)
!96 = !DILocation(line: 47, column: 3, scope: !81)
!97 = !DILocation(line: 49, column: 22, scope: !81)
!98 = !DILocation(line: 49, column: 24, scope: !81)
!99 = !DILocation(line: 49, column: 27, scope: !81)
!100 = !DILocation(line: 49, column: 32, scope: !81)
!101 = !DILocation(line: 49, column: 3, scope: !81)
!102 = !DILocation(line: 51, column: 3, scope: !81)
