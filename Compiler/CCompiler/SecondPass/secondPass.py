import json
from icecream import ic as print
from SecondPass.secondPassFuncs import isTypeCompatible,convertDecSpecToLLVM,convertToOneType
# from secondPassFuncs import convertFuncDefToBasicBlock


functions = dict()

class Scope:
    def __init__(self, parent=None):
        if parent is None:
            self.parent = None
        else:
            self.parent = parent
        self.variables = dict()
        self.children = list()
        self.passNextChild = None

    def newScope(self):
        newScope1 = Scope(self)

        if self.passNextChild:
            newScope1.variables = self.passNextChild
        self.passNextChild = None
        
        return newScope1

    def endScope(self):
        if self.parent is None:
            return None
        self.parent.children.append(
            {"variables": self.variables, "children": self.children}
        )
        return self.parent

    def returnAllData(self):
        return {"variables": self.variables, "children": self.children}

    def passToChild(self,variables):
        self.passNextChild = variables
        self.variables = dict()
# functions


def addFunction(name, data):
    global functions
    if functions.get(name):
        raise Exception(f"Function already exists : {name}")
    functions[name] = data


def getFunction(name):
    global functions
    return functions.get(name)


# variables


def getVariable(name):
    global currentScope
    currScope = currentScope
    distance = 0
    while currScope:
        value = currScope.variables.get(name)
        if value:
            return (value, distance)
        currScope = currScope.parent
        distance += 1
    return None

def modifyVariable(name, key, distance, value):
    global currentScope
    currScope = currentScope
    for i in range(distance):
        currScope = currScope.parent
    currScope.variables[name][key] = value


def addVariable(name, data=None):
    global currentScope
    getData = getVariable(name)
    if getData and getData[1] == 0:
        raise Exception(f"Variable Already Defined : {name}")

    if not data:
        data = {"init": False}

    currentScope.variables[name] = data


globalScope = Scope()
currentScope = globalScope


def secondPass(content):
    if not content:
        raise Exception("VALID JSON NOT GENERATED")
    else:
        for i in content["value"]:
            checkExternalDeclaration(i)

def checkExternalDeclaration(externalDeclaration):
    if externalDeclaration["value"]["type"] == "functionDefinition":
        checkFunctionDefinition(externalDeclaration["value"])
    if externalDeclaration["value"]["type"] == "declaration":
        checkDeclaration(externalDeclaration["value"])


def checkFunctionDefinition(functionDefinition):
    global currentScope
    funcData = dict()

    declarator = functionDefinition["declarator"]
    funcData["declarator"] = declarator
    funcData["decSpec"] = functionDefinition["declarationSpecifiers"]
    funcData["declarationList"] = functionDefinition.get("declarationList")
    name = declarator[0]["value"]
    addFunction(name, funcData)

    if len(declarator) > 1:
        parameterList = declarator[1]
        checkParameterList(parameterList)
        
    currentScope.passToChild(currentScope.variables)

    checkCompoundStatement(
        {"type": "compoundStatement", "value": functionDefinition["compoundStatement"]}
    )

def checkDeclarator(directDeclaratorList, drefCount=None):
    outputList = []

    # for dec in directDeclaratorList:
    #     if dec:
    #         outputList.append(checkDirectDeclarator(dec,drefCount=drefCount))

    outputList += checkDirectDeclarator(directDeclaratorList,drefCount)

    return outputList


def checkCompoundStatement(compoundStatement):
    global currentScope
    currentScope = currentScope.newScope()
    
    for block in compoundStatement["value"]:
        checkBlock(block)

    currentScope = currentScope.endScope()


def checkBlock(block):
    if block["type"] == "declaration":
        checkDeclaration(block)
    if block["type"] == "compoundStatement":
        checkCompoundStatement(block)
    if block["type"] == "expressionStatement":
        checkExpressionStatement(block)
    if block['type'] == "selectionStatement":
        checkSelectionStatement(block)
    if block['type'] == "iterationStatement":
        checkIterationStatement(block)

def checkSelectionStatement(block):
    checkExpression(block["expression"]["value"])
    checkBlock(block["trueStatement"])
    
    if block.get("falseStatement"):
        checkBlock(block["falseStatement"])

def checkIterationStatement(iterationStatement):
    if iterationStatement["value"]["type"] == "whileLoop":
        checkWhileLoop(iterationStatement["value"])

def checkWhileLoop(whileLoopAST):
    checkExpression(whileLoopAST["expression"]["value"])
    checkCompoundStatement(whileLoopAST["statement"])

def checkExpressionStatement(expressionStatement):
    if expressionStatement.get("expression"):
        checkExpression(expressionStatement["expression"])

def checkExpression(expressionList):
    for exp in expressionList:
        exprType = checkExpressionAll(exp)
    return exprType

def checkExpressionAll(expression):
    if not expression:
        return None

    exprType = None
    if expression["type"] == "assignmentExpression":
        exprType = checkAssignmentExpression(expression)
    elif expression["type"] == "unaryExpression":
        exprType = checkUnaryExpression(expression)["exprType"]
    elif expression["type"] == "additiveExpression":
        exprType = checkAdditiveExpression(expression)
    elif expression["type"] == "multiplicativeExpression":
        exprType = checkMultiplicativeExpression(expression)
    elif expression["type"] == "relationalExpression":
        exprType = checkRelationalExpression(expression)
    elif expression["type"] == "postfixExpression":
        exprType = checkPostFixExpression(expression)
    elif expression["type"] == "id":
        data = getVariable(expression["value"])
        if not data:
            raise Exception(f"Variable not declared : {expression['value']}")
        data = data[0]
        exprType = data["decSpec"]
    elif expression["type"] == "constant":
        exprType = [expression["valType"]]
    elif expression["type"] == "expression":
        exprType = checkExpression(expression["value"])
    return exprType


def checkPostFixExpression(expression):
    global functions
    if expression["primary"]["type"] == "id":
        funcData = functions[expression["primary"]["value"]]
        exprType = [convertToOneType(funcData["decSpec"])["value"]]
    else:
        raise Exception("Postfix Expression : This primary expression type not supported :",expression["primary"])
    
    return exprType

def checkUnaryExpression(unaryExpression):
    exprType = None
    
    outputDict = {
        "exprType":None,
        "drefCount":0
    }
    
    if unaryExpression.get("castExpr"):
        tempDict = checkCastExpression(unaryExpression["castExpr"])
        exprType = tempDict["exprType"]
        drefCount = tempDict["drefCount"]
        operator = unaryExpression["operator"]
        
    if operator == "&":
        drefCount += 1
    if operator == "*":
        drefCount -= 1
    if drefCount < 0:
        raise Exception("Dereference Error : Invalid number of dereferences")
    
    outputDict["drefCount"] = drefCount
    outputDict["exprType"] = exprType
    
    return outputDict


def checkCastExpression(castExpression):
    exprType = None
    outputDict = {
        "exprType":None,
        "drefCount":0
    }

    if castExpression["type"] == "unaryExpression":
        return checkUnaryExpression(castExpression)    
    elif castExpression["type"] == "id":
        exprType = getVariable(castExpression["value"])[0]["decSpec"]
        drefCount = getVariable(castExpression["value"])[0].get("drefCount")
        if not drefCount:
            drefCount = 0
        outputDict["drefCount"] = drefCount
        outputDict["exprType"] = exprType
        return outputDict
    raise Exception("Cast Expression : Currently only identifiers can be cast")

def checkAdditiveExpression(additiveExpression):
    leftType = checkExpressionAll(additiveExpression["left"])
    rightType = checkExpressionAll(additiveExpression["right"])

    if not isTypeCompatible(leftType,rightType):
        raise Exception("Addition : Operands are not of the same type")
    return leftType


def checkMultiplicativeExpression(multiplicativeExpression):
    leftType = checkExpressionAll(multiplicativeExpression["left"])
    rightType = checkExpressionAll(multiplicativeExpression["right"])
    if not isTypeCompatible(leftType,rightType):
        raise Exception("Multiplication : Operands are not of the same type")

    return leftType

def checkRelationalExpression(relationalExpression):
    leftType = checkExpressionAll(relationalExpression["left"])
    rightType = checkExpressionAll(relationalExpression["right"])

    if not isTypeCompatible(leftType,rightType):
        raise Exception("Multiplication : Operands are not of the same type")

    return leftType

def checkAssignmentExpression(assignmentExpression):
    global currentScope
    unary = assignmentExpression["target"]
    assign = assignmentExpression["assignedValue"]

    exprType = None
    assignType = checkExpressionAll(assign)

    if unary["type"] == "id":
        getData = getVariable(unary["value"])
        if not getData:
            raise Exception(f"Variable not declared : {unary['value']}")
        data, distance = getData
        # modifyVariable(unary["value"], "value", distance, assign)
        exprType = data["decSpec"]
    elif unary["type"] == "unaryExpression":
        exprType = checkCastExpression(unary)["exprType"]
    
    if exprType != assignType:
        raise Exception(
            f"Assignment : Operands are not of the same type : {exprType} and {assignType}"
        )

    return exprType


def checkDeclaration(declaration):
    global currentScope
    decSpec = declaration["declarationSpecifiers"]
    initDecList = declaration.get("initDeclaratorList")

    decSpecData = checkDeclarationSpecifiers(decSpec)
    nameList = checkInitDecList(initDecList)
    for nameType in nameList:
        name, exprType = nameType
        data, distance = getVariable(name)
        # if exprType and exprType != decSpecData:
        if exprType and not isTypeCompatible(exprType,decSpecData):
            raise Exception(f"Not of the same type {exprType} and {decSpecData}")
        modifyVariable(name, "decSpec", distance, decSpecData)
        modifyVariable(name, "init", distance, True)
        # print(name,getVariable(name))

def checkDeclarationSpecifiers(decSpec):
    output = []
    values = decSpec["value"]

    for value in values:
        if value["type"] == "typeSpecifier":
            output.append(value["value"])
    return output

def checkInitDecList(initDecList):
    nameList = []
    for initDeclarator in initDecList:
        nameList.append(checkInitDeclarator(initDeclarator))
    return nameList


def checkInitDeclarator(initDeclarator):
    declarator = initDeclarator["declarator"]
    initializer = initDeclarator.get("initializer")

    exprType = None

    if initializer:
        exprType = checkInitializer(initializer)

    drefCount = declarator.get("drefCount")
    decOutput = checkDeclarator(declarator["value"],drefCount=drefCount)

    # name = checkDirectDeclarator(declarator["value"],initializer,drefCount)
    # Do not delete this --^

    name = decOutput[0]
    return (name, exprType)


def checkInitializer(initializer):
    exprType = checkExpressionAll(initializer)
    return exprType

# def checkDirectDeclarator(directDeclarator, extraData=None, drefCount=None):
#     global currentScope

#     print(directDeclarator)
#     output = None
#     if directDeclarator["type"] == "id":
#         addVariable(directDeclarator["value"],)
#         modifyVariable(directDeclarator["value"],"drefCount",0,drefCount)
#         output = directDeclarator["value"]
#     elif directDeclarator["type"] == "parameterList":
#         checkParameterList(directDeclarator)
#     elif directDeclarator["type"] == "squareBrackets":
#         pass
#     else:
#         raise Exception("DirectDeclarator : Functionality not yet implemented")

#     return output

# for dec in directDeclaratorList:
#     if dec:
#         outputList.append(checkDirectDeclarator(dec,drefCount=drefCount))

def checkDirectDeclarator(directDeclaratorList, extraData=None, drefCount=None):
    global currentScope

    outputList = []
    
    # print(directDeclaratorList)
    output = None
    
    if directDeclaratorList:
        identifier = directDeclaratorList[0]

        if identifier["type"] == 'id':
            addVariable(identifier["value"],)
            modifyVariable(identifier["value"],"drefCount",0,drefCount)
            outputList.append(identifier["value"])
        else:
            raise Exception("DirectDeclarator : Currently only identifier implemented")
        
        dataList = []
        for index,dec in enumerate(directDeclaratorList):
            if index == 0:
                continue
            dataElement = dec
            if dec["type"] == "squareBrackets":
                dataElement["dataType"] = checkExpressionAll(dec["expression"])
            dataList.append(dataElement)
        modifyVariable(identifier["value"],"extraData",0,dataList)

    # for dec in directDeclaratorList:
    #     if not dec:
    #         continue
    #     if dec["type"] == "id":
    #         addVariable(dec["value"],)
    #         modifyVariable(dec["value"],"drefCount",0,drefCount)
    #         outputList.append(dec["value"])
    #     elif dec["type"] == "parameterList":
    #         checkParameterList(dec)
    #     elif dec["type"] == "squareBrackets":
    #         pass
    #     else:
    #         raise Exception("DirectDeclarator : Functionality not yet implemented")

    return outputList


def checkParameterList(parameterList):
    outputList = []
    if parameterList:
        for parameter in parameterList["value"]:
            outputList.append(checkParameter(parameter))

    return outputList

def checkParameter(parameter):
    decSpec = parameter["declarationSpecifiers"]
    declarator = parameter["declarator"]

    name = declarator[0]["value"]

    decSpecData = checkDeclarationSpecifiers({"value": decSpec})
    addVariable(name, {"decSpec":decSpecData})

def RunSecondPass():
    with open("intermediateOutput/output.json", "r") as jsonFile:
        content = json.load(jsonFile)
        
    secondPass(content)
    
    allData = {"functions": functions, "scope": currentScope.returnAllData()}
    with open("intermediateOutput/allData.json", "w") as jsonFile:
        json.dump(allData, jsonFile)
    