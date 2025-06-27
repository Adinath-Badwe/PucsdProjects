from optimisations.constantFolding import runConstantFolding
from optimisations.constantPropagation import runConstantPropagation
from optimisations.deadCodeElimination import runDeadCodeElimination
from optimisations.loopOptimisations import runLoopOptimisations

def RunOptimiser():
    hasOptimised = True
    
    while hasOptimised:
        hasOptimised = False
        runConstantFolding()
        hasOptimised = runConstantPropagation()
        
    # runDeadCodeElimination()
    # runLoopOptimisations()