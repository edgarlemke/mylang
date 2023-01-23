#!/usr/bin/python3

from subprocess import Popen, PIPE
from shlex import split


def test_single_set ():
    basictest(
        "TEST single set - ",
        """fn main  ui8 x  ui8
\tset a ui8 1
\tset a ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "Immutable name already set before: a"
    )

def test_set_mut_conflict_0 () :
    basictest(
        "TEST set mut conflict 0 - ",
        """fn main  ui8 x  ui8
\tset a ui8 1
\tmut a ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict: a")

def test_set_mut_conflict_1 () :
    basictest(
        "TEST set mut conflict 1 - ",
        """fn main  ui8 x  ui8
\tmut a ui8 1
\tset a ui8 1
""",
        "", # nothing to be tested, stderr is tested before
        "SET/MUT conflict: a")

def test_set_mut_higher_scopes () :
    basictest(
        "TEST set mut higher scopes - ",
        """pkg somepkg
\tset x ui8 1
\tfn main  ui8 a  ui8
\t\tset x ui8 2
""",
        "",
        "SET/MUT conflict in higher scope: x")



def basictest (msg, expr, expected_stdout, expected_stderr) :
    print(msg, end="", flush= True)

    stdout, stderr = _expr(expr)
    #print(stdout)
    #print(stderr)

    if not(expected_stderr in stderr):
        print(f"FAIL - stderr not correct: {stderr}")
        exit()

    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
            expected:   {expected}
            got:        {stdout}""")
        exit()

    print("OK")

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
