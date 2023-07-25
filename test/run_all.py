#!/usr/bin/python3

from subprocess import run


def t(cmd, msg):
    print(msg + "\n")
    run(cmd, shell=True)
    print("\n...\n")


t("./lex.py --fast", "Lexer Tests  (fast)")
t("./frontend_eval.py --fast", "Front-end eval() Tests - Compile-time scope  (fast)")
t("./frontend_eval_runtime.py --fast", "Front-end eval() Tests - Runtime scope  (fast)")
