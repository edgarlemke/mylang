#!/usr/bin/python3

import argparse
import inspect as i
from subprocess import Popen, PIPE, run as run_
from shlex import split

import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
root_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
import shared

OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def _test(fn_name, expected_stdout, expected_stderr, expected_stdout_bin, expected_stderr_bin, src, keep, debug=False):
    print(f"TEST {fn_name} - ", end="")

    debug_str = "--debug" if debug else ""

    cmd = f"/usr/bin/python3 {root_path}/run.py --src \"{src}\" --output \"{src}.o\" {debug_str}"
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
    run_(split(f"gcc {src}.o -o {src}.bin"))

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

    if not keep:
        run_(split(f"rm {src}.o.parse {src}.o.ll {src}.o.s {src}.o {src}.bin "))

    if err:
        print(f"CMD: %s" % cmd)
        return False

    print(OK)
    return True


def _test_exit_code(fn_name, expected_stdout, expected_stderr, expected_exit_code, src, keep, debug=False):
    print(f"TEST {fn_name} - ", end="")

    debug_str = "--debug" if debug else ""

    cmd = f"/usr/bin/python3 {root_path}/run.py --src \"{src}\" --output \"{src}.o\" {debug_str}"
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
    run_(split(f"gcc {src}.o -o {src}.bin"))

    # Running
    cmd_bin = f"{src}.bin; echo $?"
    # p_bin = Popen(split(cmd_bin), stdout=PIPE, stderr=PIPE)
    # stdout_bin, stderr_bin = p_bin.communicate()

    # print(stdout_bin)
    # print(stderr_bin)
    result = run_(split(cmd_bin), shell=True, capture_output=True, text=True)

    if str(result.returncode) != expected_exit_code:
        print(FAIL)

        print(f"""stderr_bin not correct:
        expected:   %s
        got:        %s""" % (expected_exit_code, str(result.returncode)))
        err = True

    if not keep:
        run_(split(f"rm {src}.o.parse {src}.o.ll {src}.o.s {src}.o {src}.bin "))

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

# RUNTIME
#


def test_empty_function(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/empty_function/main.k",
        keep,
        debug,
    )


def test_hello_world(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "Hello world! ❤️",
        "",
        f"{dir_path}/run/hello_world/main.k",
        keep,
        debug,
    )
#
#

# SIGNED INTEGER TESTS
#


def test_add_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        f"{dir_path}/run/add_int_int/main.k",
        keep,
        debug,
    )


def test_sub_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "4",
        f"{dir_path}/run/sub_int_int/main.k",
        keep,
        debug,
    )


def test_mul_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "15",
        f"{dir_path}/run/mul_int_int/main.k",
        keep,
        debug,
    )


def test_sdiv_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/sdiv_int_int/main.k",
        keep,
        debug,
    )


def test_and_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "42",
        f"{dir_path}/run/and_int_int/main.k",
        keep,
        debug,
    )


def test_or_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "6",
        f"{dir_path}/run/or_int_int/main.k",
        keep,
        debug,
    )


def test_xor_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "42",
        f"{dir_path}/run/xor_int_int/main.k",
        keep,
        debug,
    )


def test_not_int_int(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "254",
        f"{dir_path}/run/not_int_int/main.k",
        keep,
        debug,
    )


def test_eq_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/eq_int_int/main.k",
        keep,
        debug,
    )


def test_neq_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/neq_int_int/main.k",
        keep,
        debug,
    )


def test_gt_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/gt_int_int/main.k",
        keep,
        debug,
    )


def test_ge_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/ge_int_int/main.k",
        keep,
        debug,
    )


def test_lt_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/lt_int_int/main.k",
        keep,
        debug,
    )


def test_le_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/le_int_int/main.k",
        keep,
        debug,
    )


def test_shl_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/shl_int_int/main.k",
        keep,
        debug,
    )


def test_shr_int_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/shr_int_int/main.k",
        keep,
        debug,
    )


#
#


# UNSIGNED INTEGER TESTS
#
def test_add_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        f"{dir_path}/run/add_uint_uint/main.k",
        keep,
        debug,
    )


def test_sub_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "4",
        f"{dir_path}/run/sub_uint_uint/main.k",
        keep,
        debug,
    )


def test_mul_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "15",
        f"{dir_path}/run/mul_uint_uint/main.k",
        keep,
        debug,
    )


def test_div_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/div_uint_uint/main.k",
        keep,
        debug,
    )


def test_and_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "42",
        f"{dir_path}/run/and_uint_uint/main.k",
        keep,
        debug,
    )


def test_or_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "6",
        f"{dir_path}/run/or_uint_uint/main.k",
        keep,
        debug,
    )


def test_xor_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "0",
        f"{dir_path}/run/xor_uint_uint/main.k",
        keep,
        debug,
    )


def test_not_uint_uint(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "254",
        f"{dir_path}/run/not_uint_uint/main.k",
        keep,
        debug,
    )


def test_eq_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/eq_uint_uint/main.k",
        keep,
        debug,
    )


def test_neq_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/neq_uint_uint/main.k",
        keep,
        debug,
    )


def test_gt_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/gt_uint_uint/main.k",
        keep,
        debug,
    )


def test_ge_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/ge_uint_uint/main.k",
        keep,
        debug,
    )


def test_lt_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/lt_uint_uint/main.k",
        keep,
        debug,
    )


def test_le_uint_uint(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/le_uint_uint/main.k",
        keep,
        debug,
    )


def test_shl_uint_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/shl_uint_int/main.k",
        keep,
        debug,
    )


def test_shr_uint_int(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/shr_uint_int/main.k",
        keep,
        debug,
    )
#
#


# BYTE TESTS
#
# def test_add_byte_byte(keep=False, debug=False):
#    return _test_exit_code(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "",
#        "46",
#        f"{dir_path}/run/add_byte_byte/main.k",
#        keep,
#        debug,
#    )
#
#


# FLOAT TESTS
#
def test_add_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/add_float_float/main.k",
        keep,
        debug,
    )


def test_sub_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/sub_float_float/main.k",
        keep,
        debug,
    )


def test_mul_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/mul_float_float/main.k",
        keep,
        debug,
    )


def test_fdiv_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/fdiv_float_float/main.k",
        keep,
        debug,
    )


def test_eq_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/eq_float_float/main.k",
        keep,
        debug,
    )


def test_gt_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/gt_float_float/main.k",
        keep,
        debug,
    )


def test_ge_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/ge_float_float/main.k",
        keep,
        debug,
    )


def test_lt_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/lt_float_float/main.k",
        keep,
        debug,
    )


def test_le_float_float(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/le_float_float/main.k",
        keep,
        debug,
    )


# BOOL TESTS
def test_and_bool_bool(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/and_bool_bool/main.k",
        keep,
        debug,
    )


def test_or_bool_bool(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/or_bool_bool/main.k",
        keep,
        debug,
    )


def test_xor_bool_bool(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/xor_bool_bool/main.k",
        keep,
        debug,
    )


def test_not_bool_bool(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/not_bool_bool/main.k",
        keep,
        debug,
    )


def test_eq_bool_bool(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/eq_bool_bool/main.k",
        keep,
        debug,
    )
#
#


# IF-ELIF-ELSE TESTS
def test_if(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "true w x > 0",
        "",
        f"{dir_path}/run/if/main.k",
        keep,
        debug,
    )


def test_if_else(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "true",
        "",
        f"{dir_path}/run/if_else/main.k",
        keep,
        debug,
    )


def test_if_elif_elif_elif(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "d >= 3",
        "",
        f"{dir_path}/run/if_elif_elif_elif/main.k",
        keep,
        debug,
    )


def test_if_elif_elif_elif_else(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "else",
        "",
        f"{dir_path}/run/if_elif_elif_elif_else/main.k",
        keep,
        debug,
    )


#
#

# SET TESTS
def test_set(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/set/main.k",
        keep,
        debug,
    )


# ARRAY TESTS
def test_array_byte_init(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/array_byte_init/main.k",
        keep,
        debug,
    )


def test_array_byte_init_unset(keep=False, debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "",
        "",
        f"{dir_path}/run/array_byte_init_unset/main.k",
        keep,
        debug,
    )


def test_set_get_array_member(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        f"{dir_path}/run/set_get_array_member/main.k",
        keep,
        debug,
    )


def test_array_get_bound_checking(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "255",
        f"{dir_path}/run/array_get_bound_checking/main.k",
        keep,
        debug,
    )
#
#


# SCOPE TESTS
#
# def test_scope(keep=False, debug=False):
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "",
#        "",
#        "",
#        f"{dir_path}/run/scope/main.k",
#        keep,
#        debug,
#    )
#
#


# STRUCT TESTS
#
def test_set_get_struct_member_depth_0(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        f"{dir_path}/run/set_get_struct_member_depth_0/main.k",
        keep,
        debug,
    )


def test_set_get_struct_member_depth_1(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        f"{dir_path}/run/set_get_struct_member_depth_1/main.k",
        keep,
        debug,
    )


def test_set_get_struct_member_depth_2(keep=False, debug=False):
    return _test_exit_code(
        i.getframeinfo(i.currentframe()).function,
        "",
        "",
        "46",
        f"{dir_path}/run/set_get_struct_member_depth_2/main.k",
        keep,
        debug,
    )
#
#


# FORMATTING TESTS


# TODO: put it back
# def test_bin(keep=False, debug=False):
#    return _test(
#        i.getframeinfo(i.currentframe()).function,
#        "",
#        "",
#        "0000000000000000000000000000000001001001100101100000001011010010",
#        "",
#        f"{dir_path}/run/bin/main.k",
#        keep,
#        debug,
#    )

#
#


def run(**args):
    return shared.run_keep("End-to-end Tests", [], globals(), **args)


if __name__ == "__main__":

    args = shared.parse_args()
    run(**args)
