import re

from triangle_functions_holder import triangleFunctionHolder as trianFunc

class mamdani:
    def __init__(self, threshold):
        self.given_threshold = threshold
        self.functionsTupleList = []  #[(name, function)]
        self.fuzzySets = []           #[(name, value)]
        self.rulesList = []           #rules list in prefix notation
        self.variableNames = []       #[names]
        self.result = []              #result of firing level calculations

    def addVariable(self, name, type, firstPoint, secondPoint, thirdPoint = 0):
        if(type == "triangle"):
            self.functionsTupleList.append((name, trianFunc(firstPoint, secondPoint, thirdPoint)))
        self.variableNames.append(name)


    def calcSingle(self, name, argument):  #callculating single fuzzy value of given name
        func = next((t[1] for t in self.functionsTupleList if t[0] == name), None)
        return(func.calculate(argument))


    def calculateAll(self, inputList):  #input list - tuple list (name, argument)
        self.variableNames = []
        result = []
        for i in range(len(inputList)):
            result.append(self.calcSingle(inputList[i][0], inputList[i][1]))
            self.variableNames.append(inputList[i][0])
        self.fuzzySets = result
        return self.fuzzySets


    def addRule(self, input_string):  #dodawanie reguł + parsowanie

        tokens = re.findall(r'\bAND\b|\bOR\b|[()A-Za-z0-9_]+', input_string)
        result = tokens[-1]
        tokens = tokens[:-2]

        output = self.infix_to_prefix(tokens)

        output = self.__combine(output)

        self.rulesList.append([result, output])

    def infix_to_prefix(self, infix_tokens):
        operators = ['AND', 'OR']
        stack = []
        output = []

        for token in reversed(infix_tokens):
            if token not in operators and token not in ('(', ')'):
                output.append(token)
            elif token == ')':
                stack.append(token)
            elif token == '(':
                while stack and stack[-1] != ')':
                    output.append(stack.pop())
                stack.pop()
            elif token in operators:
                while stack and stack[-1] in operators and operators.index(stack[-1]) < operators.index(token):
                    output.append(stack.pop())
                stack.append(token)

        while stack:
            output.append(stack.pop())

        return list(reversed(output))

    def __combine(self, result):  #removing IF; IS;
        final_result = []
        i = 0
        while i < len(result):
            if i + 2 < len(result) and result[i + 1] == 'IS':
                final_result.append((result[i], result[i + 2]))
                i += 3
            else:
                if result[i] != 'IF':
                    final_result.append(result[i])
                    i += 1
                else:
                    i += 1
        return final_result


    def orOperation(self, a, b):
        return max(a, b)

    def andOperation(self, a, b):
        return min(a, b)


    def computeRules(self):  #calculating response level for each rule
        stack = []
        listTmp = []
        rulesOutput = []
        for rule in self.rulesList:
            for token in rule[1]:
                stack.append(token)

            while len(stack) > 0:
                elem = stack.pop()
                if elem == 'OR':
                    listTmp.append(self.orOperation(listTmp.pop(), listTmp.pop()))
                elif elem == 'AND':
                    listTmp.append(self.andOperation(listTmp.pop(), listTmp.pop()))
                else:
                    for name in self.variableNames:
                        if name == elem[0]:
                            if elem[1] == 'low':
                                listTmp.append(self.fuzzySets[self.variableNames.index(name)][0][1])
                            elif elem[1] == 'medium':
                                listTmp.append(self.fuzzySets[self.variableNames.index(name)][1][1])
                            elif elem[1] == 'high':
                                listTmp.append(self.fuzzySets[self.variableNames.index(name)][2][1])
            rulesOutput.append([rule[0], listTmp[0]])
            stack.clear()
            listTmp.clear()

        rulesOutput = self.eliminate_duplicates(rulesOutput)
        self.result = rulesOutput
        return self.result

    def eliminate_duplicates(self, lst):  #calculating highest response value
        max_values = {}
        result = []

        for string, value in lst:
            if string not in max_values or value > max_values[string]:
                max_values[string] = value

        for string, value in max_values.items():
            result.append([string, value])

        return result

    def getResult(self):  #interpretation of fuzzy result
        result = self.result
        cellResult = 0
        notCellResult = 0
        for element in result:
            if(element[0] == 'cell'):
                cellResult = element[1]
            elif (element[0] == 'notCell'):
                notCellResult = element[1]
        if(cellResult > notCellResult and cellResult > self.given_threshold):
            return 'cell'
        else:
            return 'notCell'