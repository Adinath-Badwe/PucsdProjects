from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import getNodesFromCFG,getPredecessors

def generateGenKillSets(content):
    gen,kill = set()
    
    CFG = content["CFG"]
    basicBlocks = content["basicBlocks"]
    nodes = getNodesFromCFG(CFG)
    
    
    
    return gen,kill

def generateFinalOutput(content):
    CFG = content["CFG"]
    basicBlocks = content["basicBlocks"]
    nodes = getNodesFromCFG(CFG)
    gen,kill = generateGenKillSets(content)
    
    outDict = {node:set() for node in nodes}
    inDict = {node:set() for node in nodes}
    changed = nodes
    
    while(changed):
        element = changed.pop()
        
        inDict[element] = set()
        
        for pred in getPredecessors(element,CFG):
            inDict[element] = inDict[element].union(outDict[pred])
        
        # OUT[n] = GEN[n] Union (IN[n] -KILL[n])

        # outDict[element] = 

def convertIRToIR():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        content = generateFinalOutput(content)
        
        with open(file,"w") as jsonFile:
            json.dump(content,jsonFile)        

def runReachingDefinitions():
    convertIRToIR()