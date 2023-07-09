#!/usr/bin/python3

import argparse

import lex
import parse
import eval
import list as list_


def run(
    expr,
    src=None,
    print_token_list=False,
    print_token_tree=False,
    #    print_raw_ast=False,
    #    print_final_ast=False,
    #    print_symbol_table=False,
    #    loaded_pkg_files=None
):

    setup_env()

    lic = get_list_from_expr(expr)
    eval_li = eval.eval(lic, None)

    print(list_.list_print(eval_li))

    return eval_li


def get_list_from_expr(expr, print_token_list=False, print_token_tree=False):
    token_list = lex.tokenize(expr)
    if print_token_list:
        print(list_.list_print(token_list), end="")
        exit()

    token_list = parse.parse(token_list)
    if print_token_tree:
        print(list_.list_print(token_list), end="")
        exit()

#    # remove LIST from actual lists recursively
#    def iterdown(token_list):
#        tc = token_list.copy()
#        for index, token in enumerate(token_list):
#            if token[0] == "LIST":
#                tc[index] = iterdown(token[1])
#
#        return tc
#
#    tc = iterdown(tc2)

    def reduce(li):
        # print(f"CLEAN {li}\n")
        lic = li.copy()
        for index, i in enumerate(lic):
            if len(i) > 0:
                if i[0] == "TOKEN":
                    lic[index] = i[4]

                elif i[0] == "LIST":
                    lic[index] = i[1]

            for subitem_i, subitem in enumerate(i):
                if type(subitem) != list:
                    continue

                reduced_subitem = reduce(subitem)

                if i[0] == "LIST":
                    lic[index] = reduced_subitem
                elif i[0] == "BLOCK":
                    lic[index][1] = reduced_subitem
                    lic[index].remove("BLOCK")

        return lic

    def remove(li):
        lic = li.copy()

        to_remove = []
        to_subst = []

        for index, item in enumerate(lic):
            if type(item) == list:
                lic[index] = remove(item)

            if item in [" "]:
                # print(f"should remove {index} from {lic}")
                to_remove.append(index)

        lic2 = lic.copy()
        for i in reversed(to_remove):
            lic2.pop(i)

        return lic2

    token_list = reduce(token_list)
    # print(f"reduce {token_list}")

    lic = remove(token_list)
    # print(f"lic {lic}")

    return lic


def setup_env():
    # Macros declared first are matched first...
    default_macros = """
(macro op_mul ('a * 'b) (mul ('a 'b)))
(macro op_div ('a / 'b) (div ('a 'b)))
(macro op_mod ('a % 'b) (mod ('a 'b)))

(macro op_add ('a + 'b) (add ('a 'b)))
(macro op_sub ('a - 'b) (sub ('a 'b)))

(macro op_eq  ('a == 'b) (eq  ('a 'b)))
(macro op_neq ('a != 'b) (neq ('a 'b)))
(macro op_gt  ('a > 'b)  (gt  ('a 'b)))
(macro op_gte ('a >= 'b) (gte ('a 'b)))
(macro op_lt  ('a < 'b)  (lt  ('a 'b)))
(macro op_lte ('a <= 'b) (lte ('a 'b)))

(macro op_ternary ('a ? 'b : 'c) (if ('a) ('b) ('c)))

(macro op_set ('a = 'b) (set 'a 'b))

(macro ret (ret) ())
"""

    op_li = get_list_from_expr(default_macros)
    # print(f"op_li: {op_li}")
    eval.eval(op_li, None)

    default_functions = """
"""
    fn_li = get_list_from_expr(default_functions)
    eval.eval(fn_li, None)


def read_file(src):
    # create a file descriptor for the src file
    with open(src, "r") as fd:

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
    print_group.add_argument("--print-token-list", action="store_true")
    print_group.add_argument("--print-token-tree", action="store_true")
#    print_group.add_argument("--print-raw-ast", action="store_true")
#    print_group.add_argument("--print-final-ast", action="store_true")
#    print_group.add_argument("--print-symbol-table", action="store_true")
#
    args = parser.parse_args()

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # extract expr from src file
    if src is not None:
        src = str(src)

        import os
        src = os.path.abspath(src)

        expr = read_file(src)

    elif expr is not None:
        expr = str(expr)

    elif src is None and expr is None:
        raise Exception("Either --src or --expr argument must be provided")

    run(
        expr,
        src,
        args.print_token_list,
        args.print_token_tree,
        #        args.print_raw_ast,
        #        args.print_final_ast,
        #        args.print_symbol_table
    )
