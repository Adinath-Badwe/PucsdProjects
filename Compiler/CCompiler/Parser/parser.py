from Parser.parserFuncs import *

class Parser:
	def __init__(self,stateFunction):
		self.stateFunction = stateFunction
	
	def run(self,parseState):
		return self.stateFunction(parseState)

	def map(self,func):
		def innerFunc(parseState):
			nextState = self.stateFunction(parseState)
			if nextState[3]:
				return nextState
			
			return updateState(nextState,result=func(nextState[2]))
		return Parser(innerFunc)
	
	def chain(self,func):
		def innerFunc(parseState):
			nextState = self.stateFunction(parseState)
			if nextState[3]:
				return nextState
			nextParser = func(nextState[2])
			return nextParser.stateFunction(nextState)
		return Parser(innerFunc)

def lazy(parser_thunk):
	return Parser(lambda parser_state: parser_thunk().run(parser_state))

def between(leftParser,rightParser):
	def innerFunc(contentParser):
		return Parser(parseSequence([leftParser,contentParser,rightParser])).map(lambda x:x[1])
	return innerFunc
	
def SequenceParser(parserList):
	return Parser(parseSequence(parserList))

def ChoiceParser(parserList):
	return Parser(parseChoice(parserList))

def ManyParser(inputParser):
	return Parser(parseMany(inputParser))

def ManyParser1(inputParser):
	return Parser(parseMany1(inputParser))

def StringParser(inputStr):
	return Parser(parseString(inputStr))

def RegexParser(inputStr):
	return Parser(parseRegex(inputStr))

def OptionalParser(inputParser):
	return Parser(parseOptional(inputParser))

spaceParser = ManyParser(StringParser(" ")).map(lambda x : '')
newlineParser = SequenceParser([spaceParser,ManyParser(StringParser("\n")),spaceParser]).map(lambda x:'')
idParser = RegexParser("[a-zA-Z_][a-zA-Z0-9_]*").map(lambda x : {'type':'id','value':x})
digitsParser = RegexParser("[0-9]+").map(lambda x : {'type':'int','value':x})
integer = digitsParser
floatingPointParser = SequenceParser([digitsParser,StringParser("."),RegexParser("[0-9]*").map(lambda x : {'type':'int','value':int("".join(x))})]).map(lambda x : {'type':'float','value':float("".join(str(x[0]['value'])+x[1]+str(x[2]['value'])))})
lpParser = StringParser("(")
rpParser = StringParser(")")