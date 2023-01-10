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

def test_parser_rule__expr_group__expr_space_expr () :
    """
    Tests
        EXPR_GROUP -> EXPR SPACE EXPR
        LIST -> PAR_OPEN EXPR_GROUP PAR_CLOSE
    """
    basictest("TEST PARSER RULE  EXPR_GROUP -> EXPR SPACE EXPR - ", "(\\\"abc\\\" \\\"xyz\\\")", """(("EXPR" (("LIST" (("PAR_OPEN" "0" "1" "(") ("EXPR_GROUP" (("EXPR" (("QUOTE" "1" "2" "\"") ("VALUE" "2" "5" "abc") ("QUOTE" "5" "6" "\""))) ("SPACE" "6" "7" " ") ("EXPR" (("QUOTE" "7" "8" "\"") ("VALUE" "8" "11" "xyz") ("QUOTE" "11" "12" "\""))))) ("PAR_CLOSE" "12" "13" ")"))))))""")

def test_parser_rule__expr_group__expr_group_space_expr () :
    """
    Tests
        EXPR_GROUP -> EXPR_GROUP SPACE EXPR
        LIST -> PAR_OPEN EXPR_GROUP PAR_CLOSE
    """
    basictest(
            "TEST PARSER RULE  EXPR_GROUP -> EXPR_GROUP SPACE EXPR - ",
            "(\\\"abc\\\" \\\"jkl\\\" \\\"xyz\\\")",
            """(("EXPR" (("LIST" (("PAR_OPEN" "0" "1" "(") ("EXPR_GROUP" (("EXPR_GROUP" (("EXPR" (("QUOTE" "1" "2" "\"") ("VALUE" "2" "5" "abc") ("QUOTE" "5" "6" "\""))) ("SPACE" "6" "7" " ") ("EXPR" (("QUOTE" "7" "8" "\"") ("VALUE" "8" "11" "jkl") ("QUOTE" "11" "12" "\""))))) ("SPACE" "12" "13" " ") ("EXPR" (("QUOTE" "13" "14" "\"") ("VALUE" "14" "17" "xyz") ("QUOTE" "17" "18" "\""))))) ("PAR_CLOSE" "18" "19" ")"))))))"""
    )
            

def _popen (expr) :
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-parse-tree"
    sp = split(cmd)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
