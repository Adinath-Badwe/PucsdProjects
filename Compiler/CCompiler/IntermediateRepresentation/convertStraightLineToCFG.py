import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import visualiseGraph,computeDomFrontiers,computeDomFrontiers1,computeDominators,buildDomTree

CFG = dict()
basicBlocks = dict()
functionData = dict()
nodes = dict()
dominanceFrontiers = dict()
filesList = []
dominators = None
domTree = None

def resetCFG():
    CFG = dict()

def generateOutputFiles(content):
    
    for funcName,bb in basicBlocks.items():
        fileName = f"intermediateOutput/{funcName}.tasCFG.json"
        filesList.append(fileName)
        with open(fileName,"w") as jsonFile:
            output = dict()
            output["CFG"] = list(CFG[funcName])
            output["basicBlocks"] = dict()
            for labelNum,(start,end) in bb.items():
                output["basicBlocks"][labelNum] = content[start:end+1]
                # newContent += content[start:end+1]
            output["functionData"] = functionData[funcName]
            output["dominanceFrontiers"] = {label:list(setVal) for label,setVal in dominanceFrontiers[funcName].items()}
            
            json.dump(output,jsonFile)
    # visualiseGraph(CFG["main"])
    with open("intermediateOutput/ir2Files.json","w") as file:
        json.dump(filesList,file)

def generateIR(content):
    addToBB = False
    for index,stm in enumerate(content):
        if stm["type"] == "define":
            currentFunction = stm["functionName"]
            functionData[currentFunction] = stm
            basicBlocks[currentFunction] = dict()
            CFG[currentFunction] = set()
            dominanceFrontiers[currentFunction] = dict()
            currentLabel = 0
            startIndex = index
            endIndex = index
            addToBB = True
        if addToBB:
            if stm["type"] in {"branch","branchConditional","label"}:
                if stm["type"] == "branch":
                    CFG[currentFunction].add((currentLabel,stm["label"]))
                    endIndex = index
                elif stm["type"] == "branchConditional":
                    CFG[currentFunction].add((currentLabel,stm["labelTrue"]))
                    CFG[currentFunction].add((currentLabel,stm["labelFalse"]))
                    endIndex = index
                elif stm["type"] == "label":
                    currentLabel = stm["labelNumber"]
                    endIndex = index - 1
                basicBlocks[currentFunction][currentLabel] = (startIndex,endIndex)
                startIndex = index
            elif stm["type"] == "return":
                basicBlocks[currentFunction][currentLabel] = (startIndex,index)
    
def generateDominanceFrontiers():
    for funcName,cfg in CFG.items():
        # step 1: Build Dominator Sets
        dominators = computeDominators(cfg, 0)
        # Step 2: Build Dominator Tree and Immediate Dominators
        dom_tree, idom = buildDomTree(dominators, 0)
        # Step 3: Compute Dominance Frontiers
        
        if computeDomFrontiers(cfg,idom) == computeDomFrontiers1(cfg,idom):
            df = computeDomFrontiers(cfg, idom)
        else:
            raise Exception("Dominance Frontiers : Invalid")
        dominanceFrontiers[funcName] = df
        

def convertIRTOCFG():
    with open("intermediateOutput/output.stm.json","r") as jsonFile:
        content = json.load(jsonFile)
    generateIR(content)
    generateDominanceFrontiers()
    generateOutputFiles(content)    

def RunIRPass2():
    convertIRTOCFG()


