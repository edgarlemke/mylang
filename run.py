#!/usr/bin/python3

import argparse

import lex
import parse
import list as list_


def run (src, print_parse_tree= False) :
    with open(src, "r") as fd:
        code = fd.readlines()
        expr = "".join(code)

    token_list = lex.tokenize(expr) 
    parsetree = parse.parse(token_list)

    if print_parse_tree:
        print( list_.list_print(parsetree) )
        exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("--print-parse-tree", action= "store_true")
    args = parser.parse_args()

    src = str(args.src)
    print_parse_tree = args.print_parse_tree

    run(src, print_parse_tree)
