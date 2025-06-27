from icecream import ic as print
import json
import operator
import heapq

stackLocation = 0
REGISTERS_TO_USE = 29
freeRegisters = [i for i in range(REGISTERS_TO_USE)]
calleeRegistersUsed = set()
SPARE_REGISTER_0 = 8
SPARE_REGISTER_1 = 18
freeRegisters.remove(SPARE_REGISTER_0)
freeRegisters.remove(SPARE_REGISTER_1)
heapq.heapify(freeRegisters)

def addToActive(active,dataElement):
    active.append(dataElement)
    sortActive(active)
    
def sortActive(active):
    active.sort(key=lambda x : x[0][1][1])
    active.sort(key=lambda x : x[0][1][0])

def compareTwoIntervals(leftInterval,rightInterval,operator):
    if operator == "==":
        return leftInterval == rightInterval
    elif operator == ">":
        if leftInterval[0] >= rightInterval[0]:
            if (leftInterval[0] > rightInterval[0]) or (leftInterval[1] > rightInterval[1]):
                return True
        return False
    elif operator == ">=":
        if leftInterval[0] >= rightInterval[0]:
            if (leftInterval[0] > rightInterval[0]) or (leftInterval[1] >= rightInterval[1]):
                return True
        return False
    else:
        raise Exception(f"Unknow operator : {operator}")

def newStackLocation(size=None):
    if size is None:
        size = 8
    global stackLocation
    
    output = stackLocation
    stackLocation += size
    
    return output

def getFreeRegister():
    global freeRegisters,calleeRegistersUsed
    registerFreed = heapq.heappop(freeRegisters)
    calleeRegistersUsed.add(registerFreed)
    return registerFreed

def addFreeRegister(registerValue):
    global freeRegisters
    heapq.heappush(freeRegisters,registerValue)

def removeFreeRegister(registerValue):
    global freeRegisters
    freeRegisters.remove(registerValue)
    heapq.heapify(freeRegisters)

def isDataElementSpecificRegister(dataElement):
    value = str(dataElement[0]).split("'")
    if len(value) == 2:
        value = value[1].split(":")
        if value[0] == "register":
            return True
    return False

def getRegisterNumber(dataElement):
    value = str(dataElement[1]).split("'")
    value = value[1].split(":")
    return int(value[1])

def generateFinalOutput(content):
    global REGISTERS_TO_USE,SPARE_REGISTER_0,SPARE_REGISTER_1,calleeRegistersUsed
    intervals = performLivenessAnalysis(content)
    registers,location = performRegisterAllocation(content,intervals,REGISTERS_TO_USE)
    newRegisters = dict()
    newLocation = dict()
    
    for key,value in registers.items():
        newRegisters[key[1]] = value
    
    for key,value in location.items():
        newLocation[key[1]] = value
    
    calleeRegistersUsed.difference_update(range(19))
    
    callerSavedRegisters =  list(range(9,18))
    
    for i in range(9,18):
        newLocation[f"'callerSavedRegister{i}"] = newStackLocation()
        
    for i in calleeRegistersUsed:
        newLocation[f"'calleeSavedRegister{i}"] = newStackLocation()
    
    newLocation["'framePointer"] = newStackLocation()
    newLocation["'linkRegister"] = newStackLocation()
    newLocation["'X0"] = newStackLocation()
    
    content["registers"] = newRegisters
    content["stackLocation"] = newLocation
    content["registersUsed"] = REGISTERS_TO_USE
    content["spareRegister0"] = SPARE_REGISTER_0
    content["spareRegister1"] = SPARE_REGISTER_1
    content["calleeRegistersUsed"] = list(calleeRegistersUsed)
    content["callerSavedRegisters"] = callerSavedRegisters
    content["stackSize"] = stackLocation

def performRegisterAllocation(content,intervals,R):
    active = list()
    registers = dict()
    location = dict()
    reverseRegisters = dict()
    
    newDataStructute = sorted([(value,key) for key,value in intervals.items()],key=lambda x :x[0][0][1])
    newDataStructute = sorted(newDataStructute,key=lambda x :x[0][0][0])
    newDataStructute = [((x[0],x[1]),y) for x,y in newDataStructute]
    
    for dataElement in newDataStructute:
        liveInterval,virtualRegister = dataElement
        expireOldIntervals(dataElement,active,registers,freeRegisters)
        
        if len(active) == R:
            spillAtInterval(dataElement,active,registers,reverseRegisters,location)
        else:   
            allocatedRegister = getFreeRegister()
            registers[dataElement] = allocatedRegister
            reverseRegisters[allocatedRegister] = dataElement
            addToActive(active,dataElement)
            
    return registers,location
                
def spillAtInterval(dataElement,active,registers,reverseRegisters,location):
    spill = active[-1]
    spillEnd = spill[0][1]
    currentEnd = dataElement[0][1]

    if compareTwoIntervals(spillEnd,currentEnd,">"):
        allocatedRegister = registers[spill]
        
        registers[dataElement] = registers[spill]
        reverseRegisters[allocatedRegister] = dataElement
        del registers[spill]
        
        location[spill] = newStackLocation()
        active.pop()
        addToActive(active,dataElement)
    else:
        location[dataElement] = newStackLocation()

def expireOldIntervals(dataElement,active,registers,freeRegisters):
    liveInterval,virtualRegister = dataElement
    indexTillRemove = 0
    
    for currentInterval,_ in active:
        currentEnd = currentInterval[1]
        liveStart = liveInterval[0]
        
        if compareTwoIntervals(currentEnd,liveStart,">="):
            break
        
        indexTillRemove += 1

    for i in range(indexTillRemove):
        live,data = active.pop(0)
        # freeRegisters.add(registers[(live,data)])
        addFreeRegister(registers[(live,data)])

def performLivenessAnalysis(content):
    basicBlocks = content["basicBlocks"]
    intervals = dict()
    for blockNum,block in basicBlocks.items():
        for index,instr in enumerate(block):
            getLiveInfo(blockNum,index,instr,intervals)
    
    return intervals

def getLiveInfo(blockNum,index,instr,intervals):
    instrType = instr[0]
    if instrType in ["CMP","MOV"]:
        target = instr[1]
        source = instr[2]
        
        updateInterval(target,blockNum,index,intervals)
        updateInterval(source,blockNum,index,intervals)
    elif instrType in ["CSEL","MUL","ADD"]:
        target = instr[1]
        source1 = instr[2]
        source2 = instr[3]
        
        updateInterval(source1,blockNum,index,intervals)
        updateInterval(source2,blockNum,index,intervals)
        updateInterval(target,blockNum,index,intervals)
    elif instrType == "BL":
        updateInterval(instr[2],blockNum,index,intervals)
        
        if instr[3]:
            for argument in instr[3]:
                if argument[1] == "register":
                    updateInterval(argument,blockNum,index,intervals)
    elif instrType in ["label","B","B.NE","RET"]:
        pass
    else:
        raise Exception(f"Unknown Instruction : {instrType}")

def updateInterval(target,blockNum,index,intervals):
    if target[1] != "register" or isDataElementSpecificRegister(target):
        # print(target)
        return 0
    
    target = target[0]
    blockNum = int(blockNum)    
    if not intervals.get(target):
        intervals[target] = [(blockNum,index),(blockNum,index)]
        
    if blockNum <= intervals[target][0][0]:
        if blockNum == intervals[target][0][0] and index < intervals[target][0][1]:
            
            intervals[target][0] = (blockNum,index)
            
        elif blockNum < intervals[target][0][0]:
            
            intervals[target][0] = (blockNum,index)
            
    if blockNum >= intervals[target][1][0]:
        if blockNum == intervals[target][1][0] and index > intervals[target][1][1]:
            
            intervals[target][1] = (blockNum,index)
            
        elif blockNum > intervals[target][1][0]:
            
            intervals[target][1] = (blockNum,index)
            
def generateOutput():
    global stackLocation
    with open("intermediateOutput/ir4Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    newFileList = list()
    
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        stackLocation = 0
        generateFinalOutput(content)
        
        with open(file,"w") as jsonFile:            
            json.dump(content,jsonFile)


def RunRegisterAllocation():
    generateOutput()
    
    

# def performRegisterAllocation(content,intervals,R):
#     active = list()
#     registers = dict()
#     location = dict()
#     reverseRegisters = dict()
    
#     newDataStructute = sorted([(value,key) for key,value in intervals.items()],key=lambda x :x[0][0][1])
#     newDataStructute = sorted(newDataStructute,key=lambda x :x[0][0][0])
#     newDataStructute = [((x[0],x[1]),y) for x,y in newDataStructute]
    
#     checkSet = set([f"'register:{i}" for i in range(32)])
        
#     for dataElement in newDataStructute:
#         liveInterval,virtualRegister = dataElement
#         expireOldIntervals(dataElement,active,registers,freeRegisters)
        
#         if len(active) == R:
#             spillAtInterval(dataElement,active,registers,reverseRegisters,location,checkSet)
#         else:   
#             allocatedRegister = getFreeRegister()
#             if dataElement[1] == "'tmp17":
#                 print(dataElement)
#             registers[dataElement] = allocatedRegister
#             reverseRegisters[allocatedRegister] = dataElement
#             addToActive(active,dataElement)
            
#             if isDataElementSpecificRegister(dataElement):
                
#                 registerNeeded = getRegisterNumber(dataElement)
                
#                 if registerNeeded in freeRegisters:
#                     addFreeRegister(registers[dataElement])
#                     removeFreeRegister(registerNeeded)
#                     reverseRegisters[allocatedRegister] = None
#                     reverseRegisters[registerNeeded] = dataElement
#                     registers[dataElement] = registerNeeded
#                 else:
#                     dataElementToSwitch = reverseRegisters[registerNeeded]
#                     registers[dataElementToSwitch],registers[dataElement] = allocatedRegister,registerNeeded
                    
#                     reverseRegisters[allocatedRegister] = dataElementToSwitch
#                     reverseRegisters[registerNeeded] = dataElement
#     return registers,location
                

# def spillAtInterval(dataElement,active,registers,reverseRegisters,location,checkSet):
#     spill = active[-1]
#     spillEnd = spill[0][1]
#     currentEnd = dataElement[0][1]
    
#     if spill[1] in checkSet:
#         location[dataElement] = newStackLocation()
#     elif compareTwoIntervals(spillEnd,currentEnd,">") or isDataElementSpecificRegister(dataElement):
#         allocatedRegister = registers[spill]
        
#         registers[dataElement] = registers[spill]
#         reverseRegisters[allocatedRegister] = dataElement
#         del registers[spill]
        
#         location[spill] = newStackLocation()
#         active.pop()
#         addToActive(active,dataElement)
        
#         if isDataElementSpecificRegister(dataElement):
#             registerNeeded = getRegisterNumber(dataElement)
            
#             dataElementToSwitch = reverseRegisters[registerNeeded]
#             registers[dataElementToSwitch],registers[dataElement] = allocatedRegister,registerNeeded
            
#             reverseRegisters[allocatedRegister] = dataElementToSwitch
#             reverseRegisters[registerNeeded] = dataElement
#     else:
#         location[dataElement] = newStackLocation()

# def expireOldIntervals(dataElement,active,registers,freeRegisters):
#     liveInterval,virtualRegister = dataElement
#     indexTillRemove = 0
    
#     for currentInterval,_ in active:
#         currentEnd = currentInterval[1]
#         liveStart = liveInterval[0]
        
#         if compareTwoIntervals(currentEnd,liveStart,">="):
#             break
        
#         indexTillRemove += 1

#     for i in range(indexTillRemove):
#         live,data = active.pop(0)
#         # freeRegisters.add(registers[(live,data)])
#         addFreeRegister(registers[(live,data)])
