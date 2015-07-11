#! /usr/bin/env python
import sys
from tokenizer import Tokenizer
from parser import Parser
from re import search
from pprint import pprint

VAR = 0
APP = 1
ABS = 2
EMPTY = 3

def printTerm(term):
    print("("),
    if term[0] == APP:
        assert len(term) == 3, "APP term has length = " + len(term)
        printTerm(term[1])
        printTerm(term[2])
    elif term[0] == VAR:
        assert len(term) == 2, "VAR term has length = " + len(term)
        printTerm(term[1])
    elif term[0] == ABS:
        assert len(term) == 3, "ABS term has length = " + len(term)
        print(term[1] + " : "),
        printTerm(term[2])

    print(")"),

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
    pprint(term)
