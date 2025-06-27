# from backEnd.ins
from IntermediateRepresentation.SSAElimination import RunIRPass4
from IntermediateRepresentation.convertToPseudoAarch64 import RunIRPass5
from backEnd.instructionSelection import RunInstructionSelection
from backEnd.registerAllocation import RunRegisterAllocation
from IntermediateRepresentation.convertToAssembly import RunIRPass6

def RunBackend():
    RunIRPass4()
    RunInstructionSelection()
    RunRegisterAllocation()
    RunIRPass5()
    RunIRPass6()