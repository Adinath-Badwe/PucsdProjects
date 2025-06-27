import json
from IntermediateRepresentation.irPass2Funcs import getNodesFromCFG
from icecream import ic as print

hasOptimised : bool

def performDataFlowAnalysis(content):
    basicBlocks = content["basicBlocks"]
    CFG = content["CFG"]
    nodes = list(basicBlocks.keys())
    output = {str(node):dict() for node in list(basicBlocks.keys())}
    
    for blockNum,block in basicBlocks.items():
        for instr in block:
            output = getInformationFromInstruction(instr,blockNum,output) 
    
    return output

def getInformationFromInstruction(instr,blockNum,output):
    
    if instr["type"] == "assign" and instr["assignedValueType"] == "constant":
        if not output[blockNum].get(instr["target"]):
            output[blockNum][instr["target"]] = dict()
        output[blockNum][instr["target"]][instr["targetVersion"]] = instr["assignedValue"]
    
    return output

def generateFinalOutput(content):
    global hasOptimised
    
    basicBlocks = content["basicBlocks"]
    analysisData = performDataFlowAnalysis(content)
    phiNodes = content["phiNodes"]
    
    phiNodesToRemove = []
    
    for blockNum,variablesDict in phiNodes.items():
        
        for variable,varData in variablesDict.items():
            version,versionBlockNum = varData["input"][0]
            blockData = analysisData.get(str(versionBlockNum))
            if not blockData:
                continue
            if not blockData.get(variable):
                continue
            
            finalValue = blockData.get(variable).get(version)
            isConstantPossible = True
            for version,versionBlockNum in varData["input"]:
                versionBlockNum = str(versionBlockNum)
                value = analysisData[str(versionBlockNum)].get(variable)
                if value:
                    value = value.get(version)
                if (not value) or (value != finalValue):
                    isConstantPossible = False
            
            if isConstantPossible:
                # phiNodes[blockNum][variable]["inputType"] = "constant"
                # phiNodes[blockNum][variable]["input"] = finalValue
                appInstr = {
                            "type": "assign",
                            "target": variable,
                            "targetType": "identifier",
                            "result": variable,
                            "resultType": "identifier",
                            "assignedValue": finalValue,
                            "assignedValueType": "constant",
                            "targetVersion": phiNodes[blockNum][variable]["version"]
                        }
                basicBlocks[blockNum].insert(1,appInstr)
                phiNodesToRemove.append(phiNodes[blockNum][variable])
    
    for remNode in phiNodesToRemove:
        del phiNodes[blockNum][variable]
    
    for blockNum,block in basicBlocks.items():
        for instrIndex,instr in enumerate(block):
            instr,changed = modifyInstrConstantPropagation(instr,blockNum,analysisData,content)
            if changed:
                block[instrIndex] = instr
                hasOptimised = True
        basicBlocks[blockNum] = block
    
    return content

def getDataFromAnalysisData(content,analysisData,value,blockNum):
    idom = content["idom"]
    currentBlock = blockNum

    while True:
        if analysisData[str(currentBlock)].get(value):
            break
        if currentBlock == '0':
            break
        currentBlock = str(idom[currentBlock])
        
    return analysisData[currentBlock].get(value)

def modifyInstrConstantPropagation(instr,blockNum,analysisData,content):
    changed = False
    
    if instr.get("leftType") == "identifier" and getDataFromAnalysisData(content,analysisData,instr["left"],blockNum) and instr["leftVersion"] in getDataFromAnalysisData(content,analysisData,instr["left"],blockNum):
        instr["left"] = getDataFromAnalysisData(content,analysisData,instr["left"],blockNum)[instr["leftVersion"]]
        instr["leftType"] = "constant"
        changed = True
    
    if instr.get("rightType") == "identifier" and getDataFromAnalysisData(content,analysisData,instr["right"],blockNum) and instr["rightVersion"] in getDataFromAnalysisData(content,analysisData,instr["right"],blockNum):
        instr["right"] = getDataFromAnalysisData(content,analysisData,instr["right"],blockNum)[instr["rightVersion"]]
        instr["rightType"] = "constant"
        changed = True
    
    if instr.get("valueType") == "identifier" and getDataFromAnalysisData(content,analysisData,instr["value"],blockNum) and instr["valueVersion"] in getDataFromAnalysisData(content,analysisData,instr["value"],blockNum):
        instr["value"] = getDataFromAnalysisData(content,analysisData,instr["value"],blockNum)[instr["valueVersion"]]
        instr["valueType"] = "constant"
        changed = True
    
    return instr,changed

# def modifyInstrConstantPropagation(instr,blockNum,analysisData):
#     changed = False
#     if instr.get("right") == "m":
#         print(instr,blockNum)
#         print(analysisData)
#     if instr.get("leftType") == "identifier" and analysisData[blockNum].get(instr["left"]) and instr["leftVersion"] in analysisData[blockNum].get(instr["left"]):
#         instr["left"] = analysisData[blockNum][instr["left"]][instr["leftVersion"]]
#         instr["leftType"] = "constant"
#         changed = True
    
#     if instr.get("rightType") == "identifier" and analysisData[blockNum].get(instr["right"]) and instr["rightVersion"] in analysisData[blockNum].get(instr["right"]):
#         instr["right"] = analysisData[blockNum][instr["right"]][instr["rightVersion"]]
#         instr["rightType"] = "constant"
#         changed = True
    
#     return instr,changed

def convertIRToIR():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        content = generateFinalOutput(content)
        
        with open(file,"w") as jsonFile:            
            json.dump(content,jsonFile)   

def runConstantPropagation():
    global hasOptimised
    
    hasOptimised = False
    convertIRToIR()
    
    return hasOptimised