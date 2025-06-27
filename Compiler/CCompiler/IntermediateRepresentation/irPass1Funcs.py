from IntermediateRepresentation.miscFuncs import convertDecSpecToLLVM

def convertParameterList(parameterListAST):
    if parameterListAST["type"] != "parameterList":
        raise Exception("Input not a valid parameter list node")
    
    output = []
    
    for paramDec in parameterListAST["value"]:
        output.append(convertParameterDeclaration(paramDec))
        
    return output


def convertParameterDeclaration(paramDecAST):
    dataElement = {
        # "type":"parameter",
        "dataType":convertDecSpecToLLVM(paramDecAST["declarationSpecifiers"]),
        "value":convertDeclarator(paramDecAST["declarator"])
    }
    
    return dataElement

def convertDeclarator(declaratorAST):
    return declaratorAST