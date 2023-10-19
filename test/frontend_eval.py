#!/usr/bin/python3
# coding: utf-8

import argparse
import inspect as i
from subprocess import Popen, PIPE
from shlex import split

import shared

OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def _test(fn_name, expected_stdout, expected_stderr, expr, debug=False):
    print(f"TEST {fn_name} - ", end="")

    debug_str = "--debug" if debug else ""

    cmd = f"/usr/bin/python3 ../frontend/run.py --print-output --compile-time-scope {debug_str} --expr \"{expr}\""
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
def test_data(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """((abc 123))\n""",
        "",
        "data abc 123",
        debug,
    )


# __fn__
def test_fn(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """()\n""",
        "",
        "fn main (x int, y int) int ()",
        debug,
    )


# def test_fn_node_size(debug=False):
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "Wrong number of arguments for fn",
#        "fn (x uint) int () wrong"
#    )


def test_fn_without_args(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn main () ()""",
        debug,
    )


def test_fn_arg_type_infer_int(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn myfn (x int) ()
myfn 1234""",
        debug,
    )


def test_fn_arg_type_infer_float(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn myfn (x float) ()
myfn 3.14""",
        debug,
    )


def test_fn_arg_type_infer_bool_true(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn myfn (x bool) ()
myfn true""",
        debug,
    )


def test_fn_arg_type_infer_bool_false(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn myfn (x bool) ()
myfn false""",
        debug,
    )


def test_fn_arg_name(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((bool true))\n",
        "",
        """fn myfn (x bool) bool
	x
def const mybool (bool true)
myfn mybool""",
        debug,
    )


def test_fn_arg_fncall(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn myfn (x bool) ()
fn retbool () bool
	data bool true
myfn (retbool ())""",
        debug,
    )


def test_fn_arg_inside_scope(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """fn myfn (x int) int
	x
myfn 1""",
        debug,
    )


def test_ret(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn x ()
	ret
x ()""",
        debug,
    )


# This test was commented out because the proper checking of ret being outside of a function
# needs executing a function at compile time, and it was chosen not to provide it in Python
#
# def test_ret_outside_function(debug=False):
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "Function return declared outside of function",
#        """ret
# """
#    )


def test_ret_type(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Returned value type of function is different from called function type",
        """fn x () bool
	ret data int 0
x ()
""",
        debug,
    )


# __def__
def test_def_const(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """()\n""",
        "",
        "def const x (int 0)",
        debug,
    )


def test_def_node_size(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for def",
        "def const x (int 0) wrong",
        debug,
    )


def test_def_mutdecl(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Assignment with invalid mutability declaration",
        "def wrong x (int 0)",
        debug,
    )


def test_def_const_over_mut(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Trying to reassign a constant name over a mutable name",
        """(def mut x (int 0))
(def const x (int 0))""",
        debug,
    )


def test_def_const_reassignment(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Trying to reassign constant",
        """(def const x (int 0))
(def mut x (int 0))""",
        debug,
    )


def test_def_call_fn(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 10))\n",
        "",
        """fn somefn () int
	ret data int 10
int x := (somefn ())
x""",
        debug,
    )


# __set__
def test_set(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 15))\n",
        "",
        """mut int x := 10
x = 15
x""",
        debug,
    )


def test_set_node_size(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for set",
        """mut int x := 10
set x 15 wrong""",
        debug,
    )


def test_set_undefined_name(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Resetting undefined name",
        """set x 15""",
        debug,
    )


def test_set_constant_name(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Resetting constant name",
        """int x := 10
set x 15""",
        debug,
    )


# __macro__
def test_macro_node_size(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for macro",
        "macro alias () () wrong",
        debug,
    )


def test_macro_expansion(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((1 2))\n",
        "",
        """macro test ('a ! 'b) (data 'a 'b)
1 ! 2""",
        debug,
    )


def test_default_macros(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Unassigned name: add",
        """(1 + 2)""",
        debug,
    )


# __if__
def test_if_node_size(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Wrong number of arguments for if",
        "if (true) () () wrong",
        debug,
    )


# __data__
# def test_data_node_size(debug=False):
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "Wrong number of arguments for data",
#        "data () wrong"
#    )


# __repeat__
# def test_repeat(debug=False):
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "(((0 0 0 0 0)))\n",
#        "",
#        "5 ** 0"
#    )


# unsafe
def test_unsafe(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((data (OK)))\n",
        "",
        "unsafe (data (OK))",
        debug,
    )


# ptr
def test_ptr(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        "def const x ((ptr int) 0xdeadbeef)",
        debug,
    )


def test_read_ptr(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((read_ptr int 0xdeadbeef))\n",
        "",
        "unsafe (read_ptr int 0xdeadbeef)",
        debug,
    )


def test_write_ptr(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((write_ptr (int 0) 0xdeadbeef))\n",
        "",
        "unsafe (write_ptr (int 0) 0xdeadbeef)",
        debug,
    )


def test_get_ptr(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((get_ptr x))\n",
        "",
        """def const x (int 0)
get_ptr x""",
        debug,
    )


def test_size_of(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((size_of x))\n",
        "",
        """def const x (int 0)
size_of x""",
        debug,
    )


# struct
def test_struct_decl(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        "def const mystruct (struct ((mut x int)))",
        debug,
    )


def test_struct_init(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """(def const mystruct (struct ((mut x int))))
(def const mystruct_ (mystruct (1)))""",
        debug,
    )


def test_struct_member_access(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """def const mystruct (struct ((mut x int)))
def const mystruct_ (mystruct (1))
mystruct_ x""",
        debug,
    )


def test_struct_deep_member_access(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """def const mystruct (struct ((member_x int)))
def const mystruct2 (struct ((member_mystruct mystruct)))
def const st_mystruct (mystruct (1))
def const st_mystruct2 (mystruct2 (st_mystruct))
st_mystruct2 member_mystruct member_x""",
        debug,
    )


def test_struct_member_def(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 2))\n",
        "",
        """def const mystruct (struct ((mut x int)))
def const mystruct_ (mystruct (1))
def mut (mystruct_ x) (int 2)
mystruct_ x""",
        debug,
    )


def test_struct_member_def_wrong_type(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Setting struct member with invalid value type",
        """def const mystruct (struct ((mut x int)))
def const mystruct_ (mystruct (1))
def mut (mystruct_ x) (float 3.14)
mystruct_ x""",
        debug,
    )


def test_struct_member_access_for_name(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """def const mystruct (struct ((mut x int)))
def const mystruct_ (mystruct (1))
def const randomvar (int (mystruct_ x))
randomvar""",
        debug,
    )


def test_struct_init_wrong_number_of_members(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Initializing struct with wrong number of member values",
        """(def const mystruct (struct ((mut x int)(mut y int))))
(def const mystruct_ (mystruct (1)))
""",
        debug,
    )


def test_struct_init_wrong_type_for_member(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Initializing struct with invalid value type for member",
        """(def const mystruct (struct ((mut x int)(mut y int))))
(def const mystruct_ (mystruct (1 3.14)))
""",
        debug,
    )


# eval tests
def test_eval_name(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "((int 1))\n",
        "",
        """def const randomvar (int 1)
randomvar""",
        debug,
    )


# unlispifcation tests
def test_unlisp_def_value(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """int somename := 1""",
        debug,
    )


def test_unlisp_def_mut_value(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """mut int somename := 1""",
        debug,
    )


def test_unlisp_fn(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn somefn (x int, y int) ()
	ret
somefn 12 34
""",
        debug,
    )


def test_unlisp_fn_with_return(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """fn somefn (x int, y int)
	ret
somefn 12 34
""",
        debug,
    )


def test_unlisp_struct(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "()\n",
        "",
        """struct File :=
	a int
File xyz := (1)
""",
        debug,
    )


def run(**args):
    return shared.run("Frontend Compiletime Tests", [], globals(), **args)


if __name__ == "__main__":

    args = shared.parse_args()
    run(**args)
