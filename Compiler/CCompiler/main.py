from Parser.Cparser1 import RunParser
from SecondPass.secondPass import RunSecondPass
from IntermediateRepresentation import RunIRConverter
from optimisations import RunOptimiser
from backEnd import RunBackend

if __name__ == "__main__":
    RunParser()
    RunSecondPass()
    RunIRConverter()
    RunOptimiser()
    RunBackend()