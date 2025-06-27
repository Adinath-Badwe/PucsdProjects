import json
from icecream import ic as print

tempConstantNumber = 0

def generateFinalOutput(content):
    basicBlocks = content["basicBlocks"]
    newBasicBlocks = dict()
    for blockNum,block in basicBlocks.items():
        currentNewBlock = list()
        for index,instr in enumerate(block):
            newInstrList = generateAarch64Instruction(instr)
            currentNewBlock.extend(newInstrList)
        newBasicBlocks[blockNum] = currentNewBlock
        
    content["basicBlocks"] = newBasicBlocks

def getSpecificRegister(regNumber):
    global tempConstantNumber
    tempConstantNumber += 1
    output = "'register:" + str(regNumber) + f":{tempConstantNumber}"
    return output

def getNewTempConstant():
    global tempConstantNumber
    tempConstantNumber += 1
    tempConstant = "'tmp" + str(tempConstantNumber)
    return tempConstant

def getLeftOperand(instr,armInstrList):
    
    if instr["leftType"] == 'identifier':
        left = (instr["left"] + "'" + str(instr["leftVersion"]),"register")
    elif instr["leftType"] == "register":
        left = (instr["left"],"register")
    elif instr["leftType"] == "constant":
        tempConstant = getNewTempConstant()
        movConstant = ("MOV",(tempConstant,"register"),(instr["left"],"constant"))
        armInstrList.append(movConstant)
        left = (tempConstant,"register")
    else:
        raise Exception(f"Instruction Mapping :{instr['resultType']} not implemented")

    return left

def getRightOperand(instr,armInstrList):
    global tempConstantNumber
    
    if instr["rightType"] == 'identifier':
        right = (instr["right"] + "'" + str(instr["rightVersion"]),"register")
    elif instr["rightType"] == "register":
        right = (instr["right"],"register")
    elif instr["rightType"] == "constant":
        tempConstant = getNewTempConstant()
        movConstant = ("MOV",(tempConstant,"register"),(instr["right"],"constant"))
        armInstrList.append(movConstant)
        right = (tempConstant,"register")
    else:
        raise Exception(f"Instruction Mapping :{instr['resultType']} not implemented")

    return right

def getResult(instr,armInstrList):
    if instr["resultType"] == 'identifier':
        result = (instr["target"] + "'" + str(instr["targetVersion"]),"register")
    elif instr["resultType"] == "register":
        result = (instr["result"],"register")
    else:
        raise Exception(f"Instruction Mapping :{instr['resultType']} not implemented")

    return result

def generateAarch64Instruction(instr):
    armInstrList = []
    if instr["type"] == "assign":
        if instr["resultType"] == 'identifier':
            result = (instr["target"] + "'" + str(instr["targetVersion"]),"register")
        elif instr["resultType"] == "identifier":
            result = (instr["target"],"register")
        else:
            raise Exception(f"Instruction Mapping :{instr['resultType']} assignment not implemented")
        
        if instr["assignedValueType"] == 'identifier':
            assignedValue = (instr["assignedValue"] + "'" + str(instr["assignedValueVersion"]),"register")
        elif instr["assignedValueType"] == "register":
            assignedValue = (instr["assignedValue"],"register")
        elif instr["assignedValueType"] == "constant":
            tempConstant = getNewTempConstant()
            movConstant = ("MOV",(tempConstant,"register"),(instr["assignedValue"],"constant"))
            armInstrList.append(movConstant)
            assignedValue = (tempConstant,"register")
        else:
            raise Exception(f"Instruction Mapping :{instr['resultType']} assignment not implemented")

        armInstr = ("MOV",result,assignedValue)
        armInstrList.append(armInstr)
        
    elif instr["type"] in ["add","mult"]:
        result = getResult(instr,armInstrList)
        
        left = getLeftOperand(instr,armInstrList)
        right = getRightOperand(instr,armInstrList)
        
        if instr["operator"] == "+":
            operator = "ADD"
        elif instr["operator"] == "-":
            operator = "SUB"
        elif instr["operator"] == "*":
            operator = "MUL"
        elif instr["operator"] == "/":
            operator = "SDIV"
        else:
            raise Exception("Unknown operator")
        
        armInstr = (operator,result,left,right)
        armInstrList.append(armInstr)
        
    elif instr["type"] == "relational":
        result = getResult(instr,armInstrList)

        left = getLeftOperand(instr,armInstrList)
        right = getRightOperand(instr,armInstrList)

        tempConstant = getNewTempConstant()
        armInstrList.append(("MOV",(tempConstant,"register"),("1","constant")))
        if instr["operator"] == "<":
            armInstrList.append(("CMP",left,right))
            armInstrList.append(("CSEL",result,(tempConstant,"register"),("XZR","physicalRegister"),"LT"))
        elif instr["operator"] == ">":
            armInstrList.append(("CMP",left,right))
            armInstrList.append(("CSEL",result,(tempConstant,"register"),("XZR","physicalRegister"),"GT"))
        elif instr["operator"] == ">=":
            armInstrList.append(("CMP",left,right))
            armInstrList.append(("CSEL",result,(tempConstant,"register"),("XZR","physicalRegister"),"GE"))
        elif instr["operator"] == "<=":
            armInstrList.append(("CMP",left,right))
            armInstrList.append(("CSEL",result,(tempConstant,"register"),("XZR","physicalRegister"),"LE"))
        else:
            raise Exception("Unknown operator")
    elif instr["type"] == "equality":
        result = getResult(instr,armInstrList)

        left = getLeftOperand(instr,armInstrList)
        right = getRightOperand(instr,armInstrList)

        tempConstant = getNewTempConstant()
        armInstrList.append(("MOV",(tempConstant,"register"),("1","constant")))
        if instr["operator"] == "==":
            armInstrList.append(("CMP",left,right))
            armInstrList.append(("CSEL",result,(tempConstant,"register"),("XZR","physicalRegister"),"EQ"))
        elif instr["operator"] == "!=":
            armInstrList.append(("CMP",left,right))
            armInstrList.append(("CSEL",result,(tempConstant,"register"),("XZR","physicalRegister"),"NE"))
        else:
            raise Exception("Unknown operator")
        
    elif instr["type"] == "branch":
        armInstrList.append(("B",instr["label"]))
        
    elif instr["type"] == "branchConditional":
        value = instr["value"]
        if instr["valueType"] == "constant":
            tempConstant = getNewTempConstant()
            armInstrList.append(("MOV",(tempConstant,"register"),(instr["value"],"constant")))
            value = tempConstant
        someValue = (value,"register")
        armInstrList.append(("CMP",someValue,("0","constant")))
        armInstrList.append(("B.NE",instr["labelTrue"]))
        armInstrList.append(("B",instr["labelFalse"]))
        
    elif instr["type"] == "label":
        armInstrList.append(("label",instr["labelNumber"]))
        
    elif instr["type"] == "return":
        value = instr["value"]
        if instr["valueType"] == "constant":
            tempConstant = getNewTempConstant()
            armInstrList.append(("MOV",(tempConstant,"register"),(instr["value"],"constant")))
            value = tempConstant
        elif instr["valueType"] == "identifier":
            value = instr["value"] + "'" + str(instr["valueVersion"])
            
        someValue = (value,"register")
        
        regZero = getSpecificRegister(0)
        armInstrList.append(("MOV",(regZero,"register"),someValue))
        armInstrList.append(("RET","RET"))
    elif instr["type"] == "postfix":
        if instr["use"] == "funcCall":
            if instr.get("argumentList"):
                for index,argument in enumerate(instr["argumentList"]):
                    if argument["resultType"] == 'identifier':
                        instr["argumentList"][index] = (argument["result"] + "'" + str(argument["resultVersion"]),"register")
                    elif argument["resultType"] == 'constant':
                        instr["argumentList"][index] = (argument["result"],"constant")
                    elif argument["resultType"] == 'register':
                        instr["argumentList"][index] = (argument["result"],"register")
            else:
                instr["argumentList"] = None
            armInstrList.append(("BL",instr["funcName"],(instr["result"],instr["resultType"]),instr["argumentList"]))
        else:
            raise Exception(f"Instruction Selection : Please add the necessary aarch64 mapping for type : Postfix {instr['use']}")
    else:
        raise Exception(f"Instruction Selection : Please add the necessary aarch64 mapping for type {instr['type']}")

    return armInstrList

def generateOutput():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    newFileList = list()
    
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
            
        generateFinalOutput(content)
        
        newFileName = file.split(".")[0]
        
        fileName = newFileName+".pseudoAarch64.json"

        newFileList.append(fileName)

        with open(fileName,"w") as jsonFile:            
            json.dump(content,jsonFile)
        
    with open("intermediateOutput/ir4Files.json","w") as jsonFile:
        json.dump(newFileList,jsonFile)

def RunInstructionSelection():
    generateOutput()