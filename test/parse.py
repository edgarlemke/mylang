#!/usr/bin/python3

import inspect as i
from subprocess import Popen, PIPE
from shlex import split


def test_listfy_par_groups():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """abc (a b c) xyz""",
        """((TOKEN LIT 0 3 abc) (TOKEN SPACE 3 4 " ") (LIST ((TOKEN LIT 5 6 a) (TOKEN SPACE 6 7 " ") (TOKEN LIT 7 8 b) (TOKEN SPACE 8 9 " ") (TOKEN LIT 9 10 c))) (TOKEN SPACE 11 12 " ") (TOKEN LIT 12 15 xyz))"""
    )


def test_listfy_blocks():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """block_start
\tstuff""",
        """((TOKEN LIT 0 11 block_start) (BLOCK ((TOKEN LIT 13 18 stuff))))"""
    )


def test_fn():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """fn main () ui8
\tnop""",
        """((TOKEN LIT 0 2 fn) (TOKEN SPACE 2 3 " ") (TOKEN LIT 3 7 main) (TOKEN SPACE 7 8 " ") (LIST ()) (TOKEN SPACE 10 11 " ") (TOKEN LIT 11 14 ui8) (BLOCK ((TOKEN LIT 16 19 nop))))"""
    )


def test_fn_1_arg():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """fn main ((ui8 x)) ui8
\tnop""",
        """((TOKEN LIT 0 2 fn) (TOKEN SPACE 2 3 " ") (TOKEN LIT 3 7 main) (TOKEN SPACE 7 8 " ") (LIST ((LIST ((TOKEN LIT 10 13 ui8) (TOKEN SPACE 13 14 " ") (TOKEN LIT 14 15 x))))) (TOKEN SPACE 17 18 " ") (TOKEN LIT 18 21 ui8) (BLOCK ((TOKEN LIT 23 26 nop))))"""
    )


def test_fn_2_args():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """fn main ((mod8 x)(mod8 y)) mod8
\tnop""",
        """((TOKEN LIT 0 2 fn) (TOKEN SPACE 2 3 " ") (TOKEN LIT 3 7 main) (TOKEN SPACE 7 8 " ") (LIST ((LIST ((TOKEN LIT 10 14 mod8) (TOKEN SPACE 14 15 " ") (TOKEN LIT 15 16 x))) (LIST ((TOKEN LIT 18 22 mod8) (TOKEN SPACE 22 23 " ") (TOKEN LIT 23 24 y))))) (TOKEN SPACE 26 27 " ") (TOKEN LIT 27 31 mod8) (BLOCK ((TOKEN LIT 33 36 nop))))"""
    )


def test_fn_3_args():
    _test(
        i.getframeinfo(i.currentframe()).function,
        """fn main ((mod8 x)(mod8 y)(mod8 z)) mod8
\tnop""",
        """((TOKEN LIT 0 2 fn) (TOKEN SPACE 2 3 " ") (TOKEN LIT 3 7 main) (TOKEN SPACE 7 8 " ") (LIST ((LIST ((TOKEN LIT 10 14 mod8) (TOKEN SPACE 14 15 " ") (TOKEN LIT 15 16 x))) (LIST ((TOKEN LIT 18 22 mod8) (TOKEN SPACE 22 23 " ") (TOKEN LIT 23 24 y))) (LIST ((TOKEN LIT 26 30 mod8) (TOKEN SPACE 30 31 " ") (TOKEN LIT 31 32 z))))) (TOKEN SPACE 34 35 " ") (TOKEN LIT 35 39 mod8) (BLOCK ((TOKEN LIT 41 44 nop))))"""
    )


def _test(fn_name, expr, expected):
    print(f"TEST {fn_name} - ", end="", flush=True)

    stdout, stderr = _expr(expr)

    err = False
    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}")
        err = True
        # exit()

    if stdout != expected:
        print(f"""FAIL - stdout not correct:
            expected:   {expected}
            got:        {stdout}""")
        err = True
        # exit()

    if err:
        return False

    print("OK")


def _expr(expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-token-tree"
#    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-token-list"
    sp = split(cmd)
    return _popen(sp)


def _popen(sp):
    p = Popen(sp, stdout=PIPE, stderr=PIPE, encoding="utf-8")
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
