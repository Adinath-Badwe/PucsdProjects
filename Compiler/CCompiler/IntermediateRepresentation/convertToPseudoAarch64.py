import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import (
    computeDominators,
    buildDomTree,
    getMyTree,
    getSuccessors,
    getPredecessors,
)
from copy import deepcopy
from networkx import dominance_frontiers, DiGraph

callerSavedRegisters = None


def generateFinalOutput(content):
    allocatePhysicalRegisters(content)


def isDataElementSpecificRegister(dataElement):
    value = str(dataElement[0]).split("'")
    if len(value) == 2:
        value = value[1].split(":")
        if value[0] == "register":
            return True
    return False


def getFrameLinkStackLocation(location):
    return location["'framePointer"]


def allocatePhysicalRegisters(content):
    registers = content["registers"]
    location = content["stackLocation"]
    registersUsed = content["registersUsed"]
    basicBlocks = content["basicBlocks"]
    spareRegister = generateRegisterName(content["spareRegister0"])
    spareRegister1 = generateRegisterName(content["spareRegister1"])
    calleeRegistersUsed = content["calleeRegistersUsed"]
    # callerRegistersUsed = content["callerRegistersUsed"]
    stackSize = content["stackSize"]
    newBlocks = dict()
    global callerSavedRegisters
    callerSavedRegisters = content["callerSavedRegisters"]

    for blockNum, block in basicBlocks.items():
        currentBlock = list()

        for index, instr in enumerate(block):
            instrList = generateNewInstructions(
                instr,
                registers,
                location,
                spareRegister,
                spareRegister1,
                calleeRegistersUsed,
                stackSize,
            )
            currentBlock.extend(instrList)

        if blockNum == "0":
            currentBlock = (
                currentBlock[:1]
                + generatePrologue(
                    stackSize, spareRegister1, location, calleeRegistersUsed
                )
                + currentBlock[1:]
            )

        newBlocks[blockNum] = currentBlock

    content["basicBlocks"] = newBlocks
    # print(newBlocks)


def generateRegisterName(registerNumber):
    return f"X{registerNumber}"


def getRegisterNumber(dataElement):
    value = str(dataElement[0]).split("'")
    value = value[1].split(":")
    return int(value[1])


def generateMovInstruction(destination, source):
    return ("MOV", destination, source)


def genStrInstr(source, destination):
    return ("STR", source, destination)


def genLdrInstr(source, destination):
    return ("LDR", destination, source)


def generateStrCSRInstr(calleeRegistersUsed, spareRegister1, location):
    instrList = []
    for register in calleeRegistersUsed:
        registerStr = "'calleeSavedRegister" + str(register)
        registerValue = f"X{register}"
        instrList.append(
            generateMovInstruction(spareRegister1, "#" + str(location[registerStr]))
        )
        instrList.append(genStrInstr(registerValue, ("SP", spareRegister1)))
    return instrList


def generateLdrCSRInstr(calleeRegistersUsed, spareRegister1, location):
    instrList = []
    for register in calleeRegistersUsed:
        registerStr = "'calleeSavedRegister" + str(register)
        registerValue = f"X{register}"
        instrList.append(
            generateMovInstruction(spareRegister1, "#" + str(location[registerStr]))
        )
        instrList.append(genLdrInstr(("SP", spareRegister1), registerValue))
    return instrList


def saveCallerRegisters(spareRegister1, location):
    instrList = []
    global callerSavedRegisters
    for register in callerSavedRegisters:
        registerStr = "'callerSavedRegister" + str(register)
        registerValue = f"X{register}"
        instrList.append(
            generateMovInstruction(spareRegister1, "#" + str(location[registerStr]))
        )
        instrList.append(genStrInstr(registerValue, ("SP", spareRegister1)))
    return instrList


def loadCallerRegisters(spareRegister1, location):
    instrList = []
    global callerSavedRegisters
    for register in callerSavedRegisters:
        registerStr = "'callerSavedRegister" + str(register)
        registerValue = f"X{register}"
        instrList.append(
            generateMovInstruction(spareRegister1, "#" + str(location[registerStr]))
        )
        instrList.append(genLdrInstr(("SP", spareRegister1), registerValue))
    return instrList


def generatePrologue(stackSize, spareRegister, location, calleeRegistersUsed):
    instrList = []

    instrList.append(generateMovInstruction(spareRegister, "#" + str(stackSize)))
    instrList.append(("SUB", "SP", "SP", spareRegister))
    instrList.append(("MOV", spareRegister, "#" + str(location["'framePointer"])))
    instrList.append(genStrInstr("X29", ("SP", spareRegister)))
    instrList.append(("MOV", spareRegister, "#" + str(location["'linkRegister"])))
    instrList.append(genStrInstr("X30", ("SP", spareRegister)))
    instrList.extend(generateStrCSRInstr(calleeRegistersUsed,spareRegister,location))

    return instrList


def generateNewInstructions(
    oldInstr,
    registers,
    location,
    spareRegister1,
    spareRegister2,
    calleeRegistersUsed,
    stackSize,
):
    instrList = list()
    instrType = oldInstr[0]

    if instrType in ["MOV", "CMP"]:
        target = oldInstr[1]
        source = oldInstr[2]
        targetSpilled = False
        instr = oldInstr

        if registers.get(str(target[0])) or registers.get(str(target[0])) == 0:
            instr = (
                instrType,
                generateRegisterName(registers.get(str(target[0]))),
                instr[2],
            )
        elif location.get(str(target[0])):
            targetSpilled = True
            instr = (instrType, spareRegister1, instr[2])
        elif isDataElementSpecificRegister(target):
            instr = (
                instrType,
                generateRegisterName(getRegisterNumber(target)),
                instr[2],
            )
        elif target[1] == "physicalRegister":
            instr = (instrType, instr[1][0], instr[2])
        else:
            raise Exception("THIS SHOULD NOT BE POSSIBLE")

        if source[1] == "register" and (
            registers.get(str(source[0])) or registers.get(str(source[0])) == 0
        ):
            instr = (
                instrType,
                instr[1],
                generateRegisterName(registers.get(str(source[0]))),
            )
        elif source[1] == "register" and location.get(str(source[0])):
            instrList.append(
                ("LDR", spareRegister1, ("SP", "#" + str(location.get(str(source[0])))))
            )
            instr = (instrType, instr[1], spareRegister1)
        elif source[1] == "constant":
            instr = (instrType, instr[1], "#" + str(instr[2][0]))
        elif source[1] == "physicalRegister":
            instr = (instrType, instr[1], instr[2][0])

        instrList.append(instr)
        if instrType == "MOV" and instr[1] == instr[2]:
            instrList.pop()

        if targetSpilled:
            instrList.append(
                ("STR", spareRegister1, ("SP", "#" + str(location.get(str(target[0])))))
            )

    elif instrType in ["MUL", "ADD", "SUB", "SDIV", "CSEL"]:
        target = oldInstr[1]
        source1 = oldInstr[2]
        source2 = oldInstr[3]
        targetSpilled = False
        instr = oldInstr

        if registers.get(str(target[0])) or registers.get(str(target[0])) == 0:
            instr = (
                instrType,
                generateRegisterName(registers.get(str(target[0]))),
                instr[2],
                instr[3],
            )
        elif location.get(str(target[0])):
            targetSpilled = True
            instr = (instrType, spareRegister1, instr[2], instr[3])

        if source1[1] == "register" and (
            registers.get(str(source1[0])) or registers.get(str(source1[0])) == 0
        ):
            instr = (
                instrType,
                instr[1],
                generateRegisterName(registers.get(str(source1[0]))),
                instr[3],
            )
        elif source1[1] == "constant":
            instr = (instrType, instr[1], "#" + str(instr[2][0]), instr[3])
        elif source1[1] == "register" and location.get(str(source1[0])):
            instrList.append(
                (
                    "LDR",
                    spareRegister1,
                    ("SP", "#" + str(location.get(str(source1[0])))),
                )
            )
            instr = (instrType, instr[1], spareRegister1, instr[3])
        elif source1[1] == "physicalRegister":
            instr = (instrType, instr[1], instr[2][0], instr[3])

        if source2[1] == "register" and (
            registers.get(str(source2[0])) or registers.get(str(source2[0])) == 0
        ):
            instr = (
                instrType,
                instr[1],
                instr[2],
                generateRegisterName(registers.get(str(source2[0]))),
            )
        elif source2[1] == "constant":
            instr = (instrType, instr[1], instr[2], "#" + str(instr[3][0]))
        elif source2[1] == "register" and location.get(str(source2[0])):
            instrList.append(
                (
                    "LDR",
                    spareRegister2,
                    ("SP", "#" + str(location.get(str(source2[0])))),
                )
            )
            instr = (instrType, instr[1], instr[2], spareRegister2)
        elif source2[1] == "physicalRegister":
            instr = (instrType, instr[1], instr[2], instr[3][0])

        if instrType == "CSEL":
            instr = (*instr, oldInstr[-1])

        instrList.append(instr)

        if targetSpilled:
            instrList.append(
                ("LDR", spareRegister1, ("SP", "#" + str(location.get(str(target[0])))))
            )
    elif instrType == "RET":
        extraAppends = generateLdrCSRInstr(calleeRegistersUsed,spareRegister1,location)

        if extraAppends:
            instrList.extend(extraAppends)

        instrList.append(("MOV", spareRegister1, "#" + str(location["'framePointer"])))
        instrList.append(genLdrInstr(("SP", spareRegister1), "X29"))
        instrList.append(("MOV", spareRegister1, "#" + str(location["'linkRegister"])))
        instrList.append(genLdrInstr(("SP", spareRegister1), "X30"))
        instrList.append(generateMovInstruction(spareRegister1, "#" + str(stackSize)))
        instrList.append(("ADD", "SP", "SP", spareRegister1))

        instrList.append(oldInstr)

    elif instrType in ["BL"]:
        target = oldInstr[2]
        if oldInstr[3]:
            
            for index,argument in enumerate(oldInstr[3]):
                if index < 8:
                    if argument[1] == "constant":
                        instrList.append(generateMovInstruction(generateRegisterName(index),"#"+str(argument[0])))
                    elif argument[1] == "register":
                        if registers.get(str(argument[0])):
                            allocatedRegister = registers[str(argument[0])]
                            instrList.append(generateMovInstruction(generateRegisterName(index),generateRegisterName(allocatedRegister)))
                        elif location.get(str(argument[0])):
                            stackLocation = location[str(argument[0])]
                            
                            instrList.append(generateMovInstruction(spareRegister1,"#"+str(stackLocation)))
                            instrList.append(genLdrInstr(("SP",spareRegister1),spareRegister1))
                            instrList.append(generateMovInstruction(generateRegisterName(index),generateRegisterName(spareRegister1)))
                        else:
                            raise Exception()
                else:
                    raise Exception()
        
        instrList.extend(saveCallerRegisters(spareRegister1,location))
        instrList.append(
            generateMovInstruction(spareRegister1, "#" + str(location["'X0"]))
        )
        instrList.append(genStrInstr("X0", ("SP", spareRegister1)))
        instrList.append(oldInstr[:2])

        if registers.get(str(target[0])):
            value = registers[str(target[0])]
            instrList.append(generateMovInstruction(generateRegisterName(value), "X0"))
        elif location.get(str(target[0])):
            value = location[str(target[0])]
            instrList.append(generateMovInstruction(spareRegister1, "X0"))
            instrList.append(generateMovInstruction(spareRegister2, "#" + str(value)))
            instrList.append(genStrInstr(spareRegister1, ("SP", spareRegister2)))
        else:
            raise Exception("Target neither in registers nor location")
        

        instrList.append(genLdrInstr(("SP", "#" + str(location["'X0"])), "X0"))
        instrList.extend(loadCallerRegisters(spareRegister1,location))

    elif instrType in ["label", "B", "B.NE"]:
        instrList.append(oldInstr)
    else:
        raise Exception("Unkown instruction type : ", instrType)

    return instrList


def convertIRToIR():
    with open("intermediateOutput/ir4Files.json", "r") as jsonFile:
        fileList = json.load(jsonFile)

    newFileList = list()

    for file in fileList:
        with open(file, "r") as jsonFile:
            content = json.load(jsonFile)

        generateFinalOutput(content)

        newFileName = file.split(".")[0]

        fileName = newFileName + ".aarch64.json"

        newFileList.append(fileName)

        with open(fileName, "w") as jsonFile:
            json.dump(content, jsonFile)

    with open("intermediateOutput/ir5Files.json", "w") as jsonFile:
        json.dump(newFileList, jsonFile)


def RunIRPass5():
    convertIRToIR()
    # pass
