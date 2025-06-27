from icecream import ic as print
from IntermediateRepresentation.miscFuncs import convertDecSpecToLLVM

def convertFuncDefToBasicBlock(functionDefAST,currentScope):
    compoundStatement = functionDefAST["compoundStatement"]
    parameterListList = functionDefAST["declarator"][1:]

    declarationList = []

    for parameterList in parameterListList:
        if parameterList:
            for index,parameter in enumerate(parameterList["value"]):
                # declaration = convertParameterToDeclaration(parameter,index)
                parameter["paramNum"] = index
                parameter["paramDest"] = index + len(parameterList["value"])
                declarationList.append(parameter)
    return declarationList + compoundStatement

def convertParameterToDeclaration(parameterAST,index):
    decSpec = parameterAST["declarationSpecifiers"]
    declarator = parameterAST["declarator"]

    outputDict = {
        "type":"declaration",
        "declarationSpecifiers":{"type":"declarationSpecifiers","value":decSpec},
        "initDeclaratorList":[
            {
                "declarator":{"type":"declarator","value":declarator},
                "initializer":{
                    "type":"parameter",
                    "value":str(index),
                },
                "type":"initDeclarator"
            }
        ],
    }
    # currentScope.addVariableRegister(str(index),convertDecSpecToLLVM(decSpec),index)
    
    return outputDict

def convertForLoopToWhileLoop(forLoopAST):
    statement = {
        "type":"compoundStatement",
        "value":[forLoopAST["statement"]]
    } 
    if forLoopAST["conditional"]["expr"]:
        expressionStatement = {
            "type":"expressionStatement",
            "value":[
                forLoopAST["conditional"]["expr"]
            ]
        }
        statement["value"].append(expressionStatement)

    outputAST = {
                    "type": "compoundStatement",
                    "value": [
                        forLoopAST["conditional"]["first"],
                     {
                        "type": "iterationStatement",
                        "value": {
                            "type": "whileLoop",
                            "statement": statement # statement followed by expr3 goes here
                            ,
                            "expression": forLoopAST["conditional"]["exprStm"] # expr2
                        }
                    }]
                }

    return outputAST

def isTypeCompatible(leftType,rightType):
    typeCompatDict = {
        "int":{"float"},
        "float":{"int"}
    }
    convertToOneType(leftType)
    convertToOneType(rightType)
    return (convertToOneType(leftType) == convertToOneType(rightType)) or (convertToOneType(rightType) in typeCompatDict[convertToOneType(leftType)])

def convertToOneType(dataType):
    return dataType[0]