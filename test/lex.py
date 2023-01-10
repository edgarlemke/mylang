#!/usr/bin/python3
# coding: utf-8

import argparse
from subprocess import Popen, PIPE
from shlex import split
import unicodedata


def basictest (msg, expected, expr):
    print(msg, end="")

    p = Popen(split(f"/usr/bin/python3 ../lex.py --expr \"{expr}\""), stdout= PIPE, stderr= PIPE)
    stdout, stderr = p.communicate()

    stdout_dec = stdout.decode()
    stdout_ok = (stdout_dec == expected)

    if stderr != b'':
        print("FAIL - stderr not empty: %s" % stderr)
        exit()

    if not stdout_ok:
        print("""FAIL - stdout not correct:
        expected:   %s
        got:        %s""" % (expected,stdout_dec))
        exit()

    print("OK")


def test_par_open () :
    """
    `(` expresssion should return only one PAR_OPEN token
    """
    basictest("TEST PAR_OPEN - ", "((PAR_OPEN 0 1 \"(\"))\n", "(")


def test_par_close () :
    """
    `)` expression should return only one PAR_CLOSE token
    """
    basictest("TEST PAR_CLOSE - ", "((PAR_CLOSE 0 1 \")\"))\n", ")")


def test_space () :
    """
    ` ` expression should return only one SPACE token
    """
    basictest("TEST SPACE - ", "((SPACE 0 1 \" \"))\n", " ")


def test_par_open_space_par_close () :
    """
    `( )` expression should return three tokens == PAR_OPEN, SPACE, PAR_CLOSE
    
    list_print() is tested for absence of spaces between lists inside a list
    tokenize() is tested for ordering of tokens
    """
    basictest(
            "TEST PAR_OPEN SPACE PAR_CLOSE - ",
            """((PAR_OPEN 0 1 "(") (SPACE 1 2 " ") (PAR_CLOSE 2 3 ")"))\n""",
            "( )"
    )


def test_quote () :
    """
    `"` expression should return only one QUOTE token
    """
    expr = "\\\""
    basictest("TEST QUOTE - ", """((QUOTE 0 1 "\\\""))\n""", expr)

def test_value () :
    """
    `mynametoken` expression should return only one VALUE token
    """
    basictest("TEST VALUE - ", """((VALUE 0 11 mynametoken))\n""", "mynametoken")

def test_abc_xyz () :
    """
    `(\"abc\" \"xyz\")` expression should return:
        one PAR_OPEN token
        one QUOTE token
        one VALUE token
        one QUOTE token
        one SPACE token
        one QUOTE token
        one VALUE token
        one QUOTE token
        one PAR_CLOSE token
    """ 
    basictest(
            "TEST (\"abc\" \"xyz\") - ",
            """((PAR_OPEN 0 1 "(") (QUOTE 1 2 "\\\"") (VALUE 2 5 abc) (QUOTE 5 6 "\\\"") (SPACE 6 7 " ") (QUOTE 7 8 "\\\"") (VALUE 8 11 xyz) (QUOTE 11 12 "\\\"") (PAR_CLOSE 12 13 ")"))\n""",
            "(\\\"abc\\\" \\\"xyz\\\")"
    )



def _test_unicode (i) :
    ch = chr(i)
    cat = unicodedata.category(ch)

    # characters which need escaping for the test to work
    escape = ['\'', ' ']
    if ch in escape:
        expr = f"\"\{ch}\""
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
        p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding="utf-8")
        stdout, stderr = p.communicate()

    except Exception as e:
        return (False, f"FAIL - char {i} {ch} - {sp} - {e}")


    stdout_dec = stdout
    if ch in ["\"","\\"]:
        expected = f"""(("QUOTE" "0" "1" "\"")("VALUE" "1" "3" "\{ch}")("QUOTE" "3" "4" "\""))\n"""
    else:
        expected = f"""(("QUOTE" "0" "1" "\"")("VALUE" "1" "2" "{ch}")("QUOTE" "2" "3" "\""))\n"""

    hex_expected = [(ord(ch),ch) for ch in expected]
    hex_stdout = [(ord(ch),ch) for ch in stdout_dec]

    if stderr != "":
        msg = f"FAIL - char {i} {ch} - {sp} - stderr not empty: {stderr}"
        return (False,msg)

    if stdout_dec != expected:
        msg = f"""FAIL - char {i} {ch} - {sp} - stdout not correct:
        expected:   {expected}
                    {hex_expected}
        got:        {stdout_dec}
                    {hex_stdout}"""
        return (False,msg)

    return (True,"")


def _get_codepoints () : 
    import sys

    codepoints = []

    for i in range(0,sys.maxunicode+1):
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


def test_quoted_unicode () :
    """
    All valid Unicode chars between QUOTE tokens should return a VALUE token
    " char should be escaped
    """
    print("TEST QUOTED UNICODE - ", end="", flush= True)

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
                print(msg, flush= True)
                exit()

    print("OK")


def test_check_nontokenized_start () :
    print("TEST CHECK NONTOKENIZED START - ", end="", flush= True)

    stdout, stderr = _popen("!@#()")
    msg = "Exception: Non-tokenized range at start: 0 3  \"!@#\""

    if not (msg in stderr):
        print(f"FAIL - non-tokenized @ char at start\nstderr: {stderr}", flush= True)
        exit()

    print("OK")

def test_check_nontokenized_middle () :
    print("TEST CHECK NONTOKENIZED MIDDLE - ", end="", flush= True)

    stdout, stderr = _popen("(!@#)")
    msg = "Exception: Non-tokenized range at middle: 1 4  \"!@#\"" 

    if not (msg in stderr):
        print(f"FAIL - non-tokenized @ char at middle\nstderr: {stderr}", flush= True)
        exit()

    print("OK")

def test_check_nontokenized_end () :
    print("TEST CHECK NONTOKENIZED END - ", end="", flush= True)

    stdout, stderr = _popen("()!@#")
    msg = "Exception: Non-tokenized range at end: 2 5  \"!@#\"" 

    if not (msg in stderr):
        print(f"FAIL - non-tokenized @ char at end\nstderr: {stderr}", flush= True)
        #print(stdout)
        exit()

    print("OK")



def _popen (expr) :
    cmd = f"/usr/bin/python3 ../lex.py --expr \"{expr}\""
    sp = split(cmd)
    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action= "store_true")
    args = parser.parse_args()

    fast = args.fast


    slow = ["test_quoted_unicode"]

    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:

        if fast and t in slow:
            continue

        eval(f"{t}()")
