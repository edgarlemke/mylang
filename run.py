#!/usr/bin/python3

import argparse

import lex
import parse
import seman
import list as list_


def run (expr, print_parse_tree= False, print_ast= False, print_symbol_table= False) :
    token_list = lex.tokenize(expr) 
    parsetree = parse.parse(token_list, "EXPR")

    if print_parse_tree:
        print( list_.list_print(parsetree), end="" )
        exit()

    ast = parse.abstract(parsetree.copy())
    if print_ast:
        print( list_.list_print(ast), end="" )
        exit()

    s_tree = parse.serialize_tree(ast)

    symtbl, scopes = seman.get_symtbl(s_tree)
    print(f"symtbl: {symtbl}")
    print(f"scopes: {scopes}")

    seman.check(s_tree, symtbl, scopes)


if __name__ == "__main__":

    # set up command line argument parsing
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--src")
    group.add_argument("--expr")

    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument("--print-parse-tree", action= "store_true")
    print_group.add_argument("--print-ast", action= "store_true")
    print_group.add_argument("--print-symbol-table", action= "store_true")

    args = parser.parse_args()

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # extract expr from src file
    if src != None:
        src = str(src)

        # create a file descriptor for the src file
        with open(src,"r") as fd:
        
            # read all content of the file into an variable
            code = fd.readlines()
            expr = "".join(code)

    elif expr != None:
        expr = str(expr)

    elif src == None and expr == None:
        raise Exception("Either --src or --expr argument must be provided")
        

    print_parse_tree = args.print_parse_tree
    print_ast = args.print_ast
    print_symbol_table = args.print_symbol_table

    run(expr, print_parse_tree, print_ast, print_symbol_table)
