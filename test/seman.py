#!/usr/bin/python3

import inspect as i
from subprocess import Popen, PIPE
from shlex import split


def test_single_set ():
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  ui8 x  ui8
\tset a ui8 1
\tset a ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "Immutable name already set before: a"
    )

def test_set_fn_arg_conflict ():
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  ui8 x  ui8
\tset x ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "Immutable name already set before: x"
    )


def test_set_mut_conflict_0 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  ui8 x  ui8
\tset a ui8 1
\tmut a ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict: a")

def test_set_mut_conflict_1 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  ui8 x  ui8
\tmut a ui8 1
\tset a ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict: a")

def test_set_mut_higher_scopes_0 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """pkg somepkg
\tset x ui8 1
\tfn main  ui8 a  ui8
\t\tset x ui8 2
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict in higher scope: x")

def test_set_mut_higher_scopes_1 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """pkg somepkg
\tset x ui8 1
\tfn main  ui8 a  ui8
\t\tfn otherfn  ui8 b  ui8
\t\t\tset x ui8 2
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict in higher scope: x")


def test_call_refs () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  ui8 a  ui8
\tcall somefn
""",
        "", # nothing to be tested, stderr is tested before
        "Call to undefined function: somefn")


def test_typedef () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """typedef ui8 8

fn main  ui8 x  ui8
\ttypedef i8 8
""",
    "", # nothing to be tested, stderr is tested before
    "Typedef not declared in global scope")




def _test (fn_name, expr, expected_stdout, expected_stderr) :
    x = " ".join( fn_name.split("_")[1:] )
    msg = f"TEST {x} - "

    print(msg, end="", flush= True)

    stdout, stderr = _expr(expr)
    #print(stdout)
    #print(stderr)

    if not(expected_stderr in stderr):
        print(f"""FAIL - stderr not correct:
        expected:   {expected_stderr}
        got:        {stderr}""")
        return False

    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
            expected:   {expected_stdout}
            got:        {stdout}""")
        return False

    print("OK")
    return True


def _expr (expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\""
    sp = split(cmd)
    return _popen(sp)

def _popen (sp) :
    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
