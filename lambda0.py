#! /usr/bin/env python
import sys
from tokenizer import Tokenizer
from parser import Parser
from re import search
from pprint import pprint
import os
from termcolor import colored

VAR = 0
APP = 1
ABS = 2
EMPTY = 3

bindMap = dict()

def printState(evalStack, msg=None):
    os.system('clear')
    print(msg if msg is not None else '')

    def helper(evalStack, offset):

        if len(evalStack) == 0:
            return ''

        term = evalStack.pop(0)
        branch = -1

        if term[0] == APP:
            if len(evalStack) == 0:
                a, b, c = 'red', 'cyan', 'grey'
                noffset = offset
            else:
                branch = evalStack.pop(0)
                if branch == 1:
                    a, b, c = 'blue', 'grey', 'grey'
                    noffset = offset + 1
                else:
                    a, b, c = 'grey', 'blue', 'grey'
                    noffset = offset + 1 + len(termToString(term[1]))

            res = ((' ' * offset) + colored('(', color=c)
                    + colored(termToString(term[1]), color=a)
                    + colored(termToString(term[2]), color=b)
                    + colored(')', color=c)
                    + '\n' + helper(evalStack, noffset))
        elif term[0] == ABS:
            if len(evalStack) == 0:
                a, b, c = 'magenta', 'green', 'grey'
                noffset = offset
            else:
                branch = evalStack.pop(0)
                a, b, c = 'grey', 'blue', 'grey'
                noffset = offset + 4 + len(bindMap[term[1]])
            res = ((' ' * offset) + colored('([', color=c)
                    + colored(bindMap[term[1]], color=a)
                    + colored(']:', color=c)
                    + colored(termToString(term[2]), color=b)
                    + colored(')', color=c)
                    + '\n' + helper(evalStack, noffset))
        elif term[0] == VAR:
            res = ((' ' * offset) + ' '
                    + (('[' + colored(bindMap[term[1]], color='magenta') + ']')
                        if term[1] in bindMap else colored(term[1], color='yellow')))

        if branch != -1:
            evalStack.insert(0, branch)
        evalStack.insert(0, term)
        return res

    print(helper(evalStack, 0))
    raw_input('(pause)')


def termToString(term):
    if term[0] == APP:
        return ('(' +
            termToString(term[1]) +
            termToString(term[2]) +
            ')')
    elif term[0] == VAR:
        return (' [' + bindMap[term[1]] + '] '
            if term[1] in bindMap else (' ' + term[1] + ' '))
    elif term[0] == ABS:
        return ('(' +
            (('[' + bindMap[term[1]] + ']')
                if term[1] in bindMap else term[1]) +
            ':' + termToString(term[2]) +
            ')')

def rebound(term,stack=[]):
    if term[0] == ABS:
        bindMap[rebound.count] = term[1]
        stack.append((term[1], rebound.count))
        rebound.count += 1
        res = (ABS, stack[-1][1], rebound(term[2], stack))
        stack.pop()
        return res
    elif term[0] == APP:
        return (
            APP,
            rebound(term[1], stack),
            rebound(term[2], stack))
    elif term[0] == VAR:
        for x, n in reversed(stack):
            if term[1] == x:
                return (VAR, n)
        return (VAR, term[1])
rebound.count = 0

def process_term(term, evalStack=[]):

    evalStack.append(term)
    printState(evalStack, "visit term")

    def rebind(b, act, par):
        if act[0] == VAR and act[1] == b:
            return par
        elif act[0] == ABS:
            if act[1] == b:
                return act
            else:
                base = rebind(b, act[2], par)
                return (act if base is None else (ABS, act[1], base))
        elif act[0] == APP:
            base1 = rebind(b, act[1], par)
            base2 = rebind(b, act[2], par)
            return (act if base1 is None and base2 is None
                         else (APP,
                               (act[1] if base1 is None
                                     else base1),
                               (act[2] if base2 is None
                                     else base2)))

    if term[0] == APP:
        evalStack.append(1)
        term = (APP, process_term(term[1], evalStack), term[2])
        evalStack.pop()
        evalStack.pop()
        evalStack.append(term)
        printState(evalStack, "Simplified Left")
        if term[1][0] == ABS:
            rb_term = rebind(term[1][1], term[1][2], term[2])
            term = term[1][2] if rb_term is None else rb_term
            evalStack.pop()
            term = process_term(term, evalStack)
            evalStack.append(term)
            printState(evalStack, 'Term processed')
            evalStack.pop()
            return term

    #if term[0] != VAR:
        #evalStack.append(2)
        #term = (term[0], term[1], process_term(term[2], evalStack))
        #evalStack.pop()
        #evalStack.pop()
        #evalStack.append(term)
        #printState(evalStack, "Simplified Right")

    evalStack.pop()
    return term

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ./lambda0.py source_file')
        sys.exit(0)
    t = Tokenizer(sys.argv[1])
    p = Parser(t)

    t_open = p.add_terminal('(', lambda x: x == Tokenizer.OPEN)
    t_close = p.add_terminal(')', lambda x: x == Tokenizer.CLOSE)
    t_abs = p.add_terminal(':', lambda x: x == Tokenizer.ABS)
    t_bquo = p.add_terminal('`', lambda x: x == Tokenizer.BQUO)
    t_eq = p.add_terminal('=', lambda x: x == Tokenizer.EQ)
    t_comma = p.add_terminal(',', lambda x: x == Tokenizer.COMMA)
    t_var = p.add_terminal(
        'v', lambda x: (search(r'^[^)`(:]+$', x) is not None))

    nt_term = p.add_non_terminal('term')
    nt_single = p.add_non_terminal('single')
    nt_bterm = p.add_non_terminal('bterm')
    nt_formal = p.add_non_terminal('formal')

    p.add_rule(nt_term, (nt_single,), lambda x : x)
    p.add_rule(nt_term, (nt_term, nt_single), lambda t, s: (APP, t, s))

    p.add_rule(nt_single, (t_var,), lambda x: (VAR, x))
    p.add_rule(nt_single, (t_open, nt_term, t_close), lambda o, t, c: t)
    p.add_rule(nt_single, (t_open, nt_bterm, t_close), lambda o, b, c: b)

    def abs_term(f, t):
        if f[1] == EMPTY:
            return (ABS, f[0], t)
        else:
            return (APP, (ABS, f[0], t), f[1])

    p.add_rule(nt_bterm, (nt_formal, t_abs, nt_term), lambda f, a, t: abs_term(f, t))
    p.add_rule(nt_bterm, (nt_formal, t_comma, nt_bterm), lambda f, c, b: abs_term(f, b))

    p.add_rule(nt_formal, (t_var,), lambda v: (v, EMPTY))
    p.add_rule(nt_formal, (t_var, t_eq, nt_term), lambda v, e, t: (v, t))

    p.add_first_set(nt_term,   set([t_open, t_var]))
    p.add_first_set(nt_single, set([t_open, t_var]))
    p.add_first_set(nt_bterm,  set([t_var]))
    p.add_first_set(nt_formal, set([t_var]))

    p.display()

    p.build_table()
    term = p.parse()

    term = rebound(term)

    term = process_term(term)
    print(termToString(term))
