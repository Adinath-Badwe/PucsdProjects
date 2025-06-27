from IntermediateRepresentation.convertASTToStraightLine import RunIRPass1
from IntermediateRepresentation.convertStraightLineToCFG import RunIRPass2
from IntermediateRepresentation.convertCFGToSSA import RunIRPass3

def RunIRConverter():
    RunIRPass1()
    RunIRPass2()
    RunIRPass3()