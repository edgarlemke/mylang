#!/usr/bin/python3
# coding: utf-8

import argparse
import inspect as i
from subprocess import Popen, PIPE
from shlex import split

OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def _test(fn_name, expected_stdout, expected_stderr, expr):
    print(f"TEST {fn_name} - ", end="")

    cmd = f"/usr/bin/python3 ../frontend/run.py --print-output --compile-time-scope --expr \"{expr}\""
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
        print(FAIL)

        print(f"""stderr not correct:
        expected:   %s
        got:        %s""" % (expected_stderr, stderr_dec))
        err = True

    if not stdout_ok:
        if not err:
            print(FAIL)

        print("""stdout not correct:
        expected:   %s
        got:        %s""" % (expected_stdout, stdout_dec))
        err = True

    if err:
        print(f"CMD: %s" % cmd)
        return False

    print(OK)
    return True


#
# RUNTIME
# __data__
def test_data():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """((abc 123))\n""",
        "",
        "data abc 123"
    )


# __fn__
def test_fn():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """((fn (x int y int) int ()))\n""",
        "",
        "fn (x int  y int) int ()"
    )


def test_fn_node_size():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for fn",
        "fn (x uint) int () wrong"
    )


def test_fn_without_args():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set mut x (fn (() () ())))
(x ())
"""
    )


def test_fn_arg_type_infer_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """set const myfn (fn ( (x int) int () ) )
myfn 1234"""
    )


def test_fn_arg_type_infer_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( (x float) float () ) ))
(myfn 3.14)"""
    )


def test_fn_arg_type_infer_bool_true():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( (x bool) bool () ) ))
(myfn true)"""
    )


def test_fn_arg_type_infer_bool_false():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const myfn (fn ( (x bool) bool () ) ))
(myfn false)"""
    )


def test_fn_arg_name():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((bool true))\n",
        "",
        """set const myfn (fn ( (x bool) bool
	x
))
set const mybool (bool true)
myfn mybool"""
    )


def test_fn_arg_fncall():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """set const myfn (fn ( (x bool) bool () ))
set const retbool (fn ( () bool ((data bool true)) ))
myfn (retbool ())"""
    )


def test_fn_arg_inside_scope():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """set const myfn (fn ( (x int) int
	x
) )
myfn 1
"""
    )


def test_ret():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set mut x (fn ( () () (ret ()) ) ))
(x ())
"""
    )


# This test was commented out because the proper checking of ret being outside of a function
# needs executing a function at compile time, and it was chosen not to provide it in Python
#
# def test_ret_outside_function():
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "Function return declared outside of function",
#        """ret
# """
#    )


def test_ret_type():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Returned value type of function is different from called function type",
        """set mut x (fn ( () bool
	ret data int 0
))
x ()
"""
    )


def test_ret_handler():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((bool true) (handled_overflow))\n",
        "",
        """set mut x (fn ( () bool
	ret (data bool true) (data overflow)
))
x ()
handle overflow
	data handled_overflow
"""
    )


def test_ret_missing_handler_evaled_li():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Forced handler set in scope but no handler",
        """set mut x (fn ( () bool
	ret (data bool true) (data overflow)
))
x ()
handle somethingelse
	data somethingelse
"""
    )


def test_ret_missing_handler():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Forced handler set but no handler",
        """set mut x (fn ( () bool
	ret (data bool true) (data overflow)
))
x ()
handle somethingelse
	(data somethingelse)
data whatever
"""
    )


# __set__
def test_set_const():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """()\n""",
        "",
        "set const x (int 0)"
    )


def test_set_node_size():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for set",
        "set const x (int 0) wrong"
    )


def test_set_mutdecl():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Assignment with invalid mutability declaration",
        "set wrong x (int 0)"
    )


def test_set_const_over_mut():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Trying to reassign a constant name over a mutable name",
        """(set mut x (int 0))
(set const x (int 0))"""
    )


def test_set_const_reassignment():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Trying to reassign constant",
        """(set const x (int 0))
(set mut x (int 0))"""
    )


def test_set_call_fn():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 10))\n",
        "",
        """somefn = fn () int
	ret data int 10
int x = (somefn ())
x"""
    )


# __macro__
def test_macro_node_size():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for macro",
        "macro alias () () wrong"
    )


def test_macro_expansion():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((1 2))\n",
        "",
        """macro test ('a ! 'b) (data 'a 'b)
1 ! 2"""
    )


def test_default_macros():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Unassigned name: add",
        """(1 + 2)"""
    )


# __if__
def test_if_node_size():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for if",
        "if (true) () () wrong"
    )


# __data__
# def test_data_node_size():
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "Wrong number of arguments for data",
#        "data () wrong"
#    )


# unsafe
def test_unsafe():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((data (OK)))\n",
        "",
        "unsafe (data (OK))"
    )


# ptr
def test_ptr():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        "set const x (ptr int 0xdeadbeef)"
    )


def test_read_ptr():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((read_ptr int 0xdeadbeef))\n",
        "",
        "unsafe (read_ptr int 0xdeadbeef)"
    )


def test_write_ptr():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((write_ptr (int 0) 0xdeadbeef))\n",
        "",
        "unsafe (write_ptr (int 0) 0xdeadbeef)"
    )


def test_get_ptr():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((get_ptr x))\n",
        "",
        """set const x (int 0)
get_ptr x"""
    )


def test_size_of():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((size_of x))\n",
        "",
        """set const x (int 0)
size_of x"""
    )


# struct
def test_struct_decl():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        "set const mystruct (struct ((mut x int)))"
    )


def test_struct_init():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(set const mystruct (struct ((mut x int))))
(set const mystruct_ (mystruct (1)))"""
    )


def test_struct_member_access():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """set const mystruct (struct ((mut x int)))
set const mystruct_ (mystruct (1))
mystruct_ x"""
    )


def test_struct_deep_member_access():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """set const mystruct (struct ((member_x int)))
set const mystruct2 (struct ((member_mystruct mystruct)))
set const st_mystruct (mystruct (1))
set const st_mystruct2 (mystruct2 (st_mystruct))
st_mystruct2 member_mystruct member_x"""
    )


def test_struct_member_set():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 2))\n",
        "",
        """set const mystruct (struct ((mut x int)))
set const mystruct_ (mystruct (1))
set mut (mystruct_ x) (int 2)
mystruct_ x"""
    )


def test_struct_member_set_wrong_type():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Setting struct member with invalid value type",
        """set const mystruct (struct ((mut x int)))
set const mystruct_ (mystruct (1))
set mut (mystruct_ x) (float 3.14)
mystruct_ x"""
    )


def test_struct_member_access_for_name():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """set const mystruct (struct ((mut x int)))
set const mystruct_ (mystruct (1))
set const randomvar (int (mystruct_ x))
randomvar"""
    )


def test_struct_init_wrong_number_of_members():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Initializing struct with wrong number of member values",
        """(set const mystruct (struct ((mut x int)(mut y int))))
(set const mystruct_ (mystruct (1)))
"""
    )


def test_struct_init_wrong_type_for_member():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Initializing struct with invalid value type for member",
        """(set const mystruct (struct ((mut x int)(mut y int))))
(set const mystruct_ (mystruct (1 3.14)))
"""
    )


# eval tests
def test_eval_name():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """set const randomvar (int 1)
randomvar"""
    )


# unlispifcation tests
def test_unlisp_set_value():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """int somename = 1"""
    )


def test_unlisp_set_mut_value():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """mut int somename = 1"""
    )


def test_unlisp_set_fn():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """somefn = fn (x int  y int) ()
	ret
somefn 12 34
"""
    )


def test_unlisp_set_fn_with_return():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """somefn = fn (x int  y int)
	ret
somefn 12 34
"""
    )


def test_unlisp_struct():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """struct file =
	a int
file xyz = (1)
"""
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fast", action="store_true")
    group.add_argument("-f")
    args = parser.parse_args()

    test_ct, ok_ct, failed_ct = 0, 0, 0

    if args.f is None:
        fast = args.fast
        slow = []
        tests = [t for t in globals() if t[0:5] == "test_" and callable(eval(t))]
        for t in tests:

            if fast and t in slow:
                continue

            result = eval(f"{t}()")
            test_ct += 1
            if result:
                ok_ct += 1
            else:
                failed_ct += 1

    else:
        result = eval(f"{args.f}()")
        test_ct += 1
        if result:
            ok_ct += 1
        else:
            failed_ct += 1

    print(f"\nTests: {test_ct} - Passed: {ok_ct} - Failed: {failed_ct}")
