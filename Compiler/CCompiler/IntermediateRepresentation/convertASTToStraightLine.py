import json
from icecream import ic as print
from IntermediateRepresentation.miscFuncs import convertDecSpecToLLVM
from IntermediateRepresentation.irPass1Funcs import *

labelNumber = 0
tempVarNumber = 0
nextRegister = 0

idVersion = dict()

def resetNextRegister():
    global nextRegister
    nextRegister = 0

def getRegisterFromId(identifier):
    return identifier

def getExpressionType(expressionType):
    return {"additiveExpression":"add","multiplicativeExpression":"mult","relationalExpression":"relational","logicalAndExpression":"logicalAnd","logicalOrExpression":"logicalOr","equalityExpression":"equality"}[expressionType]

def incrementIdVersion(identifier):
    if not idVersion.get(identifier):
        idVersion[identifier] = 0
    else:
        idVersion[identifier] += 1
        
    return idVersion[identifier]

def irBranchConditional(value,valueType,labelTrue,labelFalse):
    output = []
    
    dataElement = {
        "type":"branchConditional",
        "value":value,
        "valueType":valueType,
        "labelTrue":labelTrue,
        "labelFalse":labelFalse,
    }
    
    output.append(dataElement)
    return output

def irBranch(label):
    output = []
    
    dataElement = {
        "type":"branch",
        "label":label
    }
    output.append(dataElement)
    
    return output

def getLastUsedRegister():
    global nextRegister
    if nextRegister == 0:
        return None
    return nextRegister-1

def getTempVar():
    global tempVarNumber
    tempVarNumber += 1
    return tempVarNumber - 1

# def getLabelNumber():
#     global labelNumber
#     labelNumber += 1
#     return labelNumber - 1

def getNextRegister():
    global nextRegister
    nextRegister += 1
    return nextRegister - 1

def generateLabel() -> "dataElement":
    dataElement = {
        "type":"label",
        "labelNumber":getNextRegister()
    }
    return dataElement

def generateReturn(returnType,returnValue,valueType):
    dataElement = {
        "type":"return",
        "returnType":returnType,
        "value":returnValue,
        "valueType":valueType,
    }
    return dataElement


def generateDefine(functionDefinitionAST):
    dataElement = {
        "type":"define",
        "resultType":convertDecSpecToLLVM(functionDefinitionAST["declarationSpecifiers"]),
        "functionName":functionDefinitionAST["declarator"][0]["value"], 
    }
    
    if len(functionDefinitionAST["declarator"]) >= 2:
        dataElement["parameterList"] = convertParameterList(functionDefinitionAST["declarator"][1])
    
    return dataElement

def irWhileLoop(whileLoopAST):
    output = []
    
    expression = whileLoopAST["value"]["expression"]
    statement = whileLoopAST["value"]["statement"]
    
    # generate the nodes
    
    # generate label node
    labelNode = generateLabel()
    
    # generate and add the expression node
    exprNode = irExpression(expression)
    
    # generate true label node
    labelTrue = generateLabel()
    
    #generate the compound statement node
    cmpndStm = irCompoundStatement(statement["value"])
    
    # generate false label node
    labelFalse = generateLabel()
    
    # generate the conditional branch node
    value = exprNode["result"]
    valueType = exprNode["resultType"]
    condBranch = irBranchConditional(value,valueType,labelTrue["labelNumber"],labelFalse["labelNumber"])
    
    # add the nodes to statement list
    
    # add the the branch node
    output += irBranch(labelNode["labelNumber"])
    
    # add the expr label node
    output.append(labelNode)
    
    # add the expression node
    output += exprNode["statementList"]
    
    # add the conditional branch node
    output += condBranch
    
    # add the true label
    output.append(labelTrue)
    
    # add the compound statement node
    output += cmpndStm
    
    # add the branch to expr
    output += irBranch(labelNode["labelNumber"])
    
    # add the false label
    output.append(labelFalse)
    
    return output

def irTranslationUnit(translationUnitAST):
    output = []
    
    for externDec in translationUnitAST["value"]:
        output += irExternalDeclaration(externDec)
        
    return output

def irExternalDeclaration(externalDeclarationAST):
    output = []
    
    if externalDeclarationAST["value"]["type"] == "functionDefinition":
        
        output += irFunctionDefinition(externalDeclarationAST["value"])
    elif externalDeclarationAST["value"]["type"] == "declaration":
        output += irDeclaration(externalDeclarationAST["value"])
    
    return output

def irFunctionDefinition(functionDefinitionAST):
    resetNextRegister()
    output = []
    
    output.append(generateDefine(functionDefinitionAST))
    output.append(generateLabel())
    
    cmpndStm = irCompoundStatement(functionDefinitionAST["compoundStatement"])
    output += cmpndStm
    
    output.append(generateReturn(convertDecSpecToLLVM(functionDefinitionAST["declarationSpecifiers"]),0,"constant"))
    return output

def irCompoundStatement(compoundStatementAST):
    output = []
    if type(compoundStatementAST) == dict and compoundStatementAST["type"] == "compoundStatement":
        compoundStatementAST = compoundStatementAST["value"]
    for block in compoundStatementAST:
        if block["type"] == "declaration":
            temp = irDeclaration(block)
        else:
            temp = irStatement(block)
        output += temp
    return output

def irStatement(statementAST):
    output = []
    
    if statementAST["type"] == "expressionStatement":
        temp = irExpressionStatement(statementAST)["statementList"]
    elif statementAST["type"] == "compoundStatement":
        temp = irCompoundStatement(statementAST)
    elif statementAST["type"] == "selectionStatement":
        temp = irSelectionStatement(statementAST)
    elif statementAST["type"] == "iterationStatement":
        temp = irIterationStatement(statementAST)
    elif statementAST["type"] == "jumpStatement":
        temp = irJumpStatement(statementAST)
    else:
        raise Exception("Not a valid statement")
    output += temp
    return output

def irExpressionStatement(expressionStatementAST):
    output = dict()

    if expressionStatementAST.get("expression"):
        output = irExpression({"type":"expression","value":expressionStatementAST["expression"]})
    
    return output
    
def irExpression(expressionAST):
    output = dict()
    statementList = []
    
    expList = expressionAST["value"]
    for exp in expList:
        expressionData = irExpressionFunc(exp)
        statementList += expressionData["statementList"]
    
    output["statementList"] = statementList
    if statementList:
        lastExpr = statementList[-1]
        result = lastExpr["result"]
        resultType = lastExpr["resultType"]
        output["result"] = result
        output["resultType"] = resultType
        output["dataType"] = "i32"
    elif expList and (not statementList):
        output["result"] = expressionData["result"]
        output["resultType"] = expressionData["resultType"]
        output["dataType"] = "i32"
    
    return output

def irExpressionFunc(expressionAST):
    
    if expressionAST["type"] in {"additiveExpression","multiplicativeExpression","relationalExpression","logicalAndExpression","logicalOrExpression","equalityExpression"}:
        return irCommonExpression(expressionAST)
    elif expressionAST["type"] == "assignmentExpression":
        return irAssignExpression(expressionAST)
    elif expressionAST["type"] == "postfixExpression":
        return irPostfixExpression(expressionAST)
    elif expressionAST["type"] == "unaryExpression":
        return irUnaryExpression(expressionAST)
    else:
        return irPrimary(expressionAST)

def irCommonExpression(expressionAST):
    output = dict()
    statementList = []
    
    dataElement = {
        "operator":expressionAST["operator"],
    }
    
    left = irExpressionFunc(expressionAST["left"])
    statementList += left["statementList"]
    dataElement["left"] = left["result"]
    dataElement["leftType"] = left["resultType"]
    
    right = irExpressionFunc(expressionAST["right"])
    statementList += right["statementList"]
    dataElement["right"] = right["result"]
    dataElement["rightType"] = right["resultType"]
    
    dataElement["result"] = getNextRegister()
    dataElement["type"] = getExpressionType(expressionAST["type"])
    
    output["result"] = dataElement["result"]
    output["resultType"] = "register"
    dataElement["resultType"] = output["resultType"]
    
    statementList.append(dataElement)
    output["statementList"] = statementList
    
    return output

# DO NOT DELETE THIS
# def irAdditiveExpression(expressionAST):
#     output = dict()
#     statementList = []
    
#     dataElement = {
#         "operator":expressionAST["operator"],
#     }
    
#     left = irExpressionFunc(expressionAST["left"])
#     statementList += left["statementList"]
#     dataElement["left"] = left["result"]
#     dataElement["leftType"] = left["resultType"]
    
#     right = irExpressionFunc(expressionAST["right"])
#     statementList += right["statementList"]
#     dataElement["right"] = right["result"]
#     dataElement["rightType"] = right["resultType"]
    
#     dataElement["result"] = getNextRegister()
#     statementList.append(dataElement)
    
#     output["statementList"] = statementList
#     output["result"] = dataElement["result"]
#     output["resultType"] = "register"
    
#     return output

# DO NOT DELETE THIS
# def irMultiplicativeExpression(expressionAST):
#     output = dict()
#     statementList = []
    
#     dataElement = {
#         "operator":expressionAST["operator"],
#     }
    
#     left = irExpressionFunc(expressionAST["left"])
#     statementList += left["statementList"]
#     dataElement["left"] = left["result"]
#     dataElement["leftType"] = left["resultType"]
    
#     right = irExpressionFunc(expressionAST["right"])
#     statementList += right["statementList"]
#     dataElement["right"] = right["result"]
#     dataElement["rightType"] = right["resultType"]
    
#     dataElement["result"] = getNextRegister()
#     statementList.append(dataElement)
    
#     output["statementList"] = statementList
#     output["result"] = dataElement["result"]
#     output["resultType"] = "register"
    
#     return output

def irAssignExpression(expressionAST):
    output = dict()
    statementList = []

    dataElement = {
        "type":"assign"
    }

    # if target is an id
    if expressionAST["target"]["type"] == "id":
        dataElement["target"] = expressionAST["target"]["value"]
        dataElement["targetType"] = "identifier"
        dataElement["result"] = dataElement["target"]
        dataElement["resultType"] = "identifier"
    # if target is a unary expression
    elif expressionAST["target"]["type"] == "unaryExpression":
        #doSomething
        raise Exception("Unary lvalue not implemented")
    else:
        raise Exception("Invalid Assignment")

    exprData = irExpressionFunc(expressionAST["assignedValue"])
    
    # dataElement["value"] = dict([(key,value) for key,value in exprData.items() if key in {"result","resultType"}])
    dataElement["assignedValue"] = exprData["result"]
    dataElement["assignedValueType"] = exprData["resultType"]
    
    statementList+= exprData["statementList"]
    
    output["statementList"] = statementList
    output["statementList"].append(dataElement)
    return output

def irPostfixExpression(expressionAST):
    output = dict()
    statementList = []
    result = None

    dataElement = {
        "type":"postfix"
    }

    if len(expressionAST["postfixList"]) == 1:
        postFix = expressionAST["postfixList"][0]
        postfixUse = postFix["use"]
        if postfixUse == "funcCall":
            dataElement["use"] = "funcCall"
            dataElement["resultType"] = "register"
            dataElement["funcName"] = expressionAST["primary"]["value"]
            
            value = postFix.get("value")
            
            if value:
                argumentExpressionList = value["value"]
            if value:
                argumentResultList = []
                for argumentExpression in argumentExpressionList:
                    expressionData = irExpressionFunc(argumentExpression)
                    statementList.extend(expressionData["statementList"])
                    argumentResult = {
                        "result":expressionData["result"],
                        "resultType":expressionData["resultType"]
                        }
                    argumentResultList.append(argumentResult)
                    
                dataElement["argumentList"] = argumentResultList
    else:
        raise Exception("Postfix Expression : More than one element in postfix list not yet supported")

    output["result"] = getNextRegister()
    dataElement["result"] = output["result"]

    statementList.append(dataElement)
    output["resultType"] = "register"
    output["statementList"] = statementList
    return output

# def irRelationalExpression(expressionAST):
#     output = []

#     return output

def irUnaryExpression(expressionAST):
    output = []

    return output

def irPrimary(expressionAST):
    output = dict()
    statementList = []
    
    if expressionAST["type"] == "id":
        output["result"] = getRegisterFromId(expressionAST["value"])
        output["dataType"] = "i32"
        output["resultType"] = "identifier"
    elif expressionAST["type"] == "constant":
        output["result"] = getRegisterFromId(expressionAST["value"])
        output["dataType"] = "i32"
        output["resultType"] = "constant"
    elif expressionAST["type"] == "expression":
        # output["result"] = getRegisterFromId(expressionAST["value"])
        # output["dataType"] = "i32"
        # output["resultType"] = "constant"
        raise Exception("Expressions within parentheses currently unimplemented")
    else:
        raise Exception("Not a valid primary expression",expressionAST)
    output["statementList"] = statementList
    return output


def irSelectionStatement(selectionStatementAST):
    output = []
    
    expression = selectionStatementAST["expression"]
    trueStatement = selectionStatementAST["trueStatement"]
    falseStatement = None
    if selectionStatementAST.get("falseStatement"):
        falseStatement = selectionStatementAST["falseStatement"]
    
    # # generate the nodes
    
    # # generate label node
    labelNode = generateLabel()
    
    # # generate and add the expression node
    exprNode = irExpression(expression)
    
    # # generate true label node
    labelTrue = generateLabel()
    
    # # generate the true compound statement node
    trueStm = irCompoundStatement(trueStatement["value"])
    
    # # check if else statement exists
    if falseStatement:
        labelElse = generateLabel()
        falseStm = irCompoundStatement(falseStatement["value"])
        
    # # generate false label node
    labelFalse = generateLabel()
    
    # # generate the conditional branch node
    value = exprNode["result"]
    valueType = exprNode["resultType"]
    
    if falseStatement:
        condBranch = irBranchConditional(value,valueType,labelTrue["labelNumber"],labelElse["labelNumber"])
    else:
        condBranch = irBranchConditional(value,valueType,labelTrue["labelNumber"],labelFalse["labelNumber"])
    
    # # add the nodes to statement list
    
    # # add the the branch node
    output += irBranch(labelNode["labelNumber"])
    
    # # add the expr label node
    output.append(labelNode)
    
    # # add the expression node
    output += exprNode["statementList"]
    
    # # add the conditional branch node
    output += condBranch
    
    # # add the true label
    output.append(labelTrue)
    
    # # add the compound statement node
    output += trueStm
    
    # # add the branch to expr
    output += irBranch(labelFalse["labelNumber"])
    
    # # add the false compound statement if it exists
    if falseStatement:
        # add the else label
        output.append(labelElse)
        
        # add the else statement
        output += falseStm

        # add the final branch
        output += irBranch(labelFalse["labelNumber"])

    # # add the false label
    output.append(labelFalse)

    return output

def irIterationStatement(iterationStatementAST):
    output = []
    
    if iterationStatementAST["value"]["type"] == 'whileLoop':
        output += irWhileLoop(iterationStatementAST)
    
    return output

def irJumpStatement(jumpStatementAST):
    output = []
    
    tempExpression = irExpression(jumpStatementAST["value"])
    output.extend(tempExpression["statementList"])
    output.append(generateReturn(tempExpression["dataType"],tempExpression["result"],tempExpression["resultType"]))
    
    return output

def irDeclaration(declarationAST):
    output = []
    
    return output

def generateIR(AST):
    output = []
    
    output += irTranslationUnit(AST)
    
    return output

def convertASTToIR():
    
    with open("intermediateOutput/output.json","r") as jsonFile:
        content = json.load(jsonFile)
    output = generateIR(content)
    with open("intermediateOutput/output.stm.json","w") as outputFile:
        json.dump(output,outputFile)

def RunIRPass1():
    convertASTToIR()
    