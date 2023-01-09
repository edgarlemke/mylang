#!/usr/bin/python3

import argparse

import lex
import parse


def run (src) :
    with open(src, "r") as fd:
        code = fd.readlines()
        expr = "".join(code)

    token_list = lex.tokenize(expr) 
    parsetree = parse.parse(token_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    args = parser.parse_args()

    src = str(args.src)

    run(src)
