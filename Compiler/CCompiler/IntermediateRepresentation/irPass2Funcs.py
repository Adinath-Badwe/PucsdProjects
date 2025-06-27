import networkx as nx 
import matplotlib.pyplot as plt 
from icecream import ic as print

getSuccessors = lambda x,CFG: {j for (i,j) in CFG if i == x}
getPredecessors = lambda x,CFG: {j for (j,i) in CFG if i == x}

class GraphVisualization: 

    def __init__(self): 
        
        # visual is a list which stores all  
        # the set of edges that constitutes a 
        # graph 
        self.visual = [] 
        
    # addEdge function inputs the vertices of an 
    # edge and appends it to the visual list 
    def addEdge(self, a, b): 
        temp = [a, b] 
        self.visual.append(temp) 
        
    # In visualize function G is an object of 
    # class Graph given by networkx G.add_edges_from(visual) 
    # creates a graph with a given list 
    # nx.draw_networkx(G) - plots the graph 
    # plt.show() - displays the graph 
    def visualize(self): 
        G = nx.DiGraph()
        G.add_edges_from(self.visual)
        pos = nx.nx_agraph.graphviz_layout(G,prog="dot")
        # pos = nx.nx_agraph.graphviz_layout(G,prog="circo")

        nx.draw_networkx(G,with_labels=True,pos=pos)
        plt.show() 
        
G = GraphVisualization()

def visualiseGraph(graphSet):
    # Driver code 
    
    for x,y in graphSet:
        G.addEdge(x,y)
    
    G.visualize() 

def getNodesFromCFG(CFG):
    nodes = set()
    for x,y in CFG:
        nodes.add(x)
        nodes.add(y)
    
    return nodes

def computeDominators(cfg, start):
    nodes = getNodesFromCFG(cfg)
    dom = {n: set(nodes) for n in nodes}
    dom[start] = {start}

    changed = True
    while changed:
        changed = False
        for n in nodes:
            if n == start:
                continue
            preds = getPredecessors(n,cfg)
            if not preds:
                continue
            # new_dom = set.intersection(*(dom[p] for p in preds))
            new_dom = nodes
            for p in preds:
                new_dom = new_dom.intersection(dom[p])
            new_dom.add(n)
            if dom[n] != new_dom:
                dom[n] = new_dom
                changed = True
    return dom

def buildDomTree(dominators, start):
    idom = {}
    for b in dominators:
        if b == start:
            continue
        doms = dominators[b] - {b}
        # Immediate dominator is the one deepest in the dominator tree
        idom[b] = max(doms, key=lambda d: len(dominators[d]))
    tree = {n: [] for n in dominators}
    for b, d in idom.items():
        tree[d].append(b)
    return tree, idom

# def computeDomFrontiers(cfg, idom):
#     nodes = getNodesFromCFG(cfg)
#     df = {n: set() for n in nodes}
#     for n in nodes:
#         preds = getPredecessors(n,cfg)
#         if len(preds) >= 2:
#             for p in preds:
#                 runner = p
#                 while runner != idom.get(n) and runner is not None:
#                     df[runner].add(n)
#                     runner = idom.get(runner)
#     print(df)
#     return df

def generateBottomUpTraversal(idom,startNode):
    output = []
    
    myTree = getMyTree(idom)
    workList = [startNode]
    while workList:
        element = workList.pop()
        output.insert(0,element)
        
        children = myTree.get(element)
        if children:
            workList += children

    return output

def getMyTree(idom):
    output = dict()
    
    for x,y in idom.items():
        if not output.get(y):
            output[y] = []
        output[y].append(x)
    
    return output

def computeDomFrontiers(cfg, idom):
    nodes = generateBottomUpTraversal(idom,0)
    df = {n: set() for n in nodes}
    for n in nodes:
        preds = getPredecessors(n,cfg)
        if len(preds) >= 2:
            for p in preds:
                runner = p
                while runner != idom.get(n) and runner is not None:
                    df[runner].add(n)
                    runner = idom.get(runner)
    return df

def getChildrenDomTree(n,idom):
    myTree = getMyTree(idom)
    output = []
    children = myTree.get(n)
    workList = set()
    if children:
        workList = set(children)
    
    while workList:
        element = workList.pop()
        
        children = myTree.get(element)
        if children:
            worklist = workList.union(set(children))
        
        output.append(element)
    
    return output

def computeDomFrontiers1(cfg,idom):
    nodes = generateBottomUpTraversal(idom,0)
    df = {n: set() for n in nodes}
    
    for n in nodes:
        for succ in getSuccessors(n,cfg):
            if idom[succ] != n:
                df[n].add(succ)
        
        for child in getChildrenDomTree(n,idom):
            for y in df[child]:
                if idom[y] != n:
                    df[n].add(y)
    return df

# def computeDominanceFrontiersNaive(cfg):
#     startNode = 0
#     nodes = getNodesFromCFG(cfg)
#     df = {n:set() for n in nodes}
#     for node in nodes:
#         temp = nodes - {startNode}
#         workList = set()
#         removedNodes = set([y for (x,y) in cfg if x == node])
    
#     return df

# def generateDominanceFrontiers():
#     for funcName,data in CFG.items():
#         nodes[funcName] = set()
#         for x,y in data:
#             nodes[funcName].add(x)
#             nodes[funcName].add(y)
    
#         for node in nodes[funcName]:
#             newNodes = set({0})
#             for node1 in (nodes[funcName] - {node}):
#                 newNodes = newNodes.union(getSuccessors(node1,CFG[funcName]))
#             dominates = nodes[funcName] - newNodes
#             dominates.add(node)
            
#             # print(node,dominates)

#         print(constructDominatorTree(funcName))
#         # visualiseGraph(CFG[funcName])

# def constructDominatorTree(funcName):
#     # Step 1: Initialize the dominator sets
#     dominators = {}
#     startNode = 0
    
#     Cfg = CFG[funcName]
#     Nodes = nodes[funcName]
    
#     for node in Nodes:
#         dominators[node] = Nodes  # Initially, every node dominates all nodes
    
#     dominators[startNode] = {startNode}  # The start node only dominates itself

#     changed = True
#     while changed:
#         changed = False
#         # Step 2: Iteratively refine the dominator sets
#         for node in Nodes:
#             if node == startNode:
#                 continue
#             new_dominators = set(Nodes)  # Start with the entire set of nodes
#             for pred in getPredecessors(node,Cfg):
#                 new_dominators = new_dominators.intersection(dominators[pred])  # Intersect dominator sets
#             new_dominators.add(node)  # A node always dominates itself
#             if new_dominators != dominators[node]:
#                 dominators[node] = new_dominators
#                 changed = True
#             print(node,dominators[node])
#     # Step 3: Build the Dominator Tree
#     dominator_tree = {node: [] for node in Nodes}
#     for node, dom_set in dominators.items():
#         for other in dom_set:
#             if node != other:
#                 dominator_tree[other].append(node)
    
#     return dominator_tree