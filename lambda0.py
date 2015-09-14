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
    return
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

    tzer = Tokenizer(sys.argv[1])

    t_open  = tzer.add_token_class(rep='(', regex=r'(')
    t_close = tzer.add_token_class(rep=')', regex=r')')
    t_abs   = tzer.add_token_class(rep=':', regex=r':')
    t_eq    = tzer.add_token_class(rep='=', regex=r'=')
    t_comma = tzer.add_token_class(rep=',', regex=r',')
    t_as    = tzer.add_token_class(rep='@', regex=r'@')
    t_var   = tzer.add_token_class(rep='VAR', regex=r'[^():=,@]*')

    p = Parser(tzer)

    # nt_term   = p.add_non_terminal('term')
    # nt_single = p.add_non_terminal('single')
    # nt_bterm  = p.add_non_terminal('bterm')
    # nt_formal = p.add_non_terminal('formal')

    class NT_Term(Parser.NonTerminal):

        rep = 'term'

        @classmethod
        def expansions(cls):

            yield Parser.ExpansionRule(
                (NT_Single,),
                lambda nt_single_sv: cls(nt_single_sv)
            )

            yield Parser.ExpansionRule(
                (NT_Term, NT_Single),
                lambda nt_term, nt_single: cls(APPTerm(nt_term_sv, nt_single_sv))
            )

    # p.add_rule(nt_term, (nt_single,), lambda x : x)
    # p.add_rule(nt_term, (nt_term, nt_single), lambda t, s: (APP, t, s))

    class NT_Single(Parser.NonTerminal):

        rep = 'single'

        @classmethod
        def expansions(cls):

            yield Parser.ExpansionRule(
                (t_var,),
                lambda t_var: cls(VARTerm(t_var))
            )

            yield Parser.ExpansionRule(
                (t_open, NT_Term_t_close),
                lambda t_open, nt_term_sv, t_close: cls(nt_term_sv)
            )

            yield Parser.ExpansionRule(
                (t_open, NT_BTerm, t_close),
                lambda t_open, nt_bterm_sv, t_close: cls(nt_bterm_sv)
            )

    # p.add_rule(nt_single, (t_var,), lambda x: (VAR, x))
    # p.add_rule(nt_single, (t_open, nt_term, t_close), lambda o, t, c: t)
    # p.add_rule(nt_single, (t_open, nt_bterm, t_close), lambda o, b, c: b)

    class NT_BTerm(Parser.NonTerminal):

        rep = 'bterm'

        @classmethod
        def expansions(cls):

            def abs_term(formal, term):
                if f.assn is None:
                    return ABSTerm(f.var, term)
                else:
                    return APPTerm(ABSTerm(f.var, term), f.assn)

            yield Parser.ExpansionRule(
                (NT_Formal, t_abs, NT_Term),
                (lambda nt_formal, t_abs, nt_term_sv:
                    abs_term(nt_formal, nt_term_sv))
            )

            yield Parser.ExpansionRule(
                (NT_Formal, t_comma, t_abs, NT_Term),
                (lambda nt_formal, t_comma, t_abs, nt_term_sv:
                    abs_term(nt_formal, nt_term_sv))
            )

            yield Parser.ExpansionRule(
                (NT_Formal, t_comma, NT_BTerm),
                (lambda nt_formal, t_comma, nt_bterm_sv:
                    abs_term(nt_formal, nt_bterm_sv))
            )

    # p.add_rule(nt_bterm, (nt_formal, t_abs, nt_term), lambda f, a, t: abs_term(f, t))
    # p.add_rule(nt_bterm, (nt_formal, t_comma, t_abs, nt_term), lambda f, c, a, t: abs_term(f, t))
    # p.add_rule(nt_bterm, (nt_formal, t_comma, nt_bterm), lambda f, c, b: abs_term(f, b))

    class NT_Formal(Parser.NonTerminal):

        rep = 'formal'

        def __init__(self, var, assn=None):
            super(NT_Formal, self).__init__()
            self.var = var
            self.assn = assn

        @classmethod
        def expansions(cls):

            yield Parser.ExpansionRule(
                (t_var,), lambda t_var: cls(t_var)
            )

            yield Parser.ExpansionRule(
                (t_var, t_eq, NT_Term),
                lambda t_var, t_eq, nt_term_sv: cls(t_var, nt_term_sv)
            )

