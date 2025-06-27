
irConvertPass1 takes an ast and converts it into psuedo llvm ir type code.
irConvertPass2 takes the output of irConvertPass1 and constructs cfg out of it


some backup

"""
globalRegisterNumber = 0
sourceFile = "expr.c"
globalAttributeGroupNumber = 0


def preliminaryGeneration(inputFile):
    inputFile.write(f"; ModuleID = '{sourceFile}'" + "\n")
    inputFile.write(
        f'source_filename = "{sourceFile}"' + "\n"
    )  # write the source file name
    inputFile.write(
        'target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"'
        + "\n"
    )  # write the data layout
    # inputFile.write(f"target triple = \"aarch64-unknown-linux-gnu\"" + "\n") # write the target machine data
    inputFile.write(
        f'target triple = "x86_64-unknown-linux-gnu"' + "\n" * 2
    )  # write the target machine data

    # inputFile.write(
    #     '@.str = private unnamed_addr constant [3 x i8] c"%d\\00", align 1\n'
    # )


def postliminaryGeneration(inputFile):
    global globalAttributeGroupNumber
    # inputFile.write("declare i32 @printf(ptr noundef, ...) #1\n")
    inputFile.write(
        "attributes #"
        + str(globalAttributeGroupNumber)
        + ' = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }'
        + "\n"
    )
    # inputFile.write(
    #     'attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }\n'
    # )

    someStr = '!llvm.module.flags = !{!0, !1, !2, !3, !4}\n\
!llvm.ident = !{!5}\n\
\
!0 = !{i32 1, !"wchar_size", i32 4}\n\
!1 = !{i32 8, !"PIC Level", i32 2}\n\
!2 = !{i32 7, !"PIE Level", i32 2}\n\
!3 = !{i32 7, !"uwtable", i32 2}\n\
!4 = !{i32 7, !"frame-pointer", i32 2}\n\
!5 = !{!"clang version 21.0.0git (https://github.com/llvm/llvm-project.git 8616c873350a2fd91c0c8028065daf8026ce515f)"}\n'
    inputFile.write(someStr)
    globalAttributeGroupNumber += 1

def mainGeneration(inputFile):
    with open("intermediateOutput/output.ir1", "r") as jsonFile:
        content = json.load(jsonFile)
        inputFile.write(irTranslationUnit(content)["outputStr"])

def convertIR1ToIR2():
    with open("intermediateOutput/output.ir2", "w") as irFile:
        preliminaryGeneration(irFile)
        mainGeneration(irFile)
        postliminaryGeneration(irFile)
"""

1. dominance - done
2. phi functions - done
6. scope analysis - 
7. optimisations (read ssa and other) 
8. convert 

5. floating point numbers
4. for loops
3. arrays 
. fall through edges while constructing cfg