#!/usr/bin/python3

import argparse
import inspect as i
from subprocess import Popen, PIPE
from shlex import split

import shared

OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def _test(fn_name, expected_stdout, expected_stderr, expr, debug=True):
    print(f"TEST {fn_name} - ", end="")

    cmd = f"/usr/bin/python3 ../backend/run.py --print-output --expr \"{expr}\""
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


# Typing tests
def test_def_type(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Constant assignment has invalid type",
        "def const x (wrong 0)",
        debug,
    )


def test_fn_args(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Function argument has invalid type",
        "fn main ((x wrong)(y wrong)) int ()",
        debug,
    )


def test_fn_ret_type(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Function return type has invalid type",
        "fn main ((x int) (y int)) wrong ()",
        debug,
    )
#


def test_set(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        "",
        "Resetting constant name",
        "fn main () ((def const x (int 0)) (set x 0))",
        debug,
    )


# LLVM IR generation tests
def test_llvm_fn_void_ret_type(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """define void @main() {
	start:
		ret void
}
""",
        "",
        """fn main () ()""",
        debug,
    )


def test_llvm_fn_cvt_int(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """define i64 @main() {
	start:
		ret i64
}
""",
        "",
        """fn main () int ()""",
        debug,
    )


def test_llvm_fn_cvt_uint(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """define i64 @main() {
	start:
		ret i64
}
""",
        "",
        """fn main () uint ()""",
        debug,
    )


def test_llvm_fn_unoverload(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """define i64 @test__int_uint(i64 %x, i64 %y) {
	start:
		ret i64
}
define i64 @test__uint_int(i64 %x, i64 %y) {
	start:
		ret i64
}
""",
        "",
        """((fn test ((x int)(y uint)) int ()) (fn test ((x uint)(y int)) uint ()))""",
        debug,
    )


def test_llvm_constant_propagation(debug=False):
    return _test(
        i.getframeinfo(i.currentframe()).function,
        """@main_CONSTANT = constant i64 1;
define void @main() {
	start:
		; load value of constant "CONSTANT"
		%CONSTANT = load i64, i64* @main_CONSTANT

		ret void
}
""",
        "",
        """fn main () ((def const CONSTANT (int 1)))""",
        debug,
    )
#


def run(**args):
    return shared.run("Backend Tests", [], globals(), **args)


if __name__ == "__main__":

    args = shared.parse_args()
    run(**args)
