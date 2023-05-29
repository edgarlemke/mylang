#!/usr/bin/python3
# coding: utf-8

import argparse
import inspect as i
from subprocess import Popen, PIPE
from shlex import split
import unicodedata


def _test(fn_name, expected_stdout, expected_stderr, expr):
    print(f"TEST {fn_name} - ", end="")

    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\""
    p = Popen(
        split(cmd),
        stdout=PIPE,
        stderr=PIPE)
    stdout, stderr = p.communicate()

    stdout_dec = stdout.decode()
    stdout_ok = (expected_stdout == "" and stdout_dec == "") or (expected_stdout != "" and stdout_dec == expected_stdout)

    stderr_dec = stderr.decode()
    stderr_ok = (expected_stderr == "" and stderr_dec == "") or (expected_stderr != "" and expected_stderr in stderr_dec)

    err = False
    if not stderr_ok:
        print(f"""FAIL - stderr not correct:
        expected:   %s
        got:        %s""" % (expected_stderr, stderr_dec))
        err = True

    if not stdout_ok:
        print("""FAIL - stdout not correct:
        expected:   %s
        got:        %s""" % (expected_stdout, stdout_dec))
        err = True

    if err:
        print(f"CMD: %s" % cmd)
        return False

    print("OK")


#
# RUNTIME
# __fn__
def test_fn():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """(fn ((i8 x) (i8 y)) i8 ())\n""",
        "",
        "fn ((i8 x) (i8 y)) i8 ()"
    )


def test_fn_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for fn",
        "fn ((ui8 x)) i8 () wrong"
    )


def test_fn_args():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Function argument has invalid type",
        "fn ((wrong x) (wrong y)) i8 ()"
    )


def test_fn_ret_type():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Function return type has invalid type",
        "fn ((i8 x) (i8 y)) wrong ()"
    )


# __let__
def test_let_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for let",
        "let (i8 x 0) (body) wrong"
    )


# __set__
def test_set():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """()\n""",
        "",
        "set x i8 0"
    )


def test_set_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for set",
        "set x i8 0 wrong"
    )


def test_set_type():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Constant assignment has invalid type",
        "set x wrong 0"
    )


# __macro__
def test_macro_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for macro",
        "macro alias () () wrong"
    )


def test_macro_expansion():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "(() (someop 1 2))\n",
        "",
        """(macro test ('a ! 'b) (someop 'a 'b))
(1 ! 2)"""
    )


# __if__
def test_if_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for if",
        "if (true) () () wrong"
    )


# __data__
def test_data_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for data",
        "data () wrong"
    )


#
#


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
