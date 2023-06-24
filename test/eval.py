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
        """(fn ((int x) (int y)) int ())\n""",
        "",
        "fn ((int x) (int y)) int ()"
    )


def test_fn_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for fn",
        "fn ((uint x)) int () wrong"
    )


def test_fn_args():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Function argument has invalid type",
        "fn ((wrong x) (wrong y)) int ()"
    )


def test_fn_ret_type():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Function return type has invalid type",
        "fn ((int x) (int y)) wrong ()"
    )


def test_fn_arg_type_infer_int():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( ((int x)) int () ) ))
(myfn 1234)"""
    )


def test_fn_arg_type_infer_float():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( ((float x)) float () ) ))
(myfn 3.14)"""
    )


def test_fn_arg_type_infer_bool_true():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( ((bool x)) bool () ) ))
(myfn true)"""
    )


def test_fn_arg_type_infer_bool_false():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( ((bool x)) bool () ) ))
(myfn false)"""
    )


def test_fn_arg_name():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( ((bool x)) bool () ) ))
(set const mybool (bool true))
(myfn mybool)"""
    )


def test_fn_arg_fncall():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( ((bool x)) bool () ) ))
(set const retbool (fn (() bool (data (bool true)) ) ))
(myfn (retbool ()))"""
    )


# __let__
def test_let_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for let",
        "let (int x 0) (body) wrong"
    )


# __set__
def test_set_const():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """()\n""",
        "",
        "set const x (int 0)"
    )


def test_set_node_size():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for set",
        "set const x (int 0) wrong"
    )


def test_set_type():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Constant assignment has invalid type",
        "set const x (wrong 0)"
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
        "((1 2))\n",
        "",
        """(macro test ('a ! 'b) (data ('a 'b)))
(1 ! 2)"""
    )


def test_default_macros():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "(() (1 2))\n",
        "",
        """(1 + 2)"""
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


# other tests
# ptr
def test_ptr():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        "set const x (ptr int 0xdeadbeef)"
    )


# struct
def test_struct_decl():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        "set const mystruct (struct ((mut x int)))"
    )


def test_struct_init():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const mystruct (struct ((mut x int))))
(set const mystruct_ (mystruct (1)))"""
    )


def test_struct_member_access():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """(set const mystruct (struct ((mut x int))))
(set const mystruct_ (mystruct (1)))
(mystruct_ x)"""
    )


def test_struct_deep_member_access():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """(set const mystruct (struct ((mut member_x int))))
(set const mystruct2 (struct ((const member_mystruct mystruct))))
(set const st_mystruct (mystruct (1)))
(set const st_mystruct2 (mystruct2 (st_mystruct)))
(st_mystruct2 member_mystruct member_x)"""
    )


def test_struct_member_set():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 2))\n",
        "",
        """(set const mystruct (struct ((mut x int))))
(set const mystruct_ (mystruct (1)))
(set mut (mystruct_ x) (int 2))
(mystruct_ x)"""
    )


def test_struct_member_set_wrong_type():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Setting struct member with invalid value type",
        """(set const mystruct (struct ((mut x int))))
(set const mystruct_ (mystruct (1)))
(set mut (mystruct_ x) (float 3.14))
(mystruct_ x)"""
    )


def test_struct_member_access_for_name():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """(set const mystruct (struct ((mut x int))))
(set const mystruct_ (mystruct (1)))
(set const randomvar (int (mystruct_ x)))
(randomvar)"""
    )


def test_struct_init_wrong_number_of_members():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Initializing struct with wrong number of member values",
        """(set const mystruct (struct ((mut x int)(mut y int))))
(set const mystruct_ (mystruct (1)))
"""
    )


def test_struct_init_wrong_type_for_member():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Initializing struct with invalid value type for member",
        """(set const mystruct (struct ((mut x int)(mut y int))))
(set const mystruct_ (mystruct (1 3.14)))
"""
    )


# other tests
def test_eval_name():
    _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """(set const randomvar (int 1))
(randomvar)"""
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
