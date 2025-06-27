import json
from icecream import ic as print
from SecondPass.secondPassFuncs import convertFuncDefToBasicBlock
from IntermediateRepresentation.miscFuncs import convertDecSpecToLLVM,convertTypeToLLVM


alignChart = {
    "i32": 4,
    "i8": 1,
    "float": 4,
    "ptr": 8,
}


class ScopeHandler:

    functions = dict()

    def __init__(
        self,
        nextScopeNumber=None,
        parent=None,
        children=None,
        variables=None,
        registerMapping=None,
        functions1=None
    ):
        if nextScopeNumber is None:
            nextScopeNumber = 0
        if registerMapping is None:
            registerMapping = dict()

        self.parent = parent
        self.nextScopeNumber = nextScopeNumber
        self.children = children
        self.variables = variables
        self.registerMapping = registerMapping
        if functions1:
            ScopeHandler.functions = functions1

    def enterScope(self):
        return self.children[self.nextScopeNumber]

    def exitScope(self):
        if self.parent is None:
            raise Exception("Cannot Exit Scope. Already at global level.")
        self.parent.incrementScopeNumber()
        return self.parent

    def incrementScopeNumber(self):
        self.nextScopeNumber += 1

    def generateRegisterMapping(self, nextRegister):
        self.registerMapping = dict()
        outputStr = ""
        for name, data in self.variables.items():
            self.registerMapping[name] = (
                nextRegister,
                convertTypeToLLVM(data["decSpec"][0]),
            )
            allocType = convertTypeToLLVM(data["decSpec"][0])
            if data.get("drefCount"):
                allocType = "ptr"
            tempDict = irAlloca(allocType, nextRegister)
            nextRegister = tempDict["nextRegister"]
            outputStr += tempDict["outputStr"]

        # for child in self.children:
        #     tempDict = child.generateRegisterMapping(nextRegister)
        #     nextRegister= tempDict["nextRegister"]
        #     outputStr += tempDict["outputStr"]

        return {"nextRegister": nextRegister, "outputStr": outputStr}

    def addVariableRegister(self, varName, varType, destRegister):
        self.registerMapping[varName] = (destRegister, varType)

    def getVariableRegister(self, varName):
        current = self
        output = None
        while current:
            if current.registerMapping.get(varName):
                output = current.registerMapping.get(varName)
                break
            current = current.parent
        return output


def irAlloca(allocType, nextRegister):
    outputStr = ""
    result = ""

    outputStr = (
        f"\t%{nextRegister} = alloca {allocType}, align {alignChart[allocType]}\n"
    )
    result = "%" + str(nextRegister)
    nextRegister += 1

    outputDict = {
        "nextRegister": nextRegister,
        "outputStr": outputStr,
        "result": result,
    }

    return outputDict


def irStore(allocType, storeLoc, loadLoc):
    outputStr = ""
    result = ""

    outputStr = f"\tstore {allocType} {loadLoc}, ptr {storeLoc}, align {alignChart[allocType]}\n"

    outputDict = {"outputStr": outputStr, "result": storeLoc}

    return outputDict


def irLoad(allocType, storeLoc, loadLoc):
    outputStr = ""
    result = ""

    outputStr = f"\t{storeLoc} = load {allocType}, ptr {loadLoc}, align {alignChart[allocType]}\n"

    outputDict = {"outputStr": outputStr, "result": storeLoc}

    return outputDict

def generateScope():
    with open("allData.json", "r") as jsonFile:
        content = json.load(jsonFile)
    
    globalScope = ScopeHandler(functions1=content["functions"])
    globalScope = generateScopeFunc(content["scope"], globalScope)

    return globalScope


def generateScopeFunc(content, currentScope):
    variables = content["variables"]
    children = []

    for child in content["children"]:
        childScope = ScopeHandler(parent=currentScope)
        childScope = generateScopeFunc(child, childScope)
        children.append(childScope)

    currentScope.variables = variables
    currentScope.children = children

    return currentScope

def initScope():
    globalScope = generateScope()
    currentScope = globalScope
    currentFunction = None

def generateFunctionAttributes(funcAttributes):
    return funcAttributes


def irExpression(expressionAST, nextRegister):
    if expressionAST["type"] == "additiveExpression":
        return irAdditiveExpression(expressionAST, nextRegister)
    elif expressionAST["type"] == "multiplicativeExpression":
        return irMultiplicativeExpression(expressionAST, nextRegister)
    elif expressionAST["type"] == "assignmentExpression":
        return irAssignExpression(expressionAST, nextRegister)
    elif expressionAST["type"] == "postfixExpression":
        return irPostfixExpression(expressionAST, nextRegister)
    elif expressionAST["type"] == "relationalExpression":
        return irRelationalExpression(expressionAST, nextRegister)
    elif expressionAST["type"] == "unaryExpression":
        return irUnaryExpression(expressionAST, nextRegister)
    else:
        return irPrimary(expressionAST, nextRegister)

def irUnaryExpression(unaryExpressionAST, nextRegister):
    outputDict = dict()
    outputStr = ""
    result = None
    resultType = None

    if unaryExpressionAST.get("castExpr"):
        tempDict = irUnaryExpressionDref(unaryExpressionAST,nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]
        result = tempDict["result"]
        resultType = tempDict["resultType"]
    else:
        tempDict = irExpression(unaryExpressionAST,nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]
        result = tempDict["result"]
        resultType = tempDict["resultType"]
        
    outputDict["outputStr"] = outputStr
    outputDict["nextRegister"] = nextRegister
    outputDict["result"] = result
    outputDict["resultType"] = resultType

    return outputDict

def irUnaryExpressionDref(unaryExpressionAST,nextRegister):
    
    outputDict = dict()
    outputStr = ""
    result = None
    resultType = None
    
    castExpr = unaryExpressionAST["castExpr"]
    tempDict = irUnaryExpression(castExpr,nextRegister)
    nextRegister = tempDict["nextRegister"]
    outputStr += tempDict["outputStr"]
    result = tempDict["result"]
    resultType = tempDict["resultType"]
    operator = unaryExpressionAST["operator"]
    
    if operator == "*":
        # print(result)
        pass
    elif operator == "&":
        # print(result)
        pass
    else:
        raise Exception("UnaryExpression : Invalid unary operator")

    outputDict["outputStr"] = outputStr
    outputDict["nextRegister"] = nextRegister
    outputDict["result"] = result
    outputDict["resultType"] = resultType

    return outputDict

def irRelationalExpression(relationalExpressionAST,nextRegister):
    outputDict = dict()
    outputStr = ""


    tempDict = irExpression(relationalExpressionAST["left"],nextRegister)
    outputStr += tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]
    leftResult = tempDict["result"]
    leftResultType = tempDict["resultType"]

    tempDict = irExpression(relationalExpressionAST["right"],nextRegister)
    outputStr += tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]
    rightResult = tempDict["result"]
    rightResultType = tempDict["resultType"]

    op = relationalExpressionAST["operator"]

    compareStr = f"\t%{nextRegister} = icmp "
    nextRegister += 1

    if op == "<":
        compareStr += "slt "
    elif op == ">":
        compareStr += "sgt "
    elif op == "<=":
        compareStr += "sle "
    elif op == ">=":
        compareStr += "sge "

    compareStr += f"{leftResultType} {leftResult}, {rightResult}\n"
    outputStr += compareStr
    outputStr += f"\t%{nextRegister} = zext i1 %{nextRegister-1} to i32\n"
    finalResult = f"%{nextRegister}"
    nextRegister += 1

    resultType = leftResultType

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = finalResult
    outputDict["resultType"] = resultType

    return outputDict

def irAdditiveExpression(additiveExpressionAST, nextRegister):

    outputDict = dict()
    outputStr = ""

    # this is for constant folding
    if additiveExpressionAST["left"]["type"] == additiveExpressionAST["right"]["type"] == "constant":
        if additiveExpressionAST["operator"] == "+":
            value = int(additiveExpressionAST["left"]["value"])+int(additiveExpressionAST["right"]["value"])
        if additiveExpressionAST["operator"] == "-":
            value = int(additiveExpressionAST["left"]["value"])-int(additiveExpressionAST["right"]["value"])
        outputDict["result"] = value
        outputDict["resultType"] = convertTypeToLLVM(additiveExpressionAST["left"]["valType"])
        return outputDict

    left = irExpression(additiveExpressionAST["left"], nextRegister)
    nextRegister = left["nextRegister"]
    outputStr += left["outputStr"]

    right = irExpression(additiveExpressionAST["right"], nextRegister)
    outputStr += right["outputStr"]
    nextRegister = right["nextRegister"]

    addOp = "add" if "+" == additiveExpressionAST["operator"] else "sub"
    result = "%" + str(nextRegister)
    flags = "nsw"

    resultType = left["resultType"]
    outputStr += f"\t%{nextRegister} = {addOp} {flags} {resultType} {left['result']}, {right['result']}\n"
    nextRegister += 1

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = result
    outputDict["resultType"] = resultType

    return outputDict


def irMultiplicativeExpression(multiplicativeExpressionAST, nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = {
        "outputStr":"",
        "nextRegister":nextRegister,
        "result":None,
        "resultType":None,
    }
    outputStr = ""

    if multiplicativeExpressionAST["left"]["type"] == multiplicativeExpressionAST["right"]["type"] == "constant" and multiplicativeExpressionAST["operator"] == "*":
        value = int(multiplicativeExpressionAST["left"]["value"])*int(multiplicativeExpressionAST["right"]["value"])
        outputDict["result"] = value
        outputDict["resultType"] = convertTypeToLLVM(multiplicativeExpressionAST["left"]["valType"])
        return outputDict

    left = irExpression(multiplicativeExpressionAST["left"], nextRegister)
    nextRegister = left["nextRegister"]
    outputStr += left["outputStr"]

    right = irExpression(multiplicativeExpressionAST["right"], nextRegister)
    outputStr += right["outputStr"]
    nextRegister = right["nextRegister"]

    mulOp = "mul" if "*" == multiplicativeExpressionAST["operator"] else "sdiv"
    result = "%" + str(nextRegister)
    flags = "nsw" if "*" == multiplicativeExpressionAST["operator"] else ""


    resultType = left["resultType"]
    outputStr += f"\t%{nextRegister} = {mulOp} {flags} {resultType} {left['result']}, {right['result']}\n"
    nextRegister += 1

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = result
    outputDict["resultType"] = resultType

    return outputDict


def irPrimary(primaryAST, nextRegister):
    outputDict = {
        "outputStr": None,
        "nextRegister": None,
        "result": None,
    }

    outputStr = ""
    result = None
    resultType = None
    if primaryAST["type"] == "id":
        regLoc = currentScope.getVariableRegister(primaryAST["value"])
        tempDict = irLoad(regLoc[1], f"%{nextRegister}", f"%{regLoc[0]}")

        outputStr += tempDict["outputStr"]
        resultType = regLoc[1]
        result = tempDict["result"]

        nextRegister += 1
        
    elif primaryAST["type"] == "constant":
        resultType = convertTypeToLLVM(primaryAST["valType"])
        result = primaryAST["value"]
    # elif primaryAST["type"] == "expression":
    #     output = irExpression(primaryAST["value"],nextRegister)
    #     outputStr = outputStr + output["outputStr"]
    #     nextRegister = output["nextRegister"]
    outputDict["resultType"] = resultType
    outputDict["outputStr"] = outputStr
    outputDict["nextRegister"] = nextRegister
    outputDict["result"] = result

    return outputDict

def constructFunctionDefinitionDict(inputDict, nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = dict()

    returnType = convertTypeToLLVM(inputDict["declarationSpecifiers"][0]["value"])
    functionName = inputDict["declarator"][0]["value"]

    argumentList = None
    if len(inputDict["declarator"]) >= 2:
        argumentList = inputDict["declarator"][1]

    compoundStatement = inputDict["compoundStatement"]

    outputDict["returnType"] = returnType
    outputDict["functionName"] = functionName
    outputDict["argumentList"] = modifyParameterDeclarationList(argumentList)
    outputDict["compoundStatement"] = compoundStatement
    outputDict["nextRegister"] = nextRegister

    return outputDict


def modifyParameterDeclarationList(argumentList):
    output = []
    if not argumentList:
        return []
    for parameter in argumentList["value"]:
        if parameter["type"] != "parameterDeclaration":
            raise Exception("Invalid Parameter :", parameter)
        output.append(
            (
                parameter["declarator"][0]["value"],
                parameter["declarationSpecifiers"][0]["value"],
            )
        )

    return output

def irFunctionDefinition(functionDefAST, nextRegister=None):
    global currentScope
    global currentFunction
    

    if nextRegister is None:
        nextRegister = 0  # start from 1 since %0 is the entry label

    outputDict = {
        "nextRegister": None,
        "outputStr": None,
    }

    outputStr = ""

    modifiedDict = constructFunctionDefinitionDict(functionDefAST, nextRegister)
    nextRegister = modifiedDict["nextRegister"]

    returnType = modifiedDict.get("returnType")
    functionName = modifiedDict.get("functionName")

    currentFunction =  currentScope.functions[functionName]
    currentFunction["llvmData"] = {
        "name":functionName,
        "returnType":returnType
    }
    argumentList = modifiedDict.get("argumentList")
    compoundStatement = modifiedDict.get("compoundStatement")
    returnValue = "0"

    outputStr += "define "
    outputStr += returnType + " "
    outputStr += "@" + functionName
    outputStr += "("

    outputStr += ",".join(
        [
            f"{convertTypeToLLVM(varType)} %{index+nextRegister}"
            for index, (varName, varType) in enumerate(argumentList)
        ]
    )
    nextRegister += len(argumentList)

    outputStr += ")" + " #0 " +"{\n"
    outputStr += f"entry:\n"
    
    # outputStr += f"%{nextRegister}:\n"
    # nextRegister += 1

    # for parameter in argumentList:
    #     tempDict = irAlloca(convertTypeToLLVM(parameter[1]), nextRegister)
    #     nextRegister = tempDict["nextRegister"]
    #     outputStr += tempDict["outputStr"]

    # for index, parameter in enumerate(argumentList):
    #     tempDict = irStore(
    #         convertTypeToLLVM(parameter[1]),
    #         f"%{(len(argumentList)+1+index)}",
    #         f"%{index}",
    #     )
    #     result = tempDict["result"]
    #     currentScope.addVariableRegister(
    #         parameter[0], convertTypeToLLVM(parameter[1]), result
    #     )
    #     outputStr += tempDict["outputStr"]

    convertedAST = convertFuncDefToBasicBlock(functionDefAST,currentScope)
    currentScope = currentScope.enterScope()
    # tempDict = irCompoundStatement(
    #     functionDefAST["compoundStatement"], nextRegister=nextRegister
    # )
    tempDict = irCompoundStatement(
        convertedAST, nextRegister=nextRegister
    )
    currentScope = currentScope.exitScope()

    outputStr += tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]

    if not currentFunction["llvmData"].get("explicitReturn"):
        outputStr += f"\tret {returnType} {returnValue}\n"

    outputStr += "}\n"
    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr


    currentFunction = None
    return outputDict


def irCompoundStatement(statementList, nextRegister=None):
    global currentScope
    if nextRegister is None:
        nextRegister = 0

    outputDict = {"nextRegister": None, "outputStr": None}

    outputStr = ""

    tempDict = currentScope.generateRegisterMapping(nextRegister)

    outputStr += tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]

    for block in statementList:
        if block["type"] == "declaration":
            tempDict = irDeclaration(block, nextRegister)
        elif block["type"] == "compoundStatement":
            currentScope = currentScope.enterScope()
            tempDict = irCompoundStatement(block["value"], nextRegister)
            currentScope = currentScope.exitScope()
        elif block["type"] == "expressionStatement":
            tempDict = irExpressionStatement(block["value"][0]["value"], nextRegister)
        elif block["type"] == "jumpStatement":
            tempDict = irJumpStatement(block,nextRegister)
        elif block["type"] == "iterationStatement":
            tempDict = irIterationStatement(block,nextRegister)
        elif block["type"] == "parameterDeclaration":
            tempDict = irParameterDeclaration(block,nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr

    return outputDict

def irFunctionCall(functionCallAST,nextRegister):
    outputDict = dict()
    outputStr = ""

    funcName = functionCallAST["funcName"]
    retType = convertDecSpecToLLVM(currentScope.functions[funcName]["decSpec"])
    parameters = functionCallAST["value"]["value"]

    tempDict = funcCallGenerateParameters(parameters,nextRegister)
    parameterStr = tempDict["parameterStr"]
    outputStr += tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]

    result = nextRegister
    outputStr += f"\t%{nextRegister} = call {retType} @{funcName}({parameterStr})\n"
    nextRegister += 1

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = f"%{result}"
    outputDict["resultType"] = retType

    return outputDict

def funcCallGenerateParameters(argumentExpressionList,nextRegister):
    outputDict = dict()
    outputStr = ""
    parameterStr = ""
    
    parameterList = []

    for argument in argumentExpressionList:
        tempDict = irExpression(argument,nextRegister)
        outputStr += tempDict["outputStr"]
        nextRegister = tempDict["nextRegister"]
        result = tempDict["result"]
        resultType = tempDict["resultType"]

        # tempDict = irLoad(regValue[1],f"%{nextRegister}",f"%{regValue[0]}")
        # tempDict = irLoad(resultType,f"%{nextRegister}",f"{result}")
        # nextRegister += 1
        # outputStr += tempDict["outputStr"]

        parameterList.append(f"{resultType} noundef {tempDict['result']}")

    parameterStr = ", ".join(parameterList)
    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["parameterStr"] = parameterStr
    return outputDict

def irIterationStatement(iterationStatementAST,nextRegister):
    if iterationStatementAST["value"]["type"] == "forLoop":
        return irForLoop(iterationStatementAST["value"],nextRegister)
    if iterationStatementAST["value"]["type"] == "whileLoop":
        return irWhileLoop(iterationStatementAST["value"],nextRegister)

def irWhileLoop(whileLoopAST,nextRegister):
    global currentScope
    outputDict = dict()
    outputStr = ""

    labelComparison = nextRegister
    labelTrue = None
    labelFalse = None
    outputStr += f"\tbr label %{nextRegister}\n\n"
    outputStr += f"{nextRegister}: ; comparison\n"
    nextRegister += 1

    expression = whileLoopAST["expression"]
    compoundStatement = whileLoopAST["statement"]

    tempDict = irExpression(expression["value"][0],nextRegister)
    exprStr = tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]
    resultType = tempDict["resultType"]
    result = tempDict["result"]
    if resultType != "i1":
        exprStr += f"\t%{nextRegister} = icmp ne {resultType} {result}, 0\n"
        result = "%"+str(nextRegister)
        nextRegister += 1

    labelTrue = nextRegister
    nextRegister += 1

    currentScope = currentScope.enterScope()
    tempDict = irCompoundStatement(compoundStatement["value"],nextRegister)
    currentScope = currentScope.exitScope()
    cmpStmStr = tempDict["outputStr"]
    nextRegister = tempDict["nextRegister"]
    labelFalse = nextRegister
    nextRegister += 1

    outputStr += exprStr

    outputStr += f"\tbr i1 {result}, label %{labelTrue}, label %{labelFalse}\n\n"
    outputStr += f"{labelTrue}: ; True\n"
    outputStr += cmpStmStr
    outputStr += f"\tbr label %{labelComparison}\n\n"
    outputStr += f"{labelFalse}:; False\n"

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    return outputDict


# this thing is not working 

# def irForLoop(forLoopAST,nextRegister):
    
#     outputDict = dict()
#     outputStr = ""

#     global currentScope

#     declaration = None
#     expression = None

#     if forLoopAST["conditional"]["first"]["type"] == "declaration":
#         declaration = forLoopAST["conditional"]["first"]
#     if forLoopAST["conditional"]["first"]["type"] == "expressionStatement":
#         expression = forLoopAST["conditional"]["first"]

#     branchTrue = forLoopAST["statement"]
#     comparisonStm = forLoopAST["conditional"]["exprStm"]
#     repeat = forLoopAST["conditional"]["expr"]

#     labelTrue = None
#     labelComparison = None
#     labelFalse = None
#     labelRepeat = None

#     if declaration:
#         tempDict = irDeclaration(declaration,nextRegister)
#         nextRegister = tempDict["nextRegister"]
#         outputStr += tempDict["outputStr"]
#     if expression:
#         tempDict = irExpressionStatement(expression["value"][0]["value"],nextRegister)
#         nextRegister = tempDict["nextRegister"]
#         outputStr += tempDict["outputStr"]
    
#     # intitialization and start
#     outputStr += f"\tbr label %{nextRegister}\n\n"

#     # comparison
#     labelComparison = nextRegister
#     nextRegister += 1
#     tempDict = irExpressionStatement(comparisonStm["value"][0]["value"],nextRegister) 
#     nextRegister = tempDict["nextRegister"]
#     comparisonStr = tempDict["outputStr"]
#     result = tempDict["result"]
#     comparisonResult = result

#     # branch True
#     labelTrue = nextRegister
#     nextRegister += 1

#     currentScope = currentScope.enterScope()
#     tempDict = irCompoundStatement(branchTrue["value"],nextRegister)
#     currentScope = currentScope.exitScope()

#     nextRegister = tempDict["nextRegister"]
#     branchTrueStr = tempDict["outputStr"]

#     # repeat (usually used for incrementing the iterator)
#     labelRepeat = nextRegister
#     nextRegister += 1
#     tempDict = irExpressionStatement(repeat["value"],nextRegister)
#     nextRegister = tempDict["nextRegister"]
#     repeatStr = tempDict["outputStr"]

#     resultType = "i32"
#     # branch end


#     outputStr += f"{labelComparison}: ; comparison \n"
#     outputStr += comparisonStr
#     outputStr += f"\tbr {resultType} {comparisonResult}, label %{labelTrue}, label %{nextRegister} \n\n"

#     outputStr += f"{labelTrue}: ; branch true \n"
#     outputStr += branchTrueStr
#     outputStr += f"\tbr label %{labelRepeat}\n\n"
#     outputStr += f"{labelRepeat}: ; repeat \n"
#     outputStr += repeatStr
#     outputStr += f"\tbr label %{labelComparison}\n\n"

#     outputStr += f"{nextRegister}: ; Branch False\n"
#     nextRegister += 1

#     outputDict["nextRegister"] = nextRegister
#     outputDict["outputStr"] = outputStr

#     return outputDict

def irParameterDeclaration(parameterAST,nextRegister):
    outputDict = dict()
    outputStr = ""

    tempDict = irStore(allocType=convertDecSpecToLLVM(parameterAST["declarationSpecifiers"]),storeLoc="%"+str(parameterAST["paramDest"]),loadLoc="%"+str(parameterAST["paramNum"]))
    outputStr += tempDict["outputStr"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr

    return outputDict

def irJumpStatement(jumpStatementAST,nextRegister = None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = dict()
    outputStr = ""

    jsType = jumpStatementAST["jumpType"]

    if jsType == "return":
        tempDict = irReturn(jumpStatementAST,nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr

    return outputDict


def irDeclaration(declarationAST, nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = {"nextRegister": None, "outputStr": None}
    outputStr = ""

    decSpec = declarationAST["declarationSpecifiers"]["value"]  # a list
    initDecList = declarationAST["initDeclaratorList"]  # a list

    someType = convertDecSpecToLLVM(decSpec)

    for initDec in initDecList:
        declarator = initDec["declarator"]
        initializer = initDec.get("initializer")

        # tempDict = irDeclarator(declarator,someType,nextRegister)
        # nextRegister = tempDict["nextRegister"]
        # result = tempDict["result"]
        # outputStr += tempDict["outputStr"]
        
        if initializer:
            storeLoc = currentScope.getVariableRegister(
                declarator["value"][0]["value"]
            )[0]
            tempDict = irInitializer(initializer, nextRegister, storeLoc)
            nextRegister = tempDict["nextRegister"]
            result = tempDict["result"]
            outputStr += tempDict["outputStr"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr

    return outputDict

def irDeclarator(declarator, allocType, nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = dict()
    outputStr = ""

    getRegister = currentScope.getVariableRegister(declarator["value"][0]["value"])
    tempDict = irAlloca(allocType, nextRegister)

    nextRegister = tempDict["nextRegister"]
    outputStr += tempDict["outputStr"]
    result = tempDict["result"]

    # tempDict = irLoad(allocType,result,"%"+str(getRegister[0]))
    tempDict = irStore(allocType, result, "%" + str(getRegister[0]))

    outputStr += tempDict["outputStr"]
    result = tempDict["result"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = getRegister[0]
    return outputDict

def irTranslationUnit(translationUnitAST):
    nextRegister = 0

    outputDict = {
        "nextRegister": None,
        "outputStr": None,
        "result": None,
    }

    outputStr = ""
    result = ""

    for externalDeclaration in translationUnitAST["value"]:
        tempDict = irExternalDeclaration(externalDeclaration["value"], nextRegister)
        # nextRegister = tempDict["nextRegister"]
        nextRegister = 0
        outputStr += tempDict["outputStr"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = result

    return outputDict


def irInitializer(initializerAST, nextRegister, storeLoc):
    outputDict = dict()

    outputStr = ""

    tempDict = irExpression(initializerAST, nextRegister)
    nextRegister = tempDict["nextRegister"]
    outputStr += tempDict["outputStr"]
    result = tempDict["result"]
    resultType = tempDict["resultType"]

    # tempDict= irLoad("i32",f"%{nextRegister}",result)
    # allocType = "i32"
    allocType = resultType
    # tempDict = irStore(allocType,f"%{nextRegister}",result)
    tempDict = irStore(allocType, f"%{storeLoc}", result)

    outputStr += tempDict["outputStr"]
    result = tempDict["result"]

    outputDict["result"] = nextRegister
    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr

    return outputDict

def irExternalDeclaration(externalDeclarationAST, nextRegister=None):
    global currentScope
    if nextRegister is None:
        nextRegister = 0

    outputDict = {
        "nextRegister": None,
        "outputStr": None,
        "result": None,
    }
    outputStr = ""
    result = ""

    if externalDeclarationAST["type"] == "functionDefinition":
        # currentScope = currentScope.enterScope()
        tempDict = irFunctionDefinition(externalDeclarationAST, nextRegister)
        # currentScope = currentScope.exitScope()
    elif externalDeclarationAST["type"] == "declaration":
        tempDict = irDeclaration(externalDeclarationAST, nextRegister)

    outputDict["nextRegister"] = tempDict["nextRegister"]
    outputDict["outputStr"] = tempDict["outputStr"]
    outputDict["result"] = tempDict.get("result")

    return outputDict

def irAssignExpression(assignExpressionAST, nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = dict()
    outputStr = ""

    target = assignExpressionAST["target"]
    expression = assignExpressionAST["assignedValue"]

    tempDict = irExpression(expression, nextRegister)
    nextRegister = tempDict["nextRegister"]
    outputStr += tempDict["outputStr"]
    loadLoc = tempDict["result"]
    varType = tempDict["resultType"]

    if target["type"] == "id":
        variable = currentScope.getVariableRegister(target['value'])
        storeLoc = f"%{variable[0]}"
        allocType = variable[1]
    elif target["type"] == "unaryExpression":
        tempDict = irUnaryExpression(target,nextRegister)
        outputStr += tempDict["outputStr"]
        nextRegister = tempDict["nextRegister"]
        storeLoc = tempDict["result"]
        allocType = tempDict["resultType"]
    
    tempDict = irStore(allocType, storeLoc, loadLoc)
    outputStr += tempDict["outputStr"]

    resultType = allocType
    result = storeLoc

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = result
    outputDict["resultType"] = resultType

    return outputDict


def irExpressionStatement(expressionList: ["assignmentExpression"], nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = {"nextRegister": None, "outputStr": None}
    outputStr = ""
    result = None

    for assignExpression in expressionList:
        # tempDict = irAssignExpression(assignExpression, nextRegister)
        tempDict = irExpression(assignExpression,nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]
        result = tempDict["result"]

    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["result"] = result

    return outputDict


def irReturn(returnAST, nextRegister=None):
    if nextRegister is None:
        nextRegister = 0

    outputDict = dict()
    outputStr = ""
    returnValue = 0
    returnType = currentFunction["llvmData"]["returnType"]
    currentFunction["llvmData"]["explicitReturn"] = True
    expression = returnAST.get("value")
    
    if expression:
        tempDict = irExpressionStatement(expression["value"],nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]
        returnValue = tempDict["result"]
    
    outputStr += f"\tret {returnType} {returnValue}\n"
    
    outputDict["outputStr"] = outputStr
    outputDict["nextRegister"] = nextRegister

    return outputDict

def irPostfixExpression(postfixExpressionAST,nextRegister):
    outputDict = dict()
    outputStr = ""
    result = None
    # print(postfixExpressionAST)
    primaryExpr = postfixExpressionAST["primary"]
    funcCall = postfixExpressionAST["postfixList"][0]
    # print(funcCall)
    if funcCall.get("use") == "funcCall":
        funcCall["funcName"] = primaryExpr["value"]
        tempDict = irFunctionCall(funcCall,nextRegister)
        nextRegister = tempDict["nextRegister"]
        outputStr += tempDict["outputStr"]
        result = tempDict["result"]
        resultType = tempDict["resultType"]

    outputDict["result"] = result
    outputDict["nextRegister"] = nextRegister
    outputDict["outputStr"] = outputStr
    outputDict["resultType"] = resultType
    return outputDict