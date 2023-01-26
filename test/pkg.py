#!/usr/bin/python3

import inspect as i
from shlex import split
from subprocess import Popen, PIPE


def test_package_not_found ():
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """incl  randompkg""",
        "", # nothing to be tested, stderr is tested before
        "Package not found: randompkg"
    )


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
