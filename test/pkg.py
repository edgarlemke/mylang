#!/usr/bin/python3

import inspect as i
from shlex import split
from subprocess import Popen, PIPE


def test_package_not_found ():
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """incl randompkg""",
        "", # nothing to be tested, stderr is tested before
        "Package not found: randompkg"
    )

def test_get_pkg_name () :
    import os
    import random

    print("TEST get_pkg_name() - ", end= "")

    # create dummy pkg dir at /tmp
    rand = int( str( random.random() )[2:] )

    path = f"/tmp/mylang-test_get_pkg_name-{rand}"

    # flush old dir
    try:
        os.rmdir(path)
    except FileNotFoundError:
        pass

    # create new dir
    os.makedirs(path)

    # create pkg file
    with open(f"{path}/pkg", "w+") as fd:
        fd.write("")

    # create dummy pkg
    with open(f"{path}/test.mylang", "w+") as fd:
        fd.write("""fn main  (int x)  int
\tnop
""")

    cmd = f"/usr/bin/python3 ../run.py --src \"{path}/test.mylang\""
    sp = split(cmd)

    stdout, stderr = _popen(sp)

    expected_stderr = ""
    expected_stdout = ""

    if stderr != expected_stderr:
        print(f"""FAIL - stderr not correct:
            expected:   {expected_stdout}
            got:        {stdout}""")
        return False

    if stdout != expected_stdout:
        print(f"""FAIL - stdout not correct:
            expected:   {expected_stdout}
            got:        {stdout}""")
        return False

    print("OK")
    return True




def _test (fn_name, expr, expected_stdout, expected_stderr) :
    x = " ".join( fn_name.split("_")[1:] )
    msg = f"TEST {x} - "

    print(msg, end="", flush= True)

    stdout, stderr = _expr(expr)
    #print(stdout)
    #print(stderr)

    err = False
    if not(expected_stderr in stderr):
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
