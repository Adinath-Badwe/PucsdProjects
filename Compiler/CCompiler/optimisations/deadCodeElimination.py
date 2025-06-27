import json
hasOptimised = False
from icecream import ic as print

def generateFinalOutput(content):    
    removeUnnecessaryAssignmentsAndTemporaries(content)

def removeUnnecessaryAssignmentsAndTemporaries(content):
    defUseChain = buildDefUseChain(content)
    basicBlocks = content["basicBlocks"]
    phiNodes = content["phiNodes"]
    
    instrToRemove = dict()
    phiToRemove = dict()
    
    for (var,varVersion),varData in defUseChain.items():
        if not varData["uses"]:
            if varData["definition"][1] == "phi":
                if not phiToRemove.get(varData["definition"][0]):
                    phiToRemove[varData["definition"][0]] = list()
                phiToRemove[varData["definition"][0]].append(var)
            else:
                if not instrToRemove.get(varData["definition"][0]):
                    instrToRemove[varData["definition"][0]] = list()
                instrToRemove[varData["definition"][0]].append(varData["definition"][1])
            
    
    for blockNum,instrList in instrToRemove.items():
        for instrIndx in sorted(instrList,reverse=True):
            basicBlocks[blockNum].pop(instrIndx)
    
    for blockNum,varList in phiToRemove.items():
        for var in varList:
            del phiNodes[blockNum][var]

def buildDefUseChain(content):
    basicBlocks = content["basicBlocks"]
    defUseChain = dict()
    phiNodes = content["phiNodes"]
    
    for blockNum,block in basicBlocks.items():
        for index,instr in enumerate(block):
            isValid = checkValidInstr(instr)
            if isValid:
                addNecessaryInfoToDefUse(instr,blockNum,index,defUseChain)
        
        blockPhiNodes = phiNodes.get(str(blockNum))
        
        if blockPhiNodes:
            for var,varData in blockPhiNodes.items():
                
                if not defUseChain.get((var,varData["version"])):
                    defUseChain[(var,varData["version"])] = {"definition":(blockNum,"phi"),"uses":list()}
                    
                for version,block1 in varData["input"]:
                    if not defUseChain.get((var,version)):
                        defUseChain[(var,version)] = {"definition":None,"uses":list()}
                    defUseChain[(var,version)]["uses"].append((blockNum,"phi"))
    return defUseChain

def addNecessaryInfoToDefUse(instr,blockNum,index,defUseChain):
    if instr.get("leftType") == "identifier":
        if not defUseChain.get((instr["left"],instr["leftVersion"])):
            defUseChain[(instr["left"],instr["leftVersion"])] = {"definition":None,"uses":list()}
        defUseChain[(instr["left"],instr["leftVersion"])]["uses"].append((blockNum,index))
        
    if instr.get("rightType") == "identifier":
        if not defUseChain.get((instr["right"],instr["rightVersion"])):
            defUseChain[(instr["right"],instr["rightVersion"])] = {"definition":None,"uses":list()}
        defUseChain[(instr["right"],instr["rightVersion"])]["uses"].append((blockNum,index))
            
    if instr.get("resultType") == "identifier":
        if not defUseChain.get((instr["result"],instr["targetVersion"])):
            defUseChain[(instr["result"],instr["targetVersion"])] = {"definition":(blockNum,index),"uses":list()}
        defUseChain[(instr["result"],instr["targetVersion"])]["definition"] = (blockNum,index)

def checkValidInstr(instr):
    isValid = False
    if instr.get("leftType") == "identifier":
        isValid = True
    if instr.get("rightType") == "identifier":
        isValid = True
    if instr.get("resultType") == "identifier":
        isValid = True
    
    return isValid
    

def convertIRToIR():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        generateFinalOutput(content)
        
        with open(file,"w") as jsonFile:            
            json.dump(content,jsonFile)   

def runDeadCodeElimination():
    global hasOptimised
    
    hasOptimised = False
    convertIRToIR()
    
    return hasOptimised