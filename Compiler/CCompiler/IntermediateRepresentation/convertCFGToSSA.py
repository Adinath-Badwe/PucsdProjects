import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import computeDominators,buildDomTree,getMyTree,getSuccessors
from copy import deepcopy
from networkx import dominance_frontiers,DiGraph

def generateFinalOutput(content):    
    someDataStructure = getVariableBlockNumbers(content)
    content["phiNodes"] = dict()
    
    # place phi nodes at the start of respective basic blocks
    for variable,someData in someDataStructure.items():
        placePhiNodeForVariable(variable,someData,content)
        
    # perform variable versioning/renaming
    
    performVariableRenaming(content,list(someDataStructure.keys()))
    
    return content

def performVariableRenaming(content,varList):
    basicBlocks = content["basicBlocks"]
    CFG = content["CFG"]
    dominanceFrontiers = content["dominanceFrontiers"]
    
    domtree,idom = buildDomTree(computeDominators(CFG,0),0)
    content["domtree"] = domtree
    content["idom"] = idom
    content["dominators"] = {x:list(y) for x,y in computeDominators(CFG,0).items()}
    
    vMap = {var:0 for var in varList}
    visited = set()    
    
    
    
    renameVariables1(content,vMap)
    
    return content

def renameVariables1(content,vMap):
    stack = {var:[0] for var in vMap}
    currentAssignments = {var:0 for var in vMap}
    
    performVarRenameOnParam(content,vMap,stack,currentAssignments)
    dfsRename(content,0,vMap,stack)
    
    for var,assignment in currentAssignments.items():
        for _ in range(assignment):
            stack[var].pop()
    

def performVarRenameOnParam(content,vMap,stack,currentAssignments):
    parameterList = content["functionData"].get("parameterList")
    
    if not parameterList:
        return 
    
    for parameter in parameterList:
        identifier = parameter["value"][0]["value"]
        vMap[identifier] += 1
        currentAssignments[identifier] += 1
        parameter["value"][0]["version"] = vMap[identifier]
        stack[identifier].append(vMap[identifier])
        

def dfsRename(content,node,vMap,stack):
    currentAssignments = {var:0 for var in vMap}
    CFG = content["CFG"]
    phiNodes = content["phiNodes"]
    domTree = content["domtree"]
    basicBlocks = content["basicBlocks"]

    if phiNodes.get(str(node)):
        for var,varData in phiNodes[str(node)].items():
            vMap[var] += 1
            currentAssignments[var] += 1
            varData["version"] = vMap[var]
            stack[var].append(vMap[var])
    
    for index,instr in enumerate(basicBlocks[str(node)]):
        evaluateInstr(instr,vMap,stack,currentAssignments)
    
    for succ in getSuccessors(node,CFG):
        if phiNodes.get(str(succ)):
            for var,varData in phiNodes[str(succ)].items():
                varData["input"].append((stack[var][-1],node))
    
    content["basicBlocks"] = basicBlocks
    content["phiNodes"] = phiNodes
    
    for child in domTree[node]:
        dfsRename(content,child,vMap,stack)
    
    for var,assignment in currentAssignments.items():
        for _ in range(assignment):
            stack[var].pop()
    
def evaluateInstr(instr,vMap,stack,currentAssignments):
    if instr.get("leftType") == "identifier":
        instr["leftVersion"] = stack[instr["left"]][-1]
    if instr.get("rightType") == "identifier":
        instr["rightVersion"] = stack[instr["right"]][-1]
    if instr.get("assignedValueType") == "identifier":
        instr["assignedValueVersion"] = stack[instr["assignedValue"]][-1]
    if instr.get("targetType") == "identifier":
        vMap[instr["target"]] += 1
        currentAssignments[instr["target"]] += 1
        instr["targetVersion"] = vMap[instr["target"]]
        stack[instr["target"]].append(vMap[instr["target"]])
    if instr["type"] == "return" and instr["valueType"] == "identifier":
        instr["valueVersion"] = stack[instr["value"]][-1]
    if instr["type"] == "postfix" and instr["use"] == "funcCall" and instr.get("argumentList"):
        for argument in instr["argumentList"]:
            if argument["resultType"] == "identifier":
                argument["resultVersion"] = stack[argument["result"]][-1]
    return instr,vMap



# def renameVariables(content,vMap):
#     phiNodes = content["phiNodes"]
    
#     renameVarDFS(content,0,vMap)
        
# def renameVarDFS(content,node,vMap):
#     domTree = content["domtree"]
#     phiNodes = content["phiNodes"]
    
#     if phiNodes.get(str(node)):
#         renamePhiNodes(phiNodes[str(node)],vMap)
        
#     renameVars(content,node,vMap)
#     renamePhiNodesSuccessors(content,node,vMap)
    
#     content["phiNodes"] = phiNodes
    
#     if domTree.get(node):
#         for child in domTree[node]:
#             renameVarDFS(content,child,deepcopy(vMap))
    
            
# def renamePhiNodesSuccessors(content,node,vMap):
#     phiNodes = content["phiNodes"]
#     CFG = content["CFG"]
#     for succ in getSuccessors(node,CFG):
#         succ = str(succ)
#         if phiNodes.get(succ):
#             for var,varData in phiNodes[succ].items():
#                 phiNodes[succ][var]['input'].append((vMap[var],node))
#                 # phiNodes[succ][var]['input'].append((phiNodes[str(node)][var]["version"],node))
                
#     content["phiNodes"] = phiNodes
    
# def renamePhiNodes(phiNodes,vMap):
#     for var,VarData in phiNodes.items():
#         vMap[var] += 1
#         phiNodes[var]["version"] = vMap[var]

# def dfsRenameVar(content,start,vMap,visited):
#     CFG = content["CFG"]
#     phiNodes = content["phiNodes"]
    
#     if phiNodes.get(str(start)):        
#         current = phiNodes.get(str(start))
#         for var in current:
#             vMap[var] += 1
#             phiNodes[str(start)][var]["version"] = vMap[var]

#     content,vMap = renameVars(content,start,vMap)
#     visited.add(start)

#     for succ in sorted(getSuccessors(start,CFG)):
        
#         if phiNodes and phiNodes.get(str(succ)):
#             variables = phiNodes.get(str(succ))
#             for var in variables:
#                 phiNodes[str(succ)][var]["input"].append((vMap[var],start))
            
#         if succ not in visited:
#             content,visited = dfsRenameVar(content,succ,deepcopy(vMap),visited)
    
#     # print(phiNodes)
#     return content,visited

# def dfsRenameVar(content,start,vMap,visited):

#     CFG = content["CFG"]
    
#     content,vMap = renameVars(content,start,vMap)
#     visited.add(start)
#     phiNodes = content["phiNodes"]
    
#     if phiNodes.get(str(start)):
        
#         current = phiNodes.get(str(start))
#         for var in current:
#             vMap[var] += 1
#             phiNodes[str(start)][var]["version"] = vMap[var]
    
#     for succ in sorted(getSuccessors(start,CFG)):
#         if phiNodes and phiNodes.get(str(succ)):
#             variables = phiNodes.get(str(succ))
#             for var in variables:
#                 phiNodes[str(succ)][var]["input"].append((vMap[var],start))
#         if succ not in visited:
#             content,visited = dfsRenameVar(content,succ,vMap,visited)
            
#     return content,visited
    

# def performVariableRenaming(content,varList):
#     basicBlocks = content["basicBlocks"]
#     CFG = content["CFG"]
#     dominanceFrontiers = content["dominanceFrontiers"]
    
#     domtree,idom = buildDomTree(computeDominators(CFG,0),0)
#     myTree = getMyTree(idom)
#     dfsOrder = getDFSFromMyTree(myTree)
#     vMap = {var:0 for var in varList}
#     visited = set()
    
#     for blockNum in dfsOrder:
#         content,vMap = renameVars(content,blockNum,vMap)
#         content,vMap,visited = renamePhiNodesSuccessors1(content,blockNum,vMap,visited)
        
    
#     content["basicBlocks"] = basicBlocks
#     return content

# def renamePhiNodesSuccessors1(content,blockNum,vMap,visited):
#     basicBlocks = content["basicBlocks"]
#     for succ in getSuccessors(blockNum,content["CFG"]):
#         # if succ in visited:
#         #     continue
#         # visited.add(succ)
#         succBlock = basicBlocks[str(succ)]
#         for i in range(len(succBlock)):
#             if i == 0:
#                 continue
#             if succBlock[i]["type"] != "phi":
#                 break
            
#             succBlock[i]["input"].add(vMap[succBlock[i]["target"]])
#             # vMap[succBlock[i]["target"]] += 1
#             # succBlock[i]["version"] = vMap[succBlock[i]["target"]]
            
#     return content,vMap,visited

# def renameVars(content,blockNum,vMap):
#     basicBlocks = content["basicBlocks"]
#     # instructionAssignments = {var:0 for var in vMap}
    
#     for index,instr in enumerate(basicBlocks[str(blockNum)]):
#         instr,vMap = renameVarsModifyInstr(instr,vMap)
#         basicBlocks[str(blockNum)][index] = instr
#     # content["basicBlocks"] = basicBlocks

# def renameVarsModifyInstr(instr,vMap):
#     if instr.get("leftType") == "identifier":
#         instr["leftVersion"] = vMap[instr["left"]]
#     if instr.get("rightType") == "identifier":
#         instr["rightVersion"] = vMap[instr["right"]]
#     if instr.get("targetType") == "identifier":
#         vMap[instr["target"]] += 1
#         instr["targetVersion"] = vMap[instr["target"]]
#     return instr,vMap
    
def getVariableBlockNumbers(content):
    basicBlocks = content["basicBlocks"]
    functionData = content["functionData"]
    
    someDataStructure = dict()
    
    if functionData.get("parameterList"):
        parameterList = functionData["parameterList"]
        for parameter in parameterList:
            someDataStructure[parameter["value"][0]["value"]] = {'0'}
    
    for blockNumber,block in basicBlocks.items():
        for instr in block:
            varList = getVariableFromInstr(instr)
            while varList:
                var = varList.pop()
                if not someDataStructure.get(var):
                    someDataStructure[var] = set()
                someDataStructure[var].add(blockNumber)
                
    return someDataStructure
            
def getVariableFromInstr(instr):
    variableList = set()
    # if "identifier" == instr.get("leftType"):
    #     variableList.add(instr["left"])
    # if "identifier" == instr.get("rightType"):
    #     variableList.add(instr["right"])
    if "identifier" == instr.get("resultType"):
        variableList.add(instr["result"])
    return variableList

# def placePhiNodeForVariable(variable,someData,content):
#     CFG = content["CFG"]
#     dominanceFrontiers = content["dominanceFrontiers"]
#     basicBlocks = content["basicBlocks"]
    
#     worklist = someData
#     hasAlready = set()
#     consideredAlready = set([i for i in worklist])
#     while worklist:
#         x = str(worklist.pop())
#         for domf in dominanceFrontiers[x]:
#             domf = str(domf)
#             if not domf in hasAlready:
#                 basicBlocks[domf].insert(1,phiNode(variable))
#                 # print(f"Inserting phi node for var {variable} at {domf}")
#                 hasAlready.add(domf)
            
#             if not domf in consideredAlready:
#                 worklist.add(domf)
#                 consideredAlready.add(domf)
        
#     content["basicBlocks"] = basicBlocks
#     return content

def placePhiNodeForVariable(variable,someData,content):
    CFG = content["CFG"]
    dominanceFrontiers = content["dominanceFrontiers"]
    basicBlocks = content["basicBlocks"]
    phiNodes = content["phiNodes"]

    worklist = someData
    hasAlready = set()
    consideredAlready = set([i for i in worklist])


    while worklist:
        x = str(worklist.pop())
        for domf in dominanceFrontiers[x]:
            domf = str(domf)
            if not domf in hasAlready:
                # basicBlocks[domf].insert(1,phiNode(variable))
                if not phiNodes.get(domf):
                    phiNodes[domf] = dict()
                phiNodes[domf][variable] = phiNode(variable)
                # print(f"Inserting phi node for var {variable} at {domf}")
                hasAlready.add(domf)
            
            if not domf in consideredAlready:
                worklist.add(domf)
                consideredAlready.add(domf)
        
    content["phiNodes"] = phiNodes

def phiNode(variable):
    return {
        "type":"phi",
        "target":variable,
        "input":list(),
        "version":None,
    }

def convertIRToIR():
    with open("intermediateOutput/ir2Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    outputFileList = []
    
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
            
        content = generateFinalOutput(content)

        newFileName = file.split(".")[0]
        
        fileName = newFileName+".tasSSA.json"
        outputFileList.append(fileName)

        with open(fileName,"w") as jsonFile:            
            json.dump(content,jsonFile)
        
    with open("intermediateOutput/ir3Files.json","w") as ir3File:
        json.dump(outputFileList,ir3File)
        
def RunIRPass3():
    convertIRToIR()