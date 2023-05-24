#!/usr/bin/python3
# coding: utf-8

import argparse
import inspect as i
from subprocess import Popen, PIPE
from shlex import split
import unicodedata


def _test(fn_name, expected, expr):
    print(f"TEST {fn_name} - ", end="")

    p = Popen(
        split(f"/usr/bin/python3 ../lex.py --expr \"{expr}\""),
        stdout=PIPE,
        stderr=PIPE)
    stdout, stderr = p.communicate()

    stdout_dec = stdout.decode()
    stdout_ok = (stdout_dec == expected)

    err = False
    if stderr != b'':
        print(f"FAIL - stderr not empty: {stderr}")
        err = True

    if not stdout_ok:
        print("""FAIL - stdout not correct:
        expected:   %s
        got:        %s""" % (expected, stdout_dec))
        err = True

    if err:
        return False

    print("OK")


def test_par_open():
    """
    `(` expresssion should return only one PAR_OPEN token
    """
    _test(
        i.getframeinfo(
            i.currentframe()).function,
        "((TOKEN PAR_OPEN 0 1 \"(\"))\n",
        "(")


def test_par_close():
    """
    `)` expression should return only one PAR_CLOSE token
    """
    _test(
        i.getframeinfo(
            i.currentframe()).function,
        "((TOKEN PAR_CLOSE 0 1 \")\"))\n",
        ")")


def test_space():
    """
    ` ` expression should return only one SPACE token
    """
    _test(
        i.getframeinfo(
            i.currentframe()).function,
        "((TOKEN SPACE 0 1 \" \"))\n",
        " ")


def test_par_open_space_par_close():
    """
    `( )` expression should return three tokens == PAR_OPEN, SPACE, PAR_CLOSE

    list_print() is tested for absence of spaces between lists inside a list
    tokenize() is tested for ordering of tokens
    """
    _test(
        i.getframeinfo(i.currentframe()).function,
        """((TOKEN PAR_OPEN 0 1 "(") (TOKEN SPACE 1 2 " ") (TOKEN PAR_CLOSE 2 3 ")"))\n""",
        "( )"
    )


def test_quote():
    """
    `"` expression should return only one QUOTE token
    """
    expr = "\\\""
    _test(
        i.getframeinfo(
            i.currentframe()).function,
        """((TOKEN QUOTE 0 1 "\\\""))\n""",
        expr)

# def test_value () :
#    """
#    `mynametoken` expression should return only one VALUE token
#    """
#    _test(i.getframeinfo( i.currentframe() ).function, """((VALUE 0 11 mynametoken))\n""", "mynametoken")


def test_lit_int():
    _test(
        i.getframeinfo(
            i.currentframe()).function,
        """((TOKEN LIT 0 3 123))\n""",
        "123")


def test_lit_float():
    _test(
        i.getframeinfo(
            i.currentframe()).function,
        """((TOKEN LIT 0 4 3.14))\n""",
        "3.14")


def test_abc_xyz():
    """
    `(\"abc\" \"xyz\")` expression should return:
        one PAR_OPEN token
        one QUOTE token
        one LIT token
        one QUOTE token
        one SPACE token
        one QUOTE token
        one LIT token
        one QUOTE token
        one PAR_CLOSE token
    """
    _test(
        i.getframeinfo(i.currentframe()).function,
        """((TOKEN PAR_OPEN 0 1 "(") (TOKEN QUOTE 1 2 "\\\"") (TOKEN LIT 2 5 abc) (TOKEN QUOTE 5 6 "\\\"") (TOKEN SPACE 6 7 " ") (TOKEN QUOTE 7 8 "\\\"") (TOKEN LIT 8 11 xyz) (TOKEN QUOTE 11 12 "\\\"") (TOKEN PAR_CLOSE 12 13 ")"))\n""",
        "(\\\"abc\\\" \\\"xyz\\\")"
    )


def _test_unicode(i):
    ch = chr(i)
    cat = unicodedata.category(ch)

    # characters which need escaping for the test to work
    escape = ['\'', ' ']
    if ch in escape:
        expr = f"\"\\{ch}\""
    # escaping for " char
    elif ch == "\"":
        expr = "\\\\\\\""
    # escaping for \ char
    elif ch == "\\":
        expr = "\\\\\\\\"
    # other characters
    else:
        expr = f"\"{ch}\""

    cmd = f"""/usr/bin/python3 ../lex.py --expr "\\\"{expr}\\\"" """
    sp = split(cmd)

    try:
        p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
        stdout, stderr = p.communicate()

    except Exception as e:
        return (False, f"FAIL - char {i} {ch} - {sp} - {e}")

    stdout_dec = stdout
    if ch in ["\"", "\\"]:
        expected = f"""(("QUOTE" "0" "1" "\"")("VALUE" "1" "3" "\\{ch}")("QUOTE" "3" "4" "\""))\n"""
    else:
        expected = f"""(("QUOTE" "0" "1" "\"")("VALUE" "1" "2" "{ch}")("QUOTE" "2" "3" "\""))\n"""

    hex_expected = [(ord(ch), ch) for ch in expected]
    hex_stdout = [(ord(ch), ch) for ch in stdout_dec]

    if stderr != "":
        msg = f"FAIL - char {i} {ch} - {sp} - stderr not empty: {stderr}"
        return (False, msg)

    if stdout_dec != expected:
        msg = f"""FAIL - char {i} {ch} - {sp} - stdout not correct:
        expected:   {expected}
                    {hex_expected}
        got:        {stdout_dec}
                    {hex_stdout}"""
        return (False, msg)

    return (True, "")


def _get_codepoints():
    import sys

    codepoints = []

    for i in range(0, sys.maxunicode + 1):
        ch = chr(i)
        ucat = unicodedata.category(ch)

        # exclude control characters
        vcats = [
            #                'Cc', 'Cf', 'Cn', 'Co', 'Cs',
            'Ll', 'Lm', 'Lo', 'Lt', 'Lu',
            'Mc', 'Me', 'Mn',
            'Nd', 'Nl', 'No',
            'Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps',
            'Sc', 'Sk', 'Sm', 'So',
            'Zl', 'Zp', 'Zs'
        ]
        if ucat not in vcats:
            continue

        codepoints.append(i)

    return codepoints


def test_quoted_unicode():
    """
    All valid Unicode chars between QUOTE tokens should return a VALUE token
    " char should be escaped
    """
    import inspect as i
    print(
        f"TEST {i.getframeinfo( i.currentframe() ).function} - ",
        end="",
        flush=True)

    from multiprocessing import Pool

    codepoints = _get_codepoints()
    with Pool() as p:
        results = []

        for i in codepoints:
            ch = chr(i)

            r = p.apply_async(_test_unicode, args=(i,))
            results.append(r)

        for r in results:
            ok, msg = r.get()
            if ok is False:
                print(msg, flush=True)
                exit()

    print("OK")


# def test_use():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((USE 0 3 use))\n",
#        "use")
#
#
# def test_fn():
#    _test(i.getframeinfo(i.currentframe()).function, "((FN 0 2 fn))\n", "fn")
#
# def test_call () :
# _test(i.getframeinfo( i.currentframe() ).function, "((CALL 0 4 call))\n", "call")
#
#
# def test_ret():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((RET 0 3 ret))\n",
#        "ret")
#
#
# def test_set():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((SET 0 3 set))\n",
#        "set")
#
#
# def test_mut():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((MUT 0 3 mut))\n",
#        "mut")
#
#
# def test_res():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((RES 0 3 res))\n",
#        "res")
#
#
# def test_if():
#    _test(i.getframeinfo(i.currentframe()).function, "((IF 0 2 if))\n", "if")
#
#
# def test_else():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((ELSE 0 4 else))\n",
#        "else")
#
#
# def test_elif():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((ELIF 0 4 elif))\n",
#        "elif")
#
#
# def test_while():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((WHILE 0 5 while))\n",
#        "while")
#
#
# def test_for():
#    _test(
#        i.getframeinfo(
#            i.currentframe()).function,
#        "((FOR 0 3 for))\n",
#        "for")
#
#
# def test_comment():
#    _test(
#        i.getframeinfo(i.currentframe()).function,
#        "()\n",
#        "# comment\n"
#    )


def test_no_token_match():
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    p = Popen(split("/usr/bin/python3 ../lex.py --expr \"\""),
              stdout=PIPE, stderr=PIPE, encoding="utf-8")
    stdout, stderr = p.communicate()

    expected = "No token match!"

    if not (expected in stderr):
        print(f"""FAIL - stderr not correct:
        expected: {expected}
        got: {stderr}""")
        exit()

    print("OK")


def test_check_nontokenized_start():
    print(
        f"TEST {i.getframeinfo( i.currentframe() ).function} - ",
        end="",
        flush=True)

    stdout, stderr = _popen("@()")
    msg = "Exception: Non-tokenized range at start: 0 1  \"@\""

    if not (msg in stderr):
        print(
            f"FAIL - non-tokenized @ char at start\nstderr: {stderr}",
            flush=True)
        exit()

    print("OK")


def test_check_nontokenized_middle():
    print(
        f"TEST {i.getframeinfo( i.currentframe() ).function} - ",
        end="",
        flush=True)

    stdout, stderr = _popen("(@)")
    msg = "Exception: Non-tokenized range at middle: 1 2  \"@\""

    if not (msg in stderr):
        print(
            f"FAIL - non-tokenized @ char at middle\nstderr: {stderr}",
            flush=True)
        exit()

    print("OK")


def test_check_nontokenized_end():
    print(
        f"TEST {i.getframeinfo( i.currentframe() ).function} - ",
        end="",
        flush=True)

    stdout, stderr = _popen("()@")
    msg = "Exception: Non-tokenized range at end: 2 3  \"@\""

    if not (msg in stderr):
        print(
            f"FAIL - non-tokenized @ char at end\nstderr: {stderr}",
            flush=True)
        # print(stdout)
        exit()

    print("OK")


def test_check_no_argument():
    print(
        f"TEST {i.getframeinfo( i.currentframe() ).function} - ",
        end="",
        flush=True)

    p = Popen(
        split("/usr/bin/python3 ../lex.py"),
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


def _popen(expr):
    cmd = f"/usr/bin/python3 ../lex.py --expr \"{expr}\""
    sp = split(cmd)
    p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    return p.communicate()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fast", action="store_true")
    group.add_argument("-f")
    args = parser.parse_args()

    if args.f is None:
        fast = args.fast
        slow = ["test_quoted_unicode"]
        tests = [t for t in globals() if t[0:5] == "test_"]
        for t in tests:

            if fast and t in slow:
                continue

            eval(f"{t}()")
    else:
        eval(f"{args.f}()")
