
def convertTemp(content:"multiplicativeExpression result",inputType):
    def extractValues(inputList):
        outputList = []
        for i in inputList:
            outputList.append(i[0])
            outputList.append(i[1])
        
        return outputList

    # def someFunc(inputList:list,myFlag:bool,inputType:str):
    #     outputDict = {"type":inputType}
    #     myFlag = False
    #     outputDict["left"] = inputList[0]
    #     if len(inputList) > 1:
    #         outputDict["operator"] = inputList[1]
    #         if len(inputList[2:]) == 1 and not myFlag:
    #             outputDict["right"] = inputList[2:][0]
    #         else:
    #             outputDict["right"] = someFunc(inputList[2:],myFlag,inputType)
    #     return outputDict

    def someFunc(inputList:list,myFlag:bool,inputType:str):
        outputDict = {"type":inputType}
        myFlag = False
        outputDict["right"] = inputList[-1]
        if len(inputList) > 1:
            outputDict["operator"] = inputList[-2]
            if len(inputList[2:]) == 1 and not myFlag:
                outputDict["left"] = inputList[:-2][0]
            else:
                outputDict["left"] = someFunc(inputList[:-2],myFlag,inputType)
        return outputDict

    inputList = [content[0]] + extractValues(content[1])
    output = someFunc(inputList,True,inputType)
    return output

def convertListToTree(inputResult,inputType):
    output = {"type":inputType}
    temp1 = convertTemp(inputResult,output["type"])
    output["left"] = temp1["left"]
    output["right"] = temp1["right"]
    output["operator"] = temp1["operator"]

    return output
