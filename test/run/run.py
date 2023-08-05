#!/usr/bin/python3

import argparse
import inspect as i
from subprocess import Popen, PIPE, run
from shlex import split


OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def _test(fn_name, expected_stdout, expected_stderr, expected_stdout_bin, expected_stderr_bin, src):
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
    cmd_bin = f"{src}.bin"
    p_bin = Popen(split(cmd_bin), stdout=PIPE, stderr=PIPE)
    stdout_bin, stderr_bin = p_bin.communicate()

    stdout_bin_dec = stdout_bin.decode()
    stdout_bin_ok = (expected_stdout_bin == "" and stdout_bin_dec == "") or (expected_stdout_bin != "" and stdout_bin_dec == expected_stdout_bin)

    stderr_bin_dec = stderr_bin.decode()
    stderr_bin_ok = (expected_stderr_bin == "" and stderr_bin_dec == "") or (expected_stderr_bin != "" and expected_stderr_bin in stderr_bin_dec)

    if not stderr_bin_ok:
        print(FAIL)

        print(f"""stderr_bin not correct:
        expected:   %s
        got:        %s""" % (expected_stderr_bin, stderr_bin_dec))
        err = True

    if not stdout_bin_ok:
        if not err:
            print(FAIL)

        print("""stdout_bin not correct:
        expected:   %s
        got:        %s""" % (expected_stdout_bin, stdout_bin_dec))
        err = True

    if err:
        print(f"CMD: %s" % cmd)
        return False

    print(OK)
    return True


def _test_exit_code(fn_name, expected_stdout, expected_stderr, expected_exit_code, src):
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
    cmd_bin = f"{src}.bin; echo $?"
    # p_bin = Popen(split(cmd_bin), stdout=PIPE, stderr=PIPE)
    # stdout_bin, stderr_bin = p_bin.communicate()

    # print(stdout_bin)
    # print(stderr_bin)
    result = run(split(cmd_bin), shell=True, capture_output=True, text=True)

    if str(result.returncode) != expected_exit_code:
        print(FAIL)

        print(f"""stderr_bin not correct:
        expected:   %s
        got:        %s""" % (expected_exit_code, str(result.returncode)))
        err = True

    if err:
        print(f"CMD: %s" % cmd)
        return False

    print(OK)
    return True


def _popen(expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\""
    sp = split(cmd)
    p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    return p.communicate()


def cleanup():
    cmd = """for i in $(find | grep -e "\\.k" | grep -v "\\.k$"); do rm $i; done"""
    run(cmd, shell=True)

#
# RUNTIME


def test_empty_function():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./empty_function/main.k"
    )


def test_hello_world():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "Hello world! ❤️",
        "",
        "./hello_world/main.k"
    )


def test_add_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        "./add_int/main.k"
    )


def test_sub_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "4",
        "./sub_int/main.k"
    )


def test_mul_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "15",
        "./mul_int/main.k"
    )


def test_sdiv_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./sdiv_int/main.k"
    )


def test_and_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "42",
        "./and_int/main.k"
    )


def test_or_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "6",
        "./or_int/main.k"
    )


def test_xor_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "42",
        "./xor_int/main.k"
    )


def test_not_int():
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "254",
        "./not_int/main.k"
    )


def test_eq_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./eq_int/main.k"
    )


def test_gt_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./gt_int/main.k"
    )


def test_ge_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./ge_int/main.k"
    )


def test_lt_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./lt_int/main.k"
    )


def test_le_int():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./le_int/main.k"
    )


def test_add_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./add_float/main.k"
    )


def test_sub_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./sub_float/main.k"
    )


def test_mul_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./mul_float/main.k"
    )


def test_fdiv_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./fdiv_float/main.k"
    )


def test_eq_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./eq_float/main.k"
    )


def test_gt_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./gt_float/main.k"
    )


def test_ge_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./ge_float/main.k"
    )


def test_lt_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./lt_float/main.k"
    )


def test_le_float():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./le_float/main.k"
    )


def test_and_bool():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./and_bool/main.k"
    )


def test_or_bool():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./or_bool/main.k"
    )


def test_xor_bool():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./xor_bool/main.k"
    )


def test_not_bool():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./not_bool/main.k"
    )


def test_eq_bool():
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        "./eq_bool/main.k"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fast", action="store_true")
    group.add_argument("-f")

    parser.add_argument("-c", action="store_true")

    args = parser.parse_args()

    if args.c is True:
        cleanup()
        exit()

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
