#!/usr/bin/python3

import inspect as i
from subprocess import Popen, PIPE
from shlex import split


def _test(fn_name, expr, expected):
    msg = f"TEST {fn_name} - "
    print(msg, end="", flush=True)

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


def test_list_print_quoting():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """(\\\"(\\\" \\\")\\\" \\\" \\\")""",
        """((PAR_OPEN 0 1 "(") (QUOTE 1 2 "\\\"") (QVALUE 2 3 "(") (QUOTE 3 4 "\\\"") (SPACE 4 5 " ") (QUOTE 5 6 "\\\"") (QVALUE 6 7 ")") (QUOTE 7 8 "\\\"") (SPACE 8 9 " ") (QUOTE 9 10 "\\\"") (QVALUE 10 11 " ") (QUOTE 11 12 "\\\"") (PAR_CLOSE 12 13 ")"))\n"""
    )


def test_list_print_quoting_quote_value():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    cmd = "/usr/bin/python3 ../lex.py --expr"
    sp = split(cmd) + ["(\"\\\"\")"]
    # print(sp)

    p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
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


def test_check_no_argument():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    p = Popen(
        split("/usr/bin/python3 ../run.py"),
        stdout=PIPE,
        stderr=PIPE,
        encoding="utf-8")
    stdout, stderr = p.communicate()

    expected = "Either --src or --expr argument must be provided"

    if not (expected in stderr):
        print(f"""FAIL - stderr not correct:
        expected: {expected}
        got: {stderr}""")
        exit()

    print("OK")


def test_print_token_list():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    expr = """fn main  (ui8 x)  ui8
\tnop
"""

    p = Popen(
        split(
            f"/usr/bin/python3 ../run.py --expr=\"{expr}\" --print-token-list"),
        stdout=PIPE,
        encoding="utf-8")
    stdout, stderr = p.communicate()

    expected_stdout = """((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (PAR_OPEN 9 10 "(") (NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x) (PAR_CLOSE 15 16 ")") (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK_START 0) (NOP 23 26 nop) (BLOCK_END 0))"""
    expected_stderr = None

    err = False
    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
        expected: {expected_stdout}
        got: {stdout}""")
        err = True

    if stderr != expected_stderr:
        print(f"""FAIL - stderr not correct:
        expected: {expected_stderr}
        got: {stderr}""")
        err = True

    if err:
        return

    print("OK")


def test_print_parse_tree():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    expr = """fn main  (ui8 x)  ui8
\tnop
"""

    p = Popen(
        split(
            f"/usr/bin/python3 ../run.py --expr=\"{expr}\" --print-parse-tree"),
        stdout=PIPE,
        encoding="utf-8")
    stdout, stderr = p.communicate()

    expected_stdout = """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 23 26 nop))) (BLOCK_END 0))))))))"""
    expected_stderr = None

    err = False
    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
        expected: {expected_stdout}
        got: {stdout}""")
        err = True

    if stderr != expected_stderr:
        print(f"""FAIL - stderr not correct:
        expected: {expected_stderr}
        got: {stderr}""")
        err = True

    if err:
        return

    print("OK")


def test_print_raw_ast():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    expr = """fn main  (ui8 x)  ui8
\tnop
"""

    p = Popen(
        split(f"/usr/bin/python3 ../run.py --expr=\"{expr}\" --print-raw-ast"),
        stdout=PIPE,
        encoding="utf-8")
    stdout, stderr = p.communicate()

    expected_stdout = """(EXPR (FN_DECL ((NAME main) (ARG_PAR_GROUP (((NAME ui8) (NAME x)))) (NAME ui8) ((EXPR (NOP))))))"""
    expected_stderr = None

    err = False
    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
        expected: {expected_stdout}
        got: {stdout}""")
        err = True

    if stderr != expected_stderr:
        print(f"""FAIL - stderr not correct:
        expected: {expected_stderr}
        got: {stderr}""")
        err = True

    if err:
        return

    print("OK")


def test_print_symbol_table():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    expr = """fn main  (ui8 x)  ui8
\tnop
"""

    p = Popen(
        split(
            f"/usr/bin/python3 ../run.py --expr=\"{expr}\" --print-symbol-table"),
        stdout=PIPE,
        encoding="utf-8")
    stdout, stderr = p.communicate()

    expected_stdout = """(((fn ui8) 2 0))(((fn_arg ui8) 5 1))"""
    expected_stderr = None

    err = False
    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
        expected: {expected_stdout}
        got: {stdout}""")
        err = True

    if stderr != expected_stderr:
        print(f"""FAIL - stderr not correct:
        expected: {expected_stderr}
        got: {stderr}""")
        err = True

    if err:
        return

    print("OK")


def test_print_final_ast():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    expr = """fn main  (ui8 x)  ui8
\tnop
"""

    p = Popen(
        split(
            f"/usr/bin/python3 ../run.py --expr=\"{expr}\" --print-final-ast"),
        stdout=PIPE,
        encoding="utf-8")
    stdout, stderr = p.communicate()

    expected_stdout = """((EXPR None (1)) (FN_DECL 0 (2 3 6 7)) (NAME main 1 ()) (ARG_PAR_GROUP 1 (4 5)) (NAME ui8 3 ()) (NAME x 3 ()) (TYPE ui8 1 ()) (EXPR 1 (8)) (NOP 7 ()))"""
    expected_stderr = None

    err = False
    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
        expected: {expected_stdout}
        got: {stdout}""")
        err = True

    if stderr != expected_stderr:
        print(f"""FAIL - stderr not correct:
        expected: {expected_stderr}
        got: {stderr}""")
        err = True

    if err:
        return

    print("OK")


def _popen(expr):
    cmd = f"/usr/bin/python3 ../lex.py --expr \"{expr}\""
    sp = split(cmd)
    # print(sp)

    p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    return p.communicate()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f")
    args = parser.parse_args()

    if args.f is None:
        tests = [t for t in globals() if t[0:5] == "test_"]
        for t in tests:
            eval(f"{t}()")

    else:
        eval(f"{args.f}()")
