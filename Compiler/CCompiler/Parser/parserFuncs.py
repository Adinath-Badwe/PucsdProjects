import re

def initState(inputStr,index=None,result=None,isError=None,errorMsg=None,errorCode=None):
	if index is None:
		index = 0
	if result is None:
		result = None
	if isError is None:
		isError = False
	if errorCode is None:
		errorCode = 0
	return (inputStr,index,result,isError,errorMsg,errorCode)
	
def updateState(currentState,index=None,result=None,isError=None,errorMsg=None,errorCode=None,emptyResult=None):
	if index is None:
		index = currentState[1]
	if result is None:
		result = currentState[2]
	if isError is None:
		isError = currentState[3]
	if errorCode is None:
		errorCode = currentState[5]
	if errorMsg is None:
		errorMsg = currentState[4]
	if emptyResult==True:
		result = None
	return (currentState[0],index,result,isError,errorMsg,errorCode)

def parseString(inputStr):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		
		slice = parseState[0][parseState[1]:parseState[1]+len(inputStr)]
		
		if len(slice) == 0:
			return updateState(parseState,isError=True,errorMsg="Tried to match but unexpected end of input",errorCode=1)
		
		if slice == inputStr:
			return updateState(parseState,index=parseState[1]+len(inputStr),result=slice)
		
		return updateState(parseState,isError=True,errorMsg=f"Tried to match {inputStr} at index:{parseState[1]} but failed",errorCode=2)
	
	return innerFunc

def parseSequence(listOfParsers):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		nextState = parseState
		results = []
		
		for index,parser in enumerate(listOfParsers):
			nextState = parser.stateFunction(nextState)
			
			if nextState[3]:
				return nextState
			if nextState[2]:
				results.append(nextState[2])
		
		nextState = updateState(nextState,result=results)
		
		return nextState
		
	return innerFunc

def parseChoice(listOfParsers):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		results = None
		for parser in listOfParsers:
			nextState = parser.stateFunction(parseState)
			
			if not nextState[3]:
				return updateState(nextState,result=nextState[2])
		return updateState(parseState,isError=True,errorMsg="ChoiceParser : Unable to parse with any parser")
	return innerFunc

def parseAlphabet():
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		
		slice = parseState[0][parseState[1]:parseState[1]+1]

		if len(slice) == 0:
			return updateState(parseState,isError=True,errorMsg="Tried to match but unexpected end of input",errorCode=1)
		
		if slice.isalpha():
			return updateState(parseState,index=parseState[1]+1,result=slice)
		
		return updateState(parseState,isError=True,errorMsg="Tried to match but failed",errorCode=2)
	
	return innerFunc

def parseAlphaNumeric():
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		
		slice = parseState[0][parseState[1]:parseState[1]+1]

		if len(slice) == 0:
			return updateState(parseState,isError=True,errorMsg="Tried to match but unexpected end of input",errorCode=1)
		
		if slice.isalpha() or slice.isdigit():
			return updateState(parseState,index=parseState[1]+1,result=slice)
		
		return updateState(parseState,isError=True,errorMsg="Tried to match but failed",errorCode=2)
	
	return innerFunc

def parseDigit():
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		
		slice = parseState[0][parseState[1]:parseState[1]+1]
		
		if len(slice) == 0:
			return updateState(parseState,isError=True,errorMsg="Tried to match but unexpected end of input",errorCode=1)
		
		if slice.isdigit():
			return updateState(parseState,index=parseState[1]+1,result=slice)
		
		return updateState(parseState,isError=True,errorMsg="Tried to match but failed",errorCode=2)
	
	return innerFunc

def parseMany(inputParser):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		results = []
		done = False
		nextState = parseState
		while(not done):
			testState = inputParser.stateFunction(nextState)
			
			if(not testState[3]):
				results.append(testState[2])
				nextState = testState
			else:
				done = True
		
		return updateState(parseState,index=nextState[1],result=results)
	return innerFunc

def parseMany1(inputParser):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		results = []
		done = False
		nextState = parseState
		while(not done):
			testState = inputParser.stateFunction(nextState)
			
			if(not testState[3]):
				results.append(testState[2])
				nextState = testState
			else:
				done = True
		
		if (len(results) == 0):
			return updateState(parseState,isError=True,errorMsg=f"Many1: Unable to match any input using parser @index {parseState[1]}");
		
		return updateState(parseState,index=nextState[1],result=results)
	return innerFunc

def parseOptional(parser):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		parseState = updateState(parseState,result=None)
		nextState = parser.stateFunction(parseState)
		if nextState[3]:
			nextState = updateState(parseState,emptyResult=True,errorMsg=None,isError=False)
		return nextState
	return innerFunc

def parseRegex(pattern):
	def innerFunc(parseState):
		if parseState[3]:
			return parseState
		inputStr = parseState[0][parseState[1]:]
		match1 = re.match(pattern,inputStr)
		if match1:
			return updateState(parseState,index=parseState[1]+len(match1.group()),result=match1.group())

		return updateState(parseState,isError=True,errorMsg=f"RegexParser : Could not parse input {parseState[0]} with pattern '{pattern}' ")
	return innerFunc