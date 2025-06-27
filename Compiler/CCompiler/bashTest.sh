
gcc -fsyntax-only input/input.c > validC.txt
echo "$(cat validC.txt)"

clang -S -O0 -Xclang -disable-O0-optnone -emit-llvm input/input.c -o intermediateOutput/exprNonSSA.ll
#clang -S -O1 -emit-llvm input/expr.c -o intermediateOutput/expr1.ll
#clang -S -O2 -emit-llvm input/expr.c -o intermediateOutput/expr2.ll
#clang -S -O3 -emit-llvm input/expr.c -o intermediateOutput/expr3.ll

opt -passes=mem2reg -S intermediateOutput/exprNonSSA.ll -o intermediateOutput/expr.ll

# opt -dot-regions -disable-output intermediateOutput/expr.ll
# opt -passes="dot-dom" -disable-output intermediateOutput/expr.ll -S
# opt -passes="dot-cfg" -disable-output intermediateOutput/expr.ll -S
# opt -passes='print<domfrontier>' intermediateOutput/expr.ll -disable-output
# opt -passes='print<domtree>' intermediateOutput/expr.ll -disable-output
# dot -Tpng dom.main.dot -o dom.main.png
# dot -Tpng .main.dot -o .main.png

# mv reg.* other
# ls other | grep .dot$ | awk "{print \"dot -Tpng other/\"\$0\" -o other/\"\$0\".png\"}" | xargs -l | bash

# clang -S -O0 --target=aarch64-linux-gnu input/input.c -o intermediateOutput/llvmOutput.s
# clang --target=aarch64-linux-gnu -c intermediateOutput/llvmOutput.s -o intermediateOutput/llvmOutput.o
# clang --target=aarch64-linux-gnu intermediateOutput/llvmOutput.o -o output/llvmOutput
# qemu-aarch64 ./output/llvmOutput
# echo $?
# echo "Correct Output ^"

# python3 main.py
# clang --target=aarch64-linux-gnu -c output/finalOutput.s -o output/finalOutput.o
# clang --target=aarch64-linux-gnu output/finalOutput.o -o output/finalOutput
# echo "Compilation Done"
# qemu-aarch64 ./output/finalOutput
# echo $?
# echo "My Output ^"

python3 pythonTest.py

# llc -filetype=obj intermediateOutput/expr.ll -o intermediateOutput/output.o

# clang input/expr.c -o intermediateOutput/expr.out
# intermediateOutput/expr.out
#echo $?
# clang -g intermediateOutput/output.o -o executable
# ./executable
# echo $?
