import json
from icecream import ic as print
from IntermediateRepresentation.irPass2Funcs import getPredecessors,getSuccessors

def getNestedLoops(naturalLoops):
    parents = dict()
    toEval = {loop["header"] for loop in naturalLoops}
    
    for naturalLoop in naturalLoops:
        header,preHeader,nodes = naturalLoop["header"],naturalLoop["preHeader"],naturalLoop["nodes"]
        parents[header] = set()
        for naturalLoop1 in naturalLoops:
            header1,preHeader1,nodes1 = naturalLoop1["header"],naturalLoop1["preHeader"],naturalLoop1["nodes"]
            if naturalLoop == naturalLoop1:
                continue
            if nodes.issubset(nodes1):
                parents[header].add(header1)

    return computeLoopAnalysisOrder(parents,toEval)

def computeLoopAnalysisOrder(nestedLoops,toEval):
    someStructure = {key:set() for key in nestedLoops}
    for key,value in nestedLoops.items():
        for parent in value:
            someStructure[parent].add(key)
            
    for parent,children in someStructure.items():
        childrenToRemove = set()
        for child in children:
            childrenToRemove.update(children.intersection(someStructure[child]))
        someStructure[parent] = sorted(children - childrenToRemove)
        toEval = toEval - children
    
    return someStructure,sorted(toEval)
    
def computeNaturalLoops(CFG,dominators,idom):
    naturalLoops = []
    backEdges = []
    for (x,y) in CFG:
        if y in dominators[str(x)]:
            backEdges.append((x,y))
    
    for (back,header) in backEdges:
        naturalLoop = dict()
        naturalLoop["header"] = header
        naturalLoop["nodes"] = getNodesinNaturalLoop(CFG,back,header)
        naturalLoop["backEdge"] = back
        predecessorsOfHead = getPredecessors(header,CFG)
        if idom[str(header)] in predecessorsOfHead: 
            naturalLoop["preHeader"] = idom[str(header)]
        
        naturalLoops.append(naturalLoop)
    
    return naturalLoops

def getNodesinNaturalLoop(CFG,back,header):
    loopNodes = {header}
    stack = [back]
    
    while stack:
        m = stack.pop()
        if m not in loopNodes:
            loopNodes.add(m)
            stack.extend(getPredecessors(m,CFG))
            
    return loopNodes
