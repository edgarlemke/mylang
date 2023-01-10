#!/usr/bin/python3

from subprocess import Popen, PIPE
from shlex import split


def test_parser_rule_0 () :
    print("TEST PARSER RULE 0 - ", end="", flush= True)

    stdout, stderr = _popen("\\\" \\\"")

    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}", flush= True)
        exit()

    expected = """(("EXPR" (("QUOTE" "0" "1" "\"") ("VALUE" "1" "2" " ") ("QUOTE" "2" "3" "\""))))"""
    if stdout != expected:
        print(f"""FAIL - stdout not corrent:
            expected:   {expected}
            got:        {stdout}""", flush= True)
        exit()

    print("OK")


def _popen (expr) :
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-parse-tree"
    sp = split(cmd)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
