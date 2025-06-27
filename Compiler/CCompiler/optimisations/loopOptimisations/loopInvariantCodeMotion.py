import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import getPredecessors,getSuccessors

def generateFinalOutput(content):
    CFG = content["CFG"]
    idom = content["idom"]
    dominators = content["dominators"]
    naturalLoops = computeNaturalLoops(CFG,dominators,idom)
    print(naturalLoops)
    

def convertIRToIR():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        generateFinalOutput(content)

        with open(file,"w") as jsonFile:            
            json.dump(content,jsonFile)        


def runLoopInvariantCodeMotion():
    global hasOptimised
    
    hasOptimised = False
    convertIRToIR()
    return hasOptimised