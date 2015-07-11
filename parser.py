from collections import defaultdict
from pprint import pprint

class Parser(object):

    START = 0
    END = -1
    STOP = -1

    SHIFT = 0
    REDUCE = 1

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.terminals = []
        self.repMap = {}
        self.repMap[Parser.START] = "S'"
        self.repMap[Parser.END] = "$"
        self.rules = {}
        self.firstSets = dict()
        self.nt = 1
        self.t = -2
        self.start = None

    def add_terminal(self, rep, matcher):
        res = self.t
        self.t -= 1
        self.terminals.append((res, matcher))
        self.repMap[res] = rep
        return res

    def add_non_terminal(self, rep):
        res = self.nt
        self.nt += 1
        self.repMap[res] = rep
        self.rules[res] = []
        if self.start is None:
            self.start = res
        return res

    def add_rule(self, non_terminal, expansion, conv_fun):
        self.rules[non_terminal].append((expansion, conv_fun))

    def add_first_set(self, nt, se):
        self.firstSets[nt] = se

    def display(self):
        for nt in self.rules:
            rule = self.repMap[nt] + " -> "
            l = len(rule)
            b = False
            for exp in self.rules[nt]:
                if b:
                    rule += " " * (l - 3) + '|  '
                b = True
                rule += " ".join(map(lambda x: self.repMap[x], list(exp[0]))) + "\n"
            print(rule + '\n')

    def build_table(self):

        self.table = defaultdict(dict)

        indToStateItems = dict()
        kernelToInd = dict()

        def printItem(item):
            return (self.repMap[item[0]] + ' -> ' +
                " ".join(map(lambda x: self.repMap[x], list(item[1])[:item[2]])) + " . " +
                " ".join(map(lambda x: self.repMap[x], list(item[1])[item[2]:])) + " , " +
                self.repMap[item[3]])

        def buildState(kernel, rules):
            if kernel in kernelToInd:
                return kernelToInd[kernel], False
            print("State: " + str(buildState.stateCount))
            print("Kernel: " + ", ".join(map(printItem, list(kernel))))
            items = list(kernel)
            state = set()
            i = 0
            while i < len(items):
                item = items[i]
                if item in state:
                    i += 1
                    continue
                else:
                    state.add(item)
                if item[2] < len(item[1]) and item[1][item[2]] > 0:
                    nt = item[1][item[2]]
                    if item[2] + 1 < len(item[1]):
                        if item[1][item[2] + 1] < 0:
                            items += [(
                                nt, rule[0], 0, item[1][item[2] + 1], rule[1]) for rule in rules[nt]]
                        else:
                            for f in self.firstSets[item[1][item[2] + 1]]:
                                items += [(
                                    nt, rule[0], 0, f, rule[1]) for rule in rules[nt]]
                    else:
                        items += [(
                            nt,
                            rule[0],
                            0,
                            item[1][item[2] + 1] if item[2] + 1 < len(item[1])
                            else item[3],
                            rule[1]) for rule in rules[nt]]
                i += 1
            kernelToInd[kernel] = buildState.stateCount
            indToStateItems[buildState.stateCount] = state
            print("    " + "\n    ".join(map(printItem, list(state))))
            buildState.stateCount += 1
            return buildState.stateCount - 1, True
        buildState.stateCount = 0

        def _reduce(item):

            def do(parser):
                print("Reducing " + printItem(item))
                params = []
                for x in range(len(item[1])):
                    params.append(parser.dataStack.pop())
                    parser.stateStack.pop()
                parser.table[parser.stateStack[-1]][item[0]](parser, item[4](*reversed(params)))
            return do

        def shift(s, symb):
            def do(parser, data=None):
                if data is None:
                    data = parser.tokenizer.pull()
                    print("Shifting " + data)
                else:
                    print("Shifting " + parser.repMap[symb])
                parser.stateStack.append(s)
                parser.dataStack.append(data)
            return do

        def shiftState(kernel, table, rules):
            stateInd, created = buildState(kernel, rules)
            if not created:
                return stateInd
            stateItems = indToStateItems[stateInd]
            shiftMap = defaultdict(list)
            for item in stateItems:
                if len(item[1]) > item[2]:
                    shiftMap[item[1][item[2]]].append((item[0], item[1], item[2] + 1, item[3], item[4]))
            for symb in shiftMap:
                a = shiftState(tuple(shiftMap[symb]), table, rules)
                table[stateInd][symb] = shift(a, symb)
            return stateInd

        def reduceStates(table, rules):
            for stateInd in indToStateItems:
                stateItems = indToStateItems[stateInd]
                for item in stateItems:
                    if len(item[1]) == item[2]:
                        if item[3] in table[stateInd]:
                            print("State: " + str(stateInd))
                            print(table[stateInd][item[3]])
                            print(printItem(item))
                            assert False, "\n".join(map(printItem, list(stateItems)))
                        table[stateInd][item[3]] = _reduce(item)

        startItemTup = tuple([(Parser.START, (self.start,), 0, Parser.END, lambda x : x)])
        shiftState(startItemTup, self.table, self.rules)
        reduceStates(self.table, self.rules)
        self.table[0][Parser.START] = shift(Parser.STOP, Parser.START)

    def parse(self):

        def getTerminal(token):
            if token is None:
                return Parser.END
            for t in self.terminals:
                if t[1](token):
                    return t[0]
            assert False, "Token " + token + " was not matched."

        self.dataStack = []
        self.stateStack = [Parser.START]

        self.tokenizer.tokenize()

        while self.stateStack[-1] != Parser.STOP:
            token = self.tokenizer.peek()
            t = getTerminal(token)
            self.table[self.stateStack[-1]][t](self)

        if len(self.dataStack) != 1:
            assert False, "More than one data item."

        return self.dataStack[0]


