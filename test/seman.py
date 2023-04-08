#!/usr/bin/python3

import inspect as i
from subprocess import Popen, PIPE
from shlex import split


def test_single_set ():
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tset ui8 a 1
\tset ui8 a 1
""",
        "", # nothing to be tested, stderr is tested before
        "Immutable name already set before: a"
    )

def test_set_fn_arg_conflict ():
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tset ui8 x 1
""",
        "", # nothing to be tested, stderr is tested before
        "Immutable name already set before: x"
    )


def test_set_mut_conflict_0 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tset ui8 a 1
\tmut ui8 a 1
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict: a")

def test_set_mut_conflict_1 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tmut ui8 a 1
\tset ui8 a 1
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict: a")

def test_set_mut_higher_scopes_0 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """set ui8 x 1
fn main  (ui8 a)  ui8
\tset ui8 x 2""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict in higher scope: x")

def test_set_mut_higher_scopes_1 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """
set ui8 x 1
fn main  (ui8 a)  ui8
\tfn otherfn  (ui8 b)  ui8
\t\tset ui8 x 2
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict in higher scope: x")


#def test_call_refs () :
#    _test(
#        i.getframeinfo( i.currentframe() ).function,
#        """fn main  ui8 a  ui8
#\tcall somefn
#""",
#        "", # nothing to be tested, stderr is tested before
#        "Call to undefined function: somefn")


def test_typedef () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """typedef ui8 8

fn main  (ui8 x)  ui8
\ttypedef i8 8""",
    "", # nothing to be tested, stderr is tested before
    "Typedef not declared in global scope")


def test_subst_fn_typefying () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (mytype x)  mytype
\tnop""",
    "((EXPR None (1)) (FN_DECL 0 (2 3 6 7)) (NAME main 1 ()) (ARG_PAR_GROUP 1 (4 5)) (NAME mytype 3 ()) (NAME x 3 ()) (TYPE mytype 1 ()) (EXPR 1 (8)) (NOP 7 ()))",
    "",
    popen_fn= _print_final_ast)


def test_subst_set_mut_typefying () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (int a)  int
\tset int x 1
\tmut int y 1
""",
        """((EXPR None (1)) (FN_DECL 0 (2 3 6 7)) (NAME main 1 ()) (ARG_PAR_GROUP 1 (4 5)) (NAME int 3 ()) (NAME a 3 ()) (TYPE int 1 ()) (EXPR 1 (8 14)) (EXPR 7 (9)) (SET_DECL 8 (10 11 12)) (TYPE int 9 ()) (NAME x 9 ()) (EXPR 9 (13)) (INT 1 12 ()) (EXPR 7 (15)) (MUT_DECL 14 (16 17 18)) (TYPE int 15 ()) (NAME y 15 ()) (EXPR 15 (19)) (INT 1 18 ()))""",
        "",
        popen_fn= _print_final_ast)




def _test (fn_name, expr, expected_stdout, expected_stderr, popen_fn= None) :
    x = " ".join( fn_name.split("_")[1:] )
    msg = f"TEST {x} - "

    print(msg, end="", flush= True)

    if popen_fn == None:
        popen_fn = _expr

    stdout, stderr = popen_fn(expr)
    #print(stdout)
    #print(stderr)

    err = False
    if not(expected_stderr in stderr) or (expected_stderr == "" and expected_stderr != stderr):
        print(f"""FAIL - stderr not correct:
        expected:   {expected_stderr}
        got:        {stderr}""")
        err = True

    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
            expected:   {expected_stdout}
            got:        {stdout}""")
        err = True
    if err:
        return False

    print("OK")
    return True


def _print_final_ast (expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-final-ast"
    sp = split(cmd)
    return _popen(sp)

def _expr (expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\""
    sp = split(cmd)
    return _popen(sp)

def _popen (sp) :
    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
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
