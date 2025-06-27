import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import computeDominators,buildDomTree,getMyTree,getSuccessors,getPredecessors
from copy import deepcopy
from networkx import dominance_frontiers,DiGraph

def generateFinalOutput(content):    
    convertToListOfStr(content)
    
def convertToListOfStr(content):
    basicBlocks = content["basicBlocks"]
    funcData = content["functionData"]
    
    outputList = generatePrologue(funcData["functionName"])
    
    for blockNum,block in basicBlocks.items():
        for index,instr in enumerate(block):
            if not instr:
                continue
            instrList = generateNewInstructions(instr,funcData["functionName"])
            outputList.extend(instrList)
            
        outputList[-1] = outputList[-1] 
        
    outputList.extend(generateEpilogue(funcData["functionName"]))
    content["finalOutput"] = outputList

def generatePrologue(funcName):
    instrList = []
    
    # .globl	main                            // -- Begin function main
	# .p2align	2
	# .type	main,@function
    #  main:                                   // @main
    # 	.cfi_startproc
    
    instrList.append(f".globl {funcName}\n")
    instrList.append(f".p2align 2\n")
    instrList.append(f".type {funcName}, @function\n")
    instrList.append(f"{funcName}:\n")
    instrList.append(f".cfi_startproc\n")
    
    return instrList

def generateEpilogue(funcName):
    instrList = []
    
    label = generateLabel(funcName,"end")
 
    instrList.append(f"{label}:\n")
    instrList.append(f".size {funcName}, {label}-{funcName}\n")
    instrList.append(f".cfi_endproc\n")
    
    return instrList


def generateStr(instr):
    # f"{oldInstr[0]} {','.join([str(i) for i in oldInstr[1:]])}"
    output = list()

    for i in instr[1:]:
        if type(i) == str:
            output.append(i)
        elif type(i) == list:
            if i[0] == "SP":
                temp = ",".join(i)
                output.append("["+temp+"]")
        else:
            raise Exception(type(i))
    return "\t"+instr[0]+ " " + ",".join(output)

def generateLabel(funcName,label):
    return f".{funcName}_{label}"

def generateNewInstructions(oldInstr,funcName):
    instrList = list()
    if oldInstr[0] == "label":
        instrList.append(f"{generateLabel(funcName,oldInstr[1])}:")
    elif oldInstr[0] == "RET":
        instrList.append(f"\tRET")
    elif oldInstr[0] in ["B","B.NE"]:
        instrList.append(f"{oldInstr[0]} {generateLabel(funcName,oldInstr[1])}")
    else:
        instrList.append(generateStr(oldInstr))
    
    return [i+"\n" for i in instrList]

def convertIRToIR():
    with open("intermediateOutput/ir5Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    finalOutput = dict()
    outputList = list()
    funcList = list()
    
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        generateFinalOutput(content)
        outputList.append(file)
        finalOutput[file] = content["finalOutput"]
        funcList.append(content["functionData"]["functionName"])
    
    funcList.remove("main")
    
    with open("output/finalOutput.s","w") as file:
        file.writelines(generateFilePrologue("input.c"))
        for someFunction in outputList:
            file.writelines(finalOutput[someFunction])
        file.writelines(generateFileEpilogue(funcList))
    
def generateFilePrologue(fileName):
    instrList = []
    
    # 	.file	"input.c"
	# .text

    instrList.append(f".file \"{fileName}\"\n")
    instrList.append(f".text\n")
    
    return instrList
    
def generateFileEpilogue(funcList):
    instrList = []

    # .addrsig
	# .addrsig_sym something1

    instrList.append(".section	\".note.GNU-stack\",\"\",@progbits\n")
    instrList.append(".addrsig\n")
    
    for funcName in funcList:
        instrList.append(f".addrsig_sym {funcName}\n")
    
    return instrList
    
def RunIRPass6():
    convertIRToIR()
    # pass