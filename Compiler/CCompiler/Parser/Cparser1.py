from Parser.parser import *
import json
from Parser.miscFuncs import convertListToTree
from SecondPass.secondPassFuncs import convertForLoopToWhileLoop

"""
def test():
    def mapFunc(inputResult):
        output = inputResult
        return output
    parserFunc = 
    return parserFunc.map(mapFunc)
"""

def blockGen():
    def mapFunc(inputResult):
        output = inputResult
        return output
    parserFunc = ChoiceParser([declaration,statement])
    return parserFunc.map(mapFunc)

def statementGen():
    def mapFunc(inputResult):
        output = inputResult
        return output
    parserFunc = ChoiceParser([compoundStatement,jumpStatement,iterationStatement,selectionStatement,expressionStatement])
    return parserFunc.map(mapFunc)

def declarationGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"declaration","declarationSpecifiers":inputResult[0]}
        if len(inputResult) == 3:
            output["initDeclaratorList"] = inputResult[1]
        return output
    parserFunc = SequenceParser([declarationSpecifiers,spaceParser,OptionalParser(initDeclaratorList),spaceParser,StringParser(";")])
    return parserFunc.map(mapFunc)

def declarationListGen():
    def mapFunc(inputResult):
        output = inputResult
        return output
    parserFunc = ManyParser1(declaration)
    return parserFunc.map(mapFunc)

def declarationSpecifiersGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"declarationSpecifiers","value":inputResult}
        return output
    
    choices = [
        typeSpecifier
    ]

    parserFunc = ManyParser1(SequenceParser([ChoiceParser(choices),spaceParser]).map(lambda x:x[0]))
    return parserFunc.map(mapFunc)

def typeSpecifierGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"typeSpecifier","value":inputResult}
        return output


    typeSpecs = [StringParser(i) for i in ["void", "short" , "char" , "int" , "float" , "double" , "long" , "bool" , "signed" , "unsigned"]]
    
    choices = [
        ChoiceParser(typeSpecs),
        structUnionSpecifier
    ]
    
    parserFunc = ChoiceParser(choices)
    return parserFunc.map(mapFunc)

def initDeclaratorListGen():
    def mapFunc(inputResult):
        output = [inputResult[0]] + inputResult[1] if len(inputResult) == 2 else [inputResult[0]]
        return output
    # parserFunc = ManyParser1(initDeclarator)
    parserFunc = SequenceParser([initDeclarator,ManyParser(SequenceParser([spaceParser,StringParser(","),spaceParser,initDeclarator]).map(lambda x:x[-1]))])
    return parserFunc.map(mapFunc)

def initDeclaratorGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"initDeclarator","declarator":inputResult[0]}
        if len(inputResult) == 2:
            output["initializer"] = inputResult[1][1]
        return output
    parserFunc = SequenceParser([declarator,OptionalParser(SequenceParser([spaceParser,StringParser("="),spaceParser,initializer]))])
    return parserFunc.map(mapFunc)

def initializerGen():
    def mapFunc(inputResult):
        output = inputResult
        return output
    parserFunc = ChoiceParser([assignmentExpression])
    return parserFunc.map(mapFunc)

def declaratorGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"declarator"}
        if len(inputResult) == 2:
            output["drefCount"] = inputResult[0]["count"]
            output["value"] = inputResult[1]
        elif len(inputResult) == 1:
            output["value"] = inputResult[0]
        return output
    parserFunc = SequenceParser([OptionalParser(pointer),directDeclarator])
    return parserFunc.map(mapFunc)

def directDeclaratorGen():
    def mapFunc(inputResult):
        # output = inputResult
        # output = {"type":"directDeclarator","left":inputResult[0]}
        inputResult = [i for i in inputResult if i != ['']]
        output = [inputResult[0]]
        if len(inputResult) == 2:
            # output["right"] = inputResult[1] if inputResult[1] != [''] else None
            output += inputResult[1]
        # print(output)
        return output
    
    insideSquareBrackets = [
        assignmentExpression,
    ]
    insideParentheses = [
        parameterList,
        identifierList
    ]

    choices = [
        SequenceParser([StringParser("("),spaceParser,OptionalParser(ChoiceParser(insideParentheses)),spaceParser,StringParser(")")]).map(lambda x:x[1] if len(x) == 3 else ""),
        SequenceParser([StringParser("["),spaceParser,OptionalParser(ChoiceParser(insideSquareBrackets)),spaceParser,StringParser("]")]).map(lambda x:{"type":"squareBrackets","use":"array","expression":x[1]} if len(x) == 3 else ""),
    ]

    dd1 = ChoiceParser(choices)
    smething = ChoiceParser([SequenceParser([StringParser("("),spaceParser,declarator,spaceParser,StringParser(")")]).map(lambda x : x[1]),idParser])

    parserFunc = SequenceParser([smething,ManyParser(dd1)])
    return parserFunc.map(mapFunc)

# def retX(x,msg):
#     print(msg)
#     return x

def identifierListGen():
    def mapFunc(inputResult):
        output = inputResult
        return output
    parserFunc = SequenceParser([idParser,ManyParser(SequenceParser([spaceParser,StringParser(","),spaceParser,idParser]).map(lambda x:x[1]))])
    return parserFunc.map(mapFunc)    

def pointerGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"pointer","count":len(inputResult)}
        return output
    # parserFunc = ChoiceParser([SequenceParser([StringParser("*"),pointer]),StringParser("*")])
    parserFunc = ManyParser1(StringParser("*"))
    return parserFunc.map(mapFunc)

def compoundStatementGen():
    def mapFunc(inputResult):
        output = {"type":"compoundStatement","value":None}
        if len(inputResult) == 3:
            output["value"] = inputResult[1]
        return output
    parserFunc = SequenceParser([StringParser("{"),newlineParser,OptionalParser(blockList),newlineParser,StringParser("}")])
    return parserFunc.map(mapFunc)

def blockListGen():
    def mapFunc(inputResult):
        output = inputResult
        return output
    # parserFunc = ChoiceParser([block,SequenceParser([blockList,block])])
    parserFunc = ManyParser1(SequenceParser([newlineParser,block,newlineParser]).map(lambda x:x[0]))
    return parserFunc.map(mapFunc)

# def expressionStatementGen():
#     def mapFunc(inputResult):
#         return {"type":"expressionStatement","value":inputResult}
#     parserFunc = SequenceParser([OptionalParser(expression),spaceParser,StringParser(";").map(lambda x:"")])
#     return parserFunc.map(mapFunc)

def expressionStatementGen():
    def mapFunc(inputResult):
        output = {"type":"expressionStatement"}
        if len(inputResult) == 2:
            output["expression"]=inputResult[0]["value"]
            
        return output
    parserFunc = SequenceParser([OptionalParser(expression),spaceParser,StringParser(";")])
    return parserFunc.map(mapFunc)

def selectionStatementGen():
    def mapFunc(inputResult):
        output = {
            "type":"selectionStatement",
            "expression":inputResult[2],
            "trueStatement":inputResult[4]
        }
        
        if len(inputResult) > 5:
            output["falseStatement"] = inputResult[-1][-1]
        
        return output
    parserFunc = SequenceParser([StringParser("if"),spaceParser,StringParser("("),spaceParser,expression,spaceParser,StringParser(")"),statement,OptionalParser(SequenceParser([StringParser("else"),statement]))])
    return parserFunc.map(mapFunc)

def iterationStatementGen():
    def mapFunc(inputResult):
        output = {
            "type":"iterationStatement",
            "value":inputResult
        }
        if inputResult["type"] == "compoundStatement":
            return inputResult
        return output
    choices = [
        whileLoop,
        forLoop
    ]
    parserFunc = ChoiceParser(choices)
    return parserFunc.map(mapFunc)

def forLoopGen():
    def mapFunc(inputResult):
        output = {
            "type":"forLoop",
            "statement":inputResult[-1],
            "conditional":{
                "first":inputResult[2][0],
                "exprStm":inputResult[2][1],
            }
        }
        if len(inputResult[2]) == 3:
            output["conditional"]["expr"] = inputResult[2][2]
        
        return convertForLoopToWhileLoop(output)
        return output

    parserFunc = SequenceParser([StringParser("for"),StringParser("("),spaceParser,SequenceParser([ChoiceParser([expressionStatement,declaration]),spaceParser,expressionStatement,spaceParser,OptionalParser(expression)]),spaceParser,StringParser(")"),statement])
    return parserFunc.map(mapFunc)

def whileLoopGen():
    def mapFunc(inputResult):
        output = {
            "type":"whileLoop",
            "statement":inputResult[-1],
            "expression":inputResult[2]
        }
        return output
        
    parserFunc = SequenceParser([StringParser("while"),spaceParser,StringParser("("),spaceParser,expression,spaceParser,StringParser(")"),statement])
    return parserFunc.map(mapFunc)


def jumpStatementGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"jumpStatement","jumpType":inputResult[0]["type"]}

        if inputResult[0].get("value"):
            output["value"] = inputResult[0]["value"]

        return output
    choices = ["break","return","continue"]
    choices2 = SequenceParser([StringParser("return"),spaceParser,expression]).map(lambda x:{"type":"return","value":x[1]})
    choices3 = SequenceParser([StringParser("goto"),spaceParser,idParser]).map(lambda x:{"type":"goto","value":x[1]})

    parserFunc = SequenceParser([ChoiceParser([choices2,choices3,ChoiceParser([StringParser(i) for i in choices]).map(lambda x:{"type":x})]),spaceParser,StringParser(";")])
    return parserFunc.map(mapFunc)

def functionDefinitionGen():
    def mapFunc(inputResult):
        output = {"type":"functionDefinition","declarationSpecifiers":inputResult[0]["value"],"declarator":inputResult[1]["value"],"compoundStatement":inputResult[-1]["value"]}
        if len(inputResult) == 4:
            output["declarationList"] = inputResult[2]
        return output
    # space parser here causes error
    parserFunc = SequenceParser([declarationSpecifiers,spaceParser,declarator,spaceParser,OptionalParser(declarationList),spaceParser,compoundStatement])
    return parserFunc.map(mapFunc)

def translationUnitGen():
    def mapFunc(inputResult):
        output = {"type":"translationUnit","value":inputResult}
        return output
    # parserFunc = ChoiceParser([externalDeclaration,SequenceParser([translationUnit,externalDeclaration])])
    parserFunc = ManyParser1(SequenceParser([newlineParser,externalDeclaration,newlineParser]).map(lambda x:x[0]))
    return parserFunc.map(mapFunc)

def externalDeclarationGen():
    def mapFunc(inputResult):
        output = inputResult
        output = {"type":"externalDeclaration","value":inputResult}
        return output
    parserFunc = ChoiceParser([functionDefinition,declaration])
    return parserFunc.map(mapFunc)

def expressionGen():
    def mapFunc(inputResult):
        # return inputResult
        output = {"type":"expression","value":[inputResult[0]]}
        if len(inputResult) > 1:
            output["value"] += inputResult[1]
        # len(output["value"])

        return output
    parserFunc = SequenceParser([assignmentExpression,spaceParser,ManyParser(SequenceParser([StringParser(","),spaceParser,assignmentExpression]).map(lambda x:x[1]))])
    return parserFunc.map(mapFunc)

def assignmentExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"assignmentExpression"}
        if type(inputResult) == dict:
            output = inputResult
        else:
            output["target"] = inputResult[0]
            output["assignedValue"] = inputResult[1]
        return output
    parserFunc = ChoiceParser([SequenceParser([unaryExpression,spaceParser,StringParser("="),spaceParser,assignmentExpression]).map(lambda x:[x[0],x[2]]),conditionalExpression])
    return parserFunc.map(mapFunc)

def conditionalExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"conditionalExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output["left"] = inputResult[0]
            output["midExpr"] = inputResult[1][1]
            output["right"] = inputResult[1][3]
        return output
    parserFunc = SequenceParser([logicalOrExpression,OptionalParser(SequenceParser([spaceParser,StringParser("?"),spaceParser,expression,spaceParser,StringParser(":"),spaceParser,conditionalExpression]))])
    return parserFunc.map(mapFunc)

def logicalOrExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"logicalOrExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([logicalAndExpression,ManyParser(SequenceParser([spaceParser,StringParser("||"),spaceParser,logicalAndExpression]))])
    return parserFunc.map(mapFunc)

def logicalAndExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"logicalAndExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([inclusiveOrExpression,ManyParser(SequenceParser([spaceParser,StringParser("&&"),spaceParser,inclusiveOrExpression]))])
    return parserFunc.map(mapFunc)

def inclusiveOrExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"inclusiveOrExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([exclusiveOrExpression,ManyParser(SequenceParser([spaceParser,StringParser("|"),spaceParser,exclusiveOrExpression]))])
    return parserFunc.map(mapFunc)

def exclusiveOrExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"exclusiveOrExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([andExpression,ManyParser(SequenceParser([spaceParser,StringParser("^"),spaceParser,andExpression]))])
    return parserFunc.map(mapFunc)

def andExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"andExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([equalityExpression,ManyParser(SequenceParser([spaceParser,StringParser("&"),spaceParser,equalityExpression]))])
    return parserFunc.map(mapFunc)

def equalityExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"equalityExpression","value":inputResult}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([relationalExpression,ManyParser(SequenceParser([spaceParser,ChoiceParser([StringParser("=="),StringParser("!=")]),spaceParser,relationalExpression]))])
    return parserFunc.map(mapFunc)

def relationalExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"relationalExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([shiftExpression,ManyParser(SequenceParser([spaceParser,ChoiceParser([StringParser("<="),StringParser(">="),StringParser(">"),StringParser("<")]),spaceParser,shiftExpression]))])
    return parserFunc.map(mapFunc)

def shiftExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"shiftExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output
    parserFunc = SequenceParser([additiveExpression,ManyParser(SequenceParser([spaceParser,ChoiceParser([StringParser("<<"),StringParser(">>")]),spaceParser,additiveExpression]))])
    return parserFunc.map(mapFunc)

def additiveExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"additiveExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])
        return output

    parserFunc = SequenceParser([multiplicativeExpression,ManyParser(SequenceParser([spaceParser,ChoiceParser([StringParser("+"),StringParser("-")]),spaceParser,multiplicativeExpression]))])
    return parserFunc.map(mapFunc)

def multiplicativeExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"multiplicativeExpression"}
        if len(inputResult) == 1:
            output = inputResult[0]
        else:
            output = convertListToTree(inputResult,output["type"])

        return output

    someValue = ManyParser(SequenceParser([spaceParser,ChoiceParser([StringParser("*"),StringParser("/"),StringParser("%")]),spaceParser,castExpression]))
    parserFunc = SequenceParser([castExpression,someValue])
    return parserFunc.map(mapFunc)

def castExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"castExpression"}
        if len(inputResult) == 1:
            return inputResult[0]
        elif len(inputResult) == 2:
            output = {"type":"castExpression","expr":inputResult[1],"casts":inputResult[0]}

        return output
    parserFunc = SequenceParser([ManyParser(SequenceParser([StringParser("("),spaceParser,typeName,spaceParser,StringParser(")")]).map(lambda x:x[1])),unaryExpression])
    return parserFunc.map(mapFunc)

def unaryExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"unaryExpression","value":inputResult}
        if type(inputResult) == dict:
            return inputResult
        if type(inputResult) == list and len(inputResult) == 1:
            return inputResult[0]
        return output
    choices = [
        postfixExpression,
        SequenceParser([unaryOperator,castExpression]).map(lambda x:{"type":"unaryExpression","operator":x[0],"castExpr":x[1]}),
        SequenceParser([ChoiceParser([StringParser("++"),StringParser("--")]),unaryExpression])
    ]
    parserFunc = ChoiceParser(choices)
    return parserFunc.map(mapFunc)

def structUnionSpecifierGen():
    def mapFunc(inputResult):
        
        output = {"type":"structUnionSpecifier","structType":inputResult[0]}
        
        if len(inputResult) == 2:
            if inputResult[1]["type"] == "idParser":
                output["structName"] = inputResult[1]["value"]["value"]
            elif inputResult[1]["type"] == "someParser":
                output["value"] = inputResult[1]["value"]
        elif len(inputResult) == 3:
            output["structName"] = inputResult[1]["value"]["value"]
            output["value"] = inputResult[2]["value"]
        
        return output

    someParser = SequenceParser([StringParser("{"),newlineParser,structDeclarationList,newlineParser,StringParser("}")]).map(lambda x:x[1])

    parserFunc = SequenceParser([ChoiceParser([StringParser(i) for i in ["struct","union"]]),spaceParser,OptionalParser(idParser).map(lambda x:{"type":"idParser","value":x}),spaceParser,OptionalParser(someParser).map(lambda x:{"type":"someParser","value":x})])

    return parserFunc.map(mapFunc)

def structDeclarationListGen():
    def mapFunc(inputResult):
        output = {"type":"structDeclarationList","value":inputResult}
        if len(inputResult) == 2:
            output["value"] = [inputResult[0]] + inputResult[1]
        
        return output
    
    parserFunc = SequenceParser([structDeclaration,ManyParser(SequenceParser([newlineParser,structDeclaration]))])
    return parserFunc.map(mapFunc)

def structDeclarationGen():
    def mapFunc(inputResult):
        output = {"type":"structDeclaration","specifierQualifierList":inputResult[0]}
        if len(inputResult) == 2:
            output["structDeclaratorList"] = inputResult[1]
        
        return output
    
    parserFunc = SequenceParser([specifierQualifierList,spaceParser,OptionalParser(structDeclaratorList),spaceParser,StringParser(";").map(lambda x:'')])
    return parserFunc.map(mapFunc)

def structDeclaratorListGen():
    def mapFunc(inputResult):
        output = {"type":"structDeclaratorList","value":inputResult}
        if len(inputResult) == 2:
            output["value"] = [inputResult[0]]+inputResult[1]
        
        return output
    parserFunc = SequenceParser([structDeclarator,newlineParser,ManyParser(SequenceParser([StringParser(","),newlineParser,structDeclarator]).map(lambda x:x[1]))])
    return parserFunc.map(mapFunc)

def structDeclaratorGen():
    def mapFunc(inputResult):
        output = {"type":"structDeclarator"}
        
        if inputResult["type"] == "first":
            inputResult = inputResult["value"]
            
            output["expr"] = inputResult[-1]
            
            if len(inputResult) == 2:
                output["declarator"] = inputResult[0]
            
            if len(inputResult) > 2:
                raise Exception("StructDeclarator : Invalid Result")
            
        elif inputResult["type"] == "second":
            inputResult = inputResult["value"]
            output["declarator"] = inputResult
        else:
            raise Exception("StructDeclarator : Cannot Parse the input")
        
        return output
    
    choices = [
        SequenceParser([OptionalParser(declarator),spaceParser,StringParser(":").map(lambda x:""),spaceParser,conditionalExpression]).map(lambda x:{"type":"first","value":x}),
        declarator.map(lambda x:{"type":"second","value":x}),
    ]
    
    parserFunc = ChoiceParser(choices)
    return parserFunc.map(mapFunc)

def postfixExpressionGen():
    def mapFunc(inputResult):
        output = {"type":"postfixExpression"}
        if len(inputResult) == 1:
            return inputResult[0]
        else:
            # output = convertListToTree(inputResult,output["type"])
            output = {"type":"postfixExpression","primary":inputResult[0],"postfixList":inputResult[1]}
        return output

    choices = [
        SequenceParser([StringParser("("),spaceParser,OptionalParser(argumentExpressionList),spaceParser,StringParser(")")]).map(lambda x:{"use":"funcCall","value":x[1]} if len(x) == 3 else {"use":"funcCall"}),
        SequenceParser([StringParser("["),spaceParser,expression,spaceParser,StringParser("]")]).map(lambda x:{"use":"arrayUse","value":x[1]}),
        StringParser("++").map(lambda x:{"use":"increment"}),
        StringParser("--").map(lambda x:{"use":"decrement"}),
    ]
    postfix = ChoiceParser(choices)

    parserFunc = SequenceParser([primaryExpression,ManyParser(postfix)])
    return parserFunc.map(mapFunc)

def primaryExpressionGen():
    def mapFunc(inputResult):
        return inputResult
        output = {"type":"primaryExpression","value":inputResult}
        
        return output

    choices = [
        SequenceParser([StringParser("("),spaceParser,expression,spaceParser,StringParser(")")]).map(lambda x:x[1]),
        idParser,
        constant
    ]

    parserFunc = ChoiceParser(choices)
    return parserFunc.map(mapFunc)

def constantGen():
    def mapFunc(inputResult):
        output = {"type":"constant","value":inputResult["value"],"valType":inputResult["type"]}
        return output

    choices = [
        digitsParser,
        floatingPointParser
    ]

    parserFunc = ChoiceParser(choices)
    return parserFunc.map(mapFunc)
        
def parameterDeclarationGen():
    def mapFunc(inputResult):
        output = {"type":"parameterDeclaration","declarationSpecifiers":inputResult[0]["value"]}
        if len(inputResult) > 1:
            output["declarator"] = inputResult[1]["value"]
        return output
    parserFunc = SequenceParser([declarationSpecifiers,OptionalParser(declarator)])
    return parserFunc.map(mapFunc)

def parameterListGen():
    def mapFunc(inputResult):
        output = {"type":"parameterList","value":[inputResult[0]]}
        if len(inputResult) > 1:
            output["value"] += inputResult[1]
        return output
    parserFunc = SequenceParser([parameterDeclaration,spaceParser,ManyParser(SequenceParser([StringParser(","),spaceParser,parameterDeclaration]).map(lambda x:x[1]))])
    return parserFunc.map(mapFunc)

def argumentExpressionListGen():
    def mapFunc(inputResult):
        output = {"type":"argumentExpressionList","value":[inputResult[0]]}
        if len(inputResult) == 2:
            output["value"] += inputResult[1]
        return output
    parserFunc = SequenceParser([assignmentExpression,ManyParser(SequenceParser([spaceParser,StringParser(","),spaceParser,assignmentExpression]).map(lambda x:x[1]))])
    return parserFunc.map(mapFunc)

def specifierQualifierListGen():
    def mapFunc(inputResult):
        output = {"type":"specifierQualifierList","value":inputResult}
        return output
    parserFunc = SequenceParser([ChoiceParser([typeSpecifier]),OptionalParser(specifierQualifierList)])
    return parserFunc.map(mapFunc)


block = lazy(blockGen)
blockList = lazy(blockListGen)
declaration = lazy(declarationGen)
declarationList = lazy(declarationListGen)
declarationSpecifiers = lazy(declarationSpecifiersGen)
typeSpecifier = lazy(typeSpecifierGen)

structUnionSpecifier = lazy(structUnionSpecifierGen)
structDeclarationList = lazy(structDeclarationListGen)
structDeclaration = lazy(structDeclarationGen)
structDeclaratorList = lazy(structDeclaratorListGen)
structDeclarator = lazy(structDeclaratorGen)


initDeclaratorList = lazy(initDeclaratorListGen)
initDeclarator = lazy(initDeclaratorGen)
initializer = lazy(initializerGen)
directDeclarator = lazy(directDeclaratorGen)
declarator = lazy(declaratorGen)
pointer = lazy(pointerGen)
compoundStatement = lazy(compoundStatementGen)
expressionStatement = lazy(expressionStatementGen)
selectionStatement = lazy(selectionStatementGen)
iterationStatement = lazy(iterationStatementGen)
forLoop = lazy(forLoopGen)
whileLoop = lazy(whileLoopGen)
statement = lazy(statementGen)
functionDefinition = lazy(functionDefinitionGen)
jumpStatement = lazy(jumpStatementGen)
externalDeclaration = lazy(externalDeclarationGen)
translationUnit = lazy(translationUnitGen)
expression = lazy(expressionGen)
assignmentExpression = lazy(assignmentExpressionGen)
parameterList = lazy(parameterListGen)
parameterDeclaration = lazy(parameterDeclarationGen)

# expressions here :-

conditionalExpression = lazy(conditionalExpressionGen)
logicalOrExpression = lazy(logicalOrExpressionGen)
logicalAndExpression = lazy(logicalAndExpressionGen)
andExpression = lazy(andExpressionGen)
exclusiveOrExpression = lazy(exclusiveOrExpressionGen)
inclusiveOrExpression = lazy(inclusiveOrExpressionGen)
unaryExpression = lazy(unaryExpressionGen)
unaryOperator = ChoiceParser([StringParser(i) for i in ["&","*"]])
relationalExpression = lazy(relationalExpressionGen)
shiftExpression = lazy(shiftExpressionGen)
additiveExpression = lazy(additiveExpressionGen)
multiplicativeExpression = lazy(multiplicativeExpressionGen)
primaryExpression = lazy(primaryExpressionGen)
constant = lazy(constantGen)
castExpression = lazy(castExpressionGen)
equalityExpression = lazy(equalityExpressionGen)
postfixExpression = lazy(postfixExpressionGen)
argumentExpressionList = lazy(argumentExpressionListGen)
specifierQualifierList = lazy(specifierQualifierListGen)
typeName = specifierQualifierList
identifierList = lazy(identifierListGen)

# with open("output.json","w") as outputFile:
#     with open("input","r") as file:
#         content = file.read()
#         # result = (translationUnit.run(initState(content)))
#         result = (expression.run(initState(content)))
#         json.dump(result[2],outputFile)

def RunParser():
    with open("intermediateOutput/output.json","w") as outputFile:
        with open("input/input.c","r") as file:
            content = file.read()
            result = (translationUnit.run(initState(content)))
            json.dump(result[2],outputFile)

# assume types match in expressions, raise exception if they dont
# convert to llvm ir
# function definitions and calls
