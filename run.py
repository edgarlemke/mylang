#!/usr/bin/python3

import argparse

import lex
import parse
import pkg
import seman, seman.fn
import list as list_


def run (
    expr,
    src= None,
    print_parse_tree= False,
    print_raw_ast= False,
    print_final_ast= False,
    print_symbol_table= False,
    loaded_pkg_files= None
    ) :


    token_list = lex.tokenize(expr) 
    parsetree = parse.parse(token_list, "EXPR")

    if print_parse_tree:
        print( list_.list_print(parsetree), end="" )
        exit()

    ast = parse.abstract(parsetree.copy())
    if print_raw_ast:
        print( list_.list_print(ast), end="" )
        exit()

    s_tree = parse.serialize_tree(ast)

    # get symbol table and scopes
    symtbl, scopes = seman.get_symtbl(s_tree)

    # get types from expr typedef declarations
    expr_types = seman.get_types(s_tree, scopes)

    pkg_name = pkg.get_pkg_name(src)

    # get loaded packages info
    loaded_pkgs = pkg.load_pkgs(s_tree, src, loaded_pkg_files)
    #print(f"\npkg: {pkg_name}\n loaded_pkgs: {loaded_pkgs}\n")

    # get types to substitute
    #
    all_types = [t for t in expr_types]

    # fill all_types with types from loaded packages
    for pkg_name_ in loaded_pkgs:
        pkg_ = loaded_pkgs[ pkg_name_ ]
        pkg_s_tree, pkg_symtbl, pkg_scopes, pkg_types = list(pkg_)

        all_types += pkg_types
    #
    #

    # substitute types in tree
    seman.subst_types(s_tree, all_types)


    # extract function declarations from tree
    #print(pkg_name)
    tree_fn_decls = seman.fn.extract_fn_decls(s_tree, symtbl, pkg_name)
    #print(f"tree_fn_decls: {tree_fn_decls}")

    all_fn_decls = tree_fn_decls.copy()

    # extract function declarations from packages
    pkgs_fn_decls = {}
    for pkg_name in loaded_pkgs:
        pkg_s_tree, pkg_symtbl, pkg_scopes, pkg_types = list(pkg_)
        fn_decls = seman.fn.extract_fn_decls(pkg_s_tree, pkg_symtbl, pkg_name)

        #print(fn_decls)
        for k in fn_decls:
            fn_decl_li = fn_decls[k]

            for j in fn_decl_li:

                if k not in all_fn_decls.keys():
                    all_fn_decls[k] = []

                all_fn_decls[k].append( j )


    #print(f"all_fn_decls: {all_fn_decls}")
 

    seman.check(s_tree, symtbl, scopes, all_fn_decls)

    if print_final_ast:
        print( list_.list_print(s_tree), end="" )
        exit()


    return (s_tree, symtbl, scopes, expr_types)


def read_file (src):
    # create a file descriptor for the src file
    with open(src,"r") as fd:
    
        # read all content of the file into an variable
        code = fd.readlines()
        expr = "".join(code)

        return expr




if __name__ == "__main__":

    # set up command line argument parsing
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--src")
    group.add_argument("--expr")

    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument("--print-parse-tree", action= "store_true")
    print_group.add_argument("--print-raw-ast", action= "store_true")
    print_group.add_argument("--print-final-ast", action= "store_true")
    print_group.add_argument("--print-symbol-table", action= "store_true")

    args = parser.parse_args()

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # extract expr from src file
    if src != None:
        src = str(src)

        import os
        src = os.path.abspath(src)

        expr = read_file(src)

    elif expr != None:
        expr = str(expr)

    elif src == None and expr == None:
        raise Exception("Either --src or --expr argument must be provided")
        

    print_parse_tree = args.print_parse_tree
    print_raw_ast = args.print_raw_ast
    print_final_ast = args.print_final_ast
    print_symbol_table = args.print_symbol_table

    run(expr, src, print_parse_tree, print_raw_ast, print_final_ast, print_symbol_table)
