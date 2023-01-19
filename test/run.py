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


def test_list_print_quoting () :
    basictest(
            "TEST LIST PRINT QUOTING - ",
            """(\\\"(\\\" \\\")\\\" \\\" \\\")""",
            """((PAR_OPEN 0 1 "(") (QUOTE 1 2 "\\\"") (QVALUE 2 3 "(") (QUOTE 3 4 "\\\"") (SPACE 4 5 " ") (QUOTE 5 6 "\\\"") (QVALUE 6 7 ")") (QUOTE 7 8 "\\\"") (SPACE 8 9 " ") (QUOTE 9 10 "\\\"") (QVALUE 10 11 " ") (QUOTE 11 12 "\\\"") (PAR_CLOSE 12 13 ")"))\n"""
    )

def test_list_print_quoting_quote_value () :
    print("TEST LIST PRINT QUOTING QUOTE QVALUE - ", end="")

    cmd = "/usr/bin/python3 ../lex.py --expr"
    sp = split(cmd) + ["(\"\\\"\")"]
    #print(sp)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    stdout, stderr = p.communicate()

    expected = """((PAR_OPEN 0 1 "(") (QUOTE 1 2 "\\\"") (QVALUE 2 4 "\\\"") (QUOTE 4 5 "\\\"") (PAR_CLOSE 5 6 ")"))\n"""

    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}")
        exit()

    if stdout != expected:
        print(f"""FAIL - stdout not corrent:
            expected:   {expected}
            got:        {stdout}""")
        exit()

    print("OK")
    

def test_check_no_argument () :
    print("TEST CHECK NO ARGUMENT - ", end= "", flush= True)

    p = Popen(split("/usr/bin/python3 ../run.py"), stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    stdout, stderr = p.communicate()

    expected = "Either --src or --expr argument must be provided"

    if not (expected in stderr):
        print(f"""FAIL - stderr not correct: 
        expected: {expected}
        got: {stderr}""")
        exit()

    print("OK")



def _popen (expr) :
    cmd = f"/usr/bin/python3 ../lex.py --expr \"{expr}\""
    sp = split(cmd)
    #print(sp)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
