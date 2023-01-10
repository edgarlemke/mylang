#!/usr/bin/python3

from subprocess import Popen, PIPE
from shlex import split


def basictest (msg, expr, expected) :
    print(msg, end="", flush= True)

    stdout, stderr = _popen(expr)

    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}")
        exit()

    if stdout != expected:
        print(f"""FAIL - stdout not corrent:
            expected:   {expected}
            got:        {stdout}""")
        exit()

    print("OK")

def test_parser_rule__expr__quote_value_quote () :
    basictest("TEST PARSER RULE  EXPR -> QUOTE VALUE QUOTE - ", "\\\" \\\"", """(("EXPR" (("QUOTE" "0" "1" "\"") ("VALUE" "1" "2" " ") ("QUOTE" "2" "3" "\""))))""")

def test_parser_rule__list__par_open_par_close () :
    basictest("TEST PARSER RULE  LIST -> PAR_OPEN PAR_CLOSE - ", "()", """(("EXPR" (("LIST" (("PAR_OPEN" "0" "1" "(") ("PAR_CLOSE" "1" "2" ")"))))))""")

def test_parser_rule__list__par_open_expr_par_close () :
    basictest("TEST PARSER RULE  LIST -> PAR_OPEN EXPR PAR_CLOSE - ", "(\\\"abc\\\")", """(("EXPR" (("LIST" (("PAR_OPEN" "0" "1" "(") ("EXPR" (("QUOTE" "1" "2" "\"") ("VALUE" "2" "5" "abc") ("QUOTE" "5" "6" "\""))) ("PAR_CLOSE" "6" "7" ")"))))))""")


def _popen (expr) :
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-parse-tree"
    sp = split(cmd)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
