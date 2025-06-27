import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import computeDominators,buildDomTree,getMyTree,getSuccessors,getPredecessors
from copy import deepcopy
from networkx import dominance_frontiers,DiGraph

def generateFinalOutput(content):    
    removePhiNodes(content)
  

def removePhiNodes(content):
    basicBlocks = content["basicBlocks"]
    phiNodes = content["phiNodes"]
    CFG = content["CFG"]
    CFG = set([(str(x),str(y)) for x,y in CFG])
    nodeList = list(basicBlocks.keys())
    
    replaceWith = dict()
    
    for block in nodeList:
        preds = getPredecessors(block,CFG)
        for predecessor in preds:
            predecessorSuccessors = getSuccessors(predecessor,CFG)
            
            if len(predecessorSuccessors) > 1:
                newBlock = predecessor + "*"
                CFG.remove((predecessor,block))
                CFG.add((predecessor,newBlock))
                CFG.add((newBlock,block))
                basicBlocks[newBlock] = list()
                
                replaceWith[predecessor] = newBlock
                pass
            else:
                pass
                
        if phiNodes.get(block):
            for variable,varData in phiNodes[block].items():
                targetVersion = varData["version"]
                for version,blockNum in varData["input"]:
                    if replaceWith.get(blockNum):
                        print("HERE IS THE PLACE WHERE CRITICAL EDGE SPLITTING WORKED")
                        blockNum = replaceWith[blockNum]
                    
                    instruction = {
                        "type": "assign",
                        "target": variable,
                        "targetType": "identifier",
                        "result": variable,
                        "resultType": "identifier",
                        "assignedValue": variable,
                        "assignedValueType": "identifier",
                        "assignedValueVersion": version,
                        "targetVersion": targetVersion
                    }
                    basicBlocks[str(blockNum)].insert(-1,instruction)
                                        

    del content["phiNodes"]
    del content["domtree"]
    del content["idom"]
    del content["dominanceFrontiers"]
    del content["dominators"]
                    
  
# def removePhiNodes(content):
#     basicBlocks = content["basicBlocks"]
#     phiNodes = content["phiNodes"]
#     CFG = content["CFG"]
#     CFG = set([(str(x),str(y)) for x,y in CFG])
#     nodeList = list(basicBlocks.keys())
#     parallelCopies = dict()
    
#     replaceWith = dict()
    
#     for block in nodeList:
#         preds = getPredecessors(block,CFG)
#         for predecessor in preds:
#             predecessorSuccessors = getSuccessors(predecessor,CFG)
            
#             if len(predecessorSuccessors) > 1:
#                 newBlock = predecessor + "*"
#                 CFG.remove((predecessor,block))
#                 CFG.add((predecessor,newBlock))
#                 CFG.add((newBlock,block))
#                 basicBlocks[newBlock] = list()
                
#                 replaceWith[predecessor] = newBlock
#                 parallelCopies[newBlock] = dict()
#             else:
#                 parallelCopies[predecessor] = dict()
        
#         if phiNodes.get(block):
#             for variable,varData in phiNodes[block].items():
#                 targetVersion = varData["version"]
#                 for version,blockNum in varData["input"]:
#                     if replaceWith.get(blockNum):
#                         print("HERE IS THE PLACE WHERE CRITICAL EDGE SPLITTING WORKED")
#                         blockNum = replaceWith[blockNum]
#                     parallelCopies[str(blockNum)][variable] = (targetVersion,version)
                    

        
#     content["parallelCopies"] = parallelCopies
#     del content["phiNodes"]
#     del content["domtree"]
#     del content["idom"]
#     del content["dominanceFrontiers"]
#     del content["dominators"]
                    

def convertIRToIR():
    with open("intermediateOutput/ir3Files.json","r") as jsonFile:
        fileList = json.load(jsonFile)
        
    newFileList = []
    for file in fileList:
        with open(file,"r") as jsonFile:
            content = json.load(jsonFile)
        
        generateFinalOutput(content)
        
        newFileName = file.split(".")[0]
        
        fileName = newFileName+".tasNonSSA.json"
        
        newFileList.append(fileName)
        
        with open(fileName,"w") as jsonFile:            
            json.dump(content,jsonFile)   
            
    with open("intermediateOutput/ir3Files.json","w") as jsonFile:
        json.dump(newFileList,jsonFile)
        
def RunIRPass4():
    convertIRToIR()
    # pass