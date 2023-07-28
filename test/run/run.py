#!/usr/bin/python3

import argparse
import inspect as i
from subprocess import Popen, PIPE, run
from shlex import split


OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def _test(fn_name, expected_stdout, expected_stderr, src):
    print(f"TEST {fn_name} - ", end="")

    cmd = f"/usr/bin/python3 ../../run.py --src \"{src}\" --output \"{src}.o\""
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

    # Linking
    run(split(f"gcc {src}.o -o {src}.bin"))

    # Running
    cmd2 = f"{src}.bin"
    p2 = Popen(split(cmd2), stdout=PIPE, stderr=PIPE)
    stdout2, stderr2 = p2.communicate()

    print(OK)
    return True


def _popen(expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\""
    sp = split(cmd)
    p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    return p.communicate()

#
# RUNTIME


def test_empty_function():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "./empty_function/main.k"
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
