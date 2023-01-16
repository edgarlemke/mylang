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

#def test_parser_rule__expr__value () :
#    basictest("TEST RULE  EXPR -> VALUE - ", "anyvalue", """((EXPR ((VALUE 0 8 anyvalue))))""")

def test_parser_rule__expr__quote_value_quote () :
    basictest("TEST RULE  EXPR -> QUOTE QVALUE QUOTE - ", "\\\" \\\"", """((EXPR ((QUOTE 0 1 "\\\"") (QVALUE 1 2 " ") (QUOTE 2 3 "\\\""))))""")
    
def test_parser_rule__par_group__par_open_par_close () :
    basictest("TEST RULE  PAR_GROUP -> PAR_OPEN PAR_CLOSE - ", "()", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (PAR_CLOSE 1 2 ")"))))))""")

def test_parser_rule__par_group__par_open_expr_par_close () :
    basictest("TEST RULE  PAR_GROUP -> PAR_OPEN EXPR PAR_CLOSE - ", "(\\\"abc\\\")", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (PAR_CLOSE 6 7 ")"))))))""")

def test_parser_rule__expr_group__expr_space_expr () :
    """
    Tests
        EXPR_GROUP -> EXPR SPACE EXPR
        PAR_GROUP -> PAR_OPEN EXPR_GROUP PAR_CLOSE
    """
    basictest("TEST RULE  EXPR_GROUP -> EXPR SPACE EXPR - ", "(\\\"abc\\\" \\\"xyz\\\")", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR_GROUP ((EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (SPACE 6 7 " ") (EXPR ((QUOTE 7 8 "\\\"") (QVALUE 8 11 xyz) (QUOTE 11 12 "\\\""))))) (PAR_CLOSE 12 13 ")"))))))""")

def test_parser_rule__expr_group__expr_group_space_expr () :
    """
    Tests
        EXPR_GROUP -> EXPR_GROUP SPACE EXPR
        PAR_GROUP -> PAR_OPEN EXPR_GROUP PAR_CLOSE
    """
    basictest(
            "TEST RULE  EXPR_GROUP -> EXPR_GROUP SPACE EXPR - ",
            "(\\\"abc\\\" \\\"jkl\\\" \\\"xyz\\\")",
            """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR_GROUP ((EXPR_GROUP ((EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (SPACE 6 7 " ") (EXPR ((QUOTE 7 8 "\\\"") (QVALUE 8 11 jkl) (QUOTE 11 12 "\\\""))))) (SPACE 12 13 " ") (EXPR ((QUOTE 13 14 "\\\"") (QVALUE 14 17 xyz) (QUOTE 17 18 "\\\""))))) (PAR_CLOSE 18 19 ")"))))))"""
    )


def test_parser_rule_fn_decl_0 () :
    basictest(
            "TEST RULE  FN_DECL 0 - ",
            """fn main  ui8 x  ui8
\tret x""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8))))))"""
    )

def test_parser_rule_fn_decl_1 () :
    basictest(
            "TEST RULE  FN_DECL 1 - ",
            """fn main  ui8 x ui8 y  ui8
\tret x""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (NAMEPAIR ((NAME 15 18 ui8) (SPACE 18 19 " ") (NAME 19 20 y))))) (SPACE 20 21 " ") (SPACE 21 22 " ") (NAME 22 25 ui8))))))"""
    )


def test_invalid_syntax () :
    print("TEST INVALID SYNTAX - ", end="")

    stdout, stderr = _popen("())")

    expected = "Invalid syntax!"
    if not (expected in stderr):
        print(f"""FAIL - stderr not correct
                expected: {expected}
                got: {stderr}""")
        exit()

    print("OK")


def _popen (expr) :
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-parse-tree"
    sp = split(cmd)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
