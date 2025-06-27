def convertTypeToLLVM(inputType):
    typeDict = {
        "int": "i32",
        "float": "float",
        "char": "i8",
    }

    return typeDict.get(inputType)

def convertDecSpecToLLVM(decSpec):
    return convertTypeToLLVM(decSpec[0]["value"])
