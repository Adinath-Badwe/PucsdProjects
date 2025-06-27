from icecream import ic as print
import json

hasOptimised = False

def generateFinalOutput(content):
    global hasOptimised
    basicBlocks = content["basicBlocks"]
    registerValues = dict()
    valuesCurrent = set()
    
    for blockNum,block in basicBlocks.items():
        index = 0
        while index < len(block):
            instr = block[index]
            if isCandidateConstantFolding(instr):
                valuesCurrent.add(instr["result"])
                registerValues[instr["result"]] = calculateConstantResult(instr)
                block.pop(index)
                hasOptimised = True
            else:
                modifiedInstr = False
                instr,modifiedInstr = replaceRegister(instr,registerValues,valuesCurrent)
                block[index] = instr
                if not modifiedInstr:
                    index += 1
    content["basicBlocks"] = basicBlocks
    return content

def replaceRegister(instr,registerValues,valuesCurrent):
    modifiedInstr = False
    
    if instr.get("leftType") == "register" and instr.get("left") in valuesCurrent:
        instr["leftType"] = "constant"
        instr["left"] = str(registerValues[instr["left"]])
        modifiedInstr = True
    if instr.get("rightType") == "register" and instr.get("right") in valuesCurrent:
        instr["rightType"] = "constant"
        instr["right"] = str(registerValues[instr["right"]])
        modifiedInstr = True
    if instr.get("type") == "assign" and instr.get("assignedValue") in valuesCurrent and instr.get("assignedValueType") == "register":
        instr["assignedValue"] = str(registerValues[instr["assignedValue"]])
        instr["assignedValueType"] = "constant"
        modifiedInstr = True
    if instr.get("valueType") == "register" and instr["value"] in valuesCurrent:
        instr["value"] = str(registerValues[instr["value"]])
        instr["valueType"] = "constant"
        modifiedInstr = True
    
    return instr,modifiedInstr

def calculateConstantResult(instr):
    leftValue = instr["left"]
    rightValue = instr["right"]
    operator = instr["operator"]
    
    if operator == "*":
        result = int(leftValue) * int(rightValue)
    elif operator == "+":
        result = int(leftValue) + int(rightValue)
    elif operator == "-":
        result = int(leftValue) - int(rightValue)
    elif operator == ">":
        result = int(leftValue) > int(rightValue)
    elif operator == "<":
        result = int(leftValue) < int(rightValue)
    elif operator == "<=":
        result = int(leftValue) <= int(rightValue)
    elif operator == ">=":
        result = int(leftValue) >= int(rightValue)
    elif operator == "==":
        result = int(leftValue) == int(rightValue)
    # elif operator == "/":
    #     result = leftValue / rightValue
    
    return result

def isCandidateConstantFolding(instr):
    isCandidate = False
    if instr.get("leftType") == instr.get("rightType") == "constant":
        isCandidate = True
    return isCandidate

def convertIRToIR():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        content = generateFinalOutput(content)
        
        with open(file,"w") as jsonFile:            
            json.dump(content,jsonFile)        

def runConstantFolding():
    global hasOptimised
    convertIRToIR()
    return hasOptimised
    