import json
from icecream import ic as print
from optimisations.loopOptimisations.functions import computeNaturalLoops,getNodesinNaturalLoop,getNestedLoops

content = None

def generateFinalOutput(content):
    CFG,dominators,idom = content["CFG"],content["dominators"],content["idom"]
    naturalLoops = computeNaturalLoops(CFG,dominators,idom)
    nestedLoops,toEval = getNestedLoops(naturalLoops)
    inductionVariableData = {"use":dict(),"def":dict(),"invariants":dict(),"cycles":dict()}
    performInductionVariableAnalysis(nestedLoops,toEval,naturalLoops,inductionVariableData)
    
    
def performInductionVariableAnalysis(nestedLoops,toEval,naturalLoops,inductionVariableData):
    dfsOrder = list()
    visited = set()
    stack = toEval
    naturalLoops = {loop["header"]:loop for loop in naturalLoops}
    for topParent in toEval:
        stack = [topParent]
        currentDfsOrder = list()
        while stack:
            el = stack.pop(0)
            if el in visited:
                currentDfsOrder.append(el)
                continue
            currentDfsOrder.insert(0,el)
            visited.add(el)
            stack = list(nestedLoops[el]) + stack

        dfsOrder.append(currentDfsOrder)
    
    for nodeList in dfsOrder:
        for node in nodeList:
            analyseInvariants(content,node,naturalLoops[node],inductionVariableData)
            analyseInductionVariables(node,naturalLoops[node],inductionVariableData,visited)
            findCyclicDefinitions(content,node,naturalLoops[node],inductionVariableData)
    
def findCyclicDefinitions(content,loopHeader,loopData,inductionVariableData):
    phiNodes = content["phiNodes"]
    definitions = inductionVariableData["def"]
    basicBlocks = content["basicBlocks"]
    cycles = []
    
    for var,varData in phiNodes[str(loopHeader)].items():
        outside = varData["input"][0]
        inside = varData["input"][1]
        
        if inside[1] not in loopData["nodes"]:
            outside,inside = inside,outside
        
        variablesToExamine = [(var,inside[0])]
        variablesExamined = set()
        lastExamined = None
        
        while variablesToExamine:
            el = variablesToExamine.pop()
            if el in variablesExamined:
                continue
            
            location = definitions[el]
            if location[1] == "phi":
                if el[0] == var and el[1] == varData["version"]:
                # if el[0] == var:
                    blockNum,index = inductionVariableData['def'][lastExamined]
                    if index == "phi":
                        print(blockNum,index)
                    else:
                        instr = (basicBlocks[blockNum][index])
                        myValue = None
                        
                        if instr.get("left") == var:
                            rightValue = None
                            myValue = (instr["left"],instr["leftVersion"])
                            if instr["rightType"] == "register":
                                rightValue = (instr["right"],"register")
                            elif instr["rightType"] == "identifier":
                                rightValue = ((instr["right"],instr["rightVersion"]),"identifier")
                            elif instr["rightType"] == "constant":
                                rightValue = (instr["right"],"constant")
                            otherValue = rightValue    
                        elif instr.get("right") == var:
                            leftValue = None
                            myValue = (instr["right"],instr["rightVersion"])
                            if instr["leftType"] == "register":
                                leftValue = (instr["left"],"register")
                            elif instr["leftType"] == "identifier":
                                leftValue = ((instr["left"],instr["leftVersion"]),"identifier")
                            elif instr["leftType"] == "constant":
                                leftValue = (instr["left"],"constant")
                            otherValue = leftValue
                        else:
                            raise Exception("Something went wrong")
                        
                        something = ((var,varData["version"]),instr["operator"],otherValue)
                        cycles.append(something)
                    
            else:
                instruction = basicBlocks[location[0]][location[1]]
                variablesToExamine.extend(getElementsFromInstruction(content,instruction))
            
            variablesExamined.add(el)
            lastExamined = el
 
    print(cycles)
    inductionVariableData["cycles"][loopHeader] = cycles
    
def getElementsFromInstruction(content,instruction):
    output = list()
    
    if instruction.get("assignedValueType") == "register":
        output.append(instruction["assignedValue"])
    else:
        if instruction.get("leftType") == "register":
            output.append(instruction["left"])
        elif instruction.get("leftType") == "identifier":
            output.append((instruction["left"],instruction["leftVersion"]))
            
        if instruction.get("rightType") == "register":
            output.append(instruction["right"])
        elif instruction.get("rightType") == "identifier":
            output.append((instruction["right"],instruction["rightVersion"]))
            
    return output
        
# def identifyBasicInductionVariables(content,loopHeader,naturalLoop,inductionVariableData):
#     basicBlocks = content["basicBlocks"]
#     phiNodes = content["phiNodes"]
    
#     if not inductionVariableData["BIV"].get(loopHeader):
#         inductionVariableData["BIV"][loopHeader] = dict()
        
#     for node in naturalLoop["nodes"]:
#         for instr in basicBlocks[str(node)]:
#             getBasicInductionVariableFromInstr(instr,content,loopHeader,inductionVariableData)

#     newBIV = dict()

#     for blockNum,BIV in inductionVariableData["BIV"].items():
#         newBIV[blockNum] = dict()
#         try:
#             for var,version in BIV:
#                 if version in [x for x,y in phiNodes.get(str(blockNum)).get(var)["input"]]:
#                     # print(var,version,phiNodes.get(str(blockNum)).get(var))
#                     pass
#         except:
#             pass
    
    
# def getBasicInductionVariableFromInstr(instr,content,loopHeader,inductionVariableData):
#     basicBlocks = content["basicBlocks"]
    
#     if instr["type"] == "assign" and instr["assignedValueType"] == "register":
#         var = instr["target"]
#         targetVersion = instr["targetVersion"]
        
#         assignBlockNum,assignIndex = inductionVariableData["def"][instr["assignedValue"]]
#         assignedInstr = basicBlocks[assignBlockNum][assignIndex]
        
#         if assignedInstr["left"] == var:
#             otherType = assignedInstr["rightType"]
#             other = assignedInstr["right"]
#             otherVersion = assignedInstr.get("rightVersion")
#             assignedVersion = assignedInstr["leftVersion"]
            
#         elif assignedInstr["right"] == var:
#             otherType = assignedInstr["leftType"]
#             other = assignedInstr["left"]
#             otherVersion = assignedInstr.get("leftVersion")
#             assignedVersion = assignedInstr["rightVersion"]
        
#         if otherType == "constant":
#             inductionVariableData["BIV"][loopHeader][(var,targetVersion)] = {"operator":assignedInstr["operator"],'other':other,"otherType":otherType}
#         elif otherType == "register":
#             if other in inductionVariableData["invariants"][loopHeader]:
#                 inductionVariableData["BIV"][loopHeader][(var,targetVersion)] = {"operator":assignedInstr["operator"],'other':other,"otherType":otherType}
#         elif otherType == "identifier":
#             if (other,assignedVersion) in inductionVariableData["invariants"][loopHeader]:
#                 inductionVariableData["BIV"][loopHeader][(var,targetVersion)] = {"operator":assignedInstr["operator"],'other':other,"otherType":otherType,"otherVersion":otherVersion}
    
def analyseInvariants(content,loopHeader,naturalLoop,inductionVariableData):
    basicBlocks = content["basicBlocks"]
    phiNodes = content["phiNodes"]
    changed = True
    
    if not inductionVariableData["invariants"].get(loopHeader):
        inductionVariableData["invariants"][loopHeader] = set()
    
    while changed:
        changed = False
        for node in naturalLoop["nodes"]:
            if phiNodes.get(str(node)):
                for var,varData in phiNodes[str(node)].items():
                    areAllVersionsInvariant = True
                    for version,block in varData["input"]:
                        if block not in naturalLoop["nodes"]:
                            if (var,version) not in inductionVariableData["invariants"][loopHeader]:
                                inductionVariableData["invariants"][loopHeader].add((var,version))
                                changed = True
                                
                        if (var,version) not in inductionVariableData["invariants"][loopHeader]:
                            areAllVersionsInvariant = False
                            
                    # this idea below is probably wrong
                    if areAllVersionsInvariant:
                        if (var,varData["version"]) not in inductionVariableData["invariants"][loopHeader]:
                            inductionVariableData["invariants"][loopHeader].add((var,varData["version"]))
                            changed = True
            
            for instr in basicBlocks[str(node)]:
                changed = changed or checkInstrInvariant(instr,loopHeader,inductionVariableData)
    
def checkInstrInvariant(instr,loopHeader,inductionVariableData):
    changed = False
    operationsToCheck = {"add"}
    
    if instr["type"] == "assign":
        if instr["assignedValueType"] == "constant":
            if (instr["target"],instr["targetVersion"]) not in inductionVariableData["invariants"][loopHeader]:
                inductionVariableData["invariants"][loopHeader].add((instr["target"],instr["targetVersion"]))
                changed = True
        if instr["assignedValueType"] == "register" and instr["assignedValue"] in inductionVariableData["invariants"][loopHeader]:
            if (instr["target"],instr["targetVersion"]) not in inductionVariableData["invariants"][loopHeader]:
                inductionVariableData["invariants"][loopHeader].add((instr["target"],instr["targetVersion"]))
                changed = True
                
    if instr["type"] in operationsToCheck:
        left,leftType,right,rightType = instr["left"],instr["leftType"],instr["right"],instr["rightType"]
        leftVersion,rightVersion = instr.get("leftVersion"),instr.get("rightVersion")
        isLeftInvariant,isRightInvariant = False,False
        
        if leftType == "register":
            if left in inductionVariableData["invariants"][loopHeader]:
                isLeftInvariant = True
        elif leftType == "identifier":
            if (left,leftVersion) in inductionVariableData["invariants"][loopHeader]:
                isLeftInvariant = True
        elif leftType == "constant":
            isLeftInvariant = True

        if rightType == "register":
            if right in inductionVariableData["invariants"][loopHeader]:
                isRightInvariant = True
        elif rightType == "identifier":
            if (right,rightVersion) in inductionVariableData["invariants"][loopHeader]:
                isRightInvariant = True
        elif rightType == "constant":
            isRightInvariant = True
        
        if isLeftInvariant and isRightInvariant and instr["result"] not in inductionVariableData["invariants"][loopHeader]:
            changed = True
            inductionVariableData["invariants"][loopHeader].add(instr["result"])
    
    return changed

def analyseInductionVariables(loopHeader,naturalLoop,inductionVariableData,visited):
    analyseBasicBlock(content,loopHeader,naturalLoop,inductionVariableData)
    
    for node in naturalLoop["nodes"]:
        if node in visited:
            continue
        analyseBasicBlock(content,node,naturalLoop,inductionVariableData)
        visited.add(node)

def analyseBasicBlock(content,node,naturalLoop,inductionVariableData):    
    phiNodes = content["phiNodes"].get(str(node))
    if phiNodes:
        for var,data in phiNodes.items():
            outsideBlocks = [i for j,i in data["input"] if int(i) not in naturalLoop["nodes"]]
            loopBlocks = [i for j,i in data["input"] if int(i) in naturalLoop["nodes"]]
            # inductionVariableData["def"][(var,data["version"])] = data
            inductionVariableData["def"][(var,data["version"])] = (str(node),"phi")
        
    basicBlock = content["basicBlocks"][str(node)]
    
    for index,instr in enumerate(basicBlock):
        collectInstructionData(instr,index,str(node),inductionVariableData)
        
def collectInstructionData(instr,index,blockNum,inductionVariableData):
    if instr["type"] == "assign":
        if instr["targetType"] == "identifier":
            inductionVariableData["def"][(instr["target"],instr["targetVersion"])] = (blockNum,index)
        elif instr["targetType"] == "register":
            inductionVariableData["def"][instr["target"]] = (blockNum,index)
    if instr["type"] == "add":
        if instr["leftType"] == "identifier":
            ident = instr["left"]
            version = instr["leftVersion"]
            other = instr["right"]
            otherType = instr["rightType"]
            otherVersion = instr.get("rightVersion")
        elif instr["rightType"] == "identifier":
            ident = instr["right"]
            version = instr["rightVersion"]
            other = instr["left"]
            otherType = instr["leftType"]
            otherVersion = instr.get("leftVersion")
        operator = instr["operator"]
        
        if not inductionVariableData["use"].get((ident,version)):
            inductionVariableData["use"][(ident,version)] = list()
        inductionVariableData["use"][(ident,version)].append((blockNum,index))
        
        if instr["resultType"] == "identifier":
            inductionVariableData["def"][(instr["result"],instr["resultVersion"])] = (blockNum,index)
        elif instr["resultType"] == "register":
            inductionVariableData["def"][instr["result"]] = (blockNum,index)
        
def convertIRToIR():
    global content
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        generateFinalOutput(content)
        
        with open(file,"w") as jsonFile:            
            json.dump(content,jsonFile)        


def runInductionVariableAnalysis():
    global hasOptimised
    
    hasOptimised = False
    convertIRToIR()
    return hasOptimised