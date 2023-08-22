import argparse
import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)


def run(
    expr,
    src=None,
    print_token_list=False,
    print_token_tree=False,
    print_output=False,
    compile_time_scope=False
):
    import eval
    import list as list_
    import frontend.compiletime as compiletime
    import frontend.runtime as runtime

    # print(f"print_token_list: {print_token_list}")
    # print(f"print_token_tree: {print_token_tree}")

    _setup_env(compile_time_scope)

    expr_li = _get_list_from_expr(expr, print_token_list=print_token_list, print_token_tree=print_token_tree)
    # print(f"expr_li: {expr_li}")

    if compile_time_scope:
        eval_li = eval.eval(expr_li, compiletime.scope, ["handle"])
    else:
        eval_li = eval.eval(expr_li, runtime.scope, ["handle"])

    if print_output:
        print(list_.list_print(eval_li))
        exit()

    return eval_li


def _get_list_from_expr(expr, print_token_list=False, print_token_tree=False):
    # from pprint import pprint
    import lex
    import parse

    token_list = lex.tokenize(expr)
    if print_token_list:
        print(list_.list_print(token_list), end="")
        exit()

    # print(f"tokenize token_list: {pprint(token_list)}\n")

    token_list = parse.parse(token_list)
    if print_token_tree:
        print(list_.list_print(token_list), end="")
        exit()

    # print(f"parse token_list: {pprint(token_list)}\n")

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
        # print(f"reduce {li}")
        lic = li.copy()
        for index, i in enumerate(lic):
            if len(i) > 0:
                if i[0] == "TOKEN":
                    # print(f"i: {i}")
                    lic[index] = i[4]

                elif i[0] == "LIST":
                    lic[index] = i[1]

            for subitem_i, subitem in enumerate(i):
                if type(subitem) != list:
                    continue

                reduced_subitem = reduce(subitem)

                if i[0] == "LIST":
                    lic[index] = reduced_subitem
                # elif i[0] == "BLOCK":
                #    lic[index][1] = reduced_subitem
                #    lic[index].remove("BLOCK")

        # print(f"reduce {li} -> {lic}\n")
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
    # print(f"reduce {token_list}\n")

    lic = remove(token_list)
    # print(f"remove lic {lic}\n")

    return lic


def _setup_env(compiletime_scope=False):
    import eval
    import frontend.compiletime as compiletime
    import frontend.runtime as runtime

    scope = runtime.scope if compiletime_scope == False else compiletime.scope

    # Macros declared first are matched first...
    default = """
macro op_mul ('a * 'b) ((mul 'a 'b))
macro op_div ('a / 'b) ((div 'a 'b))
macro op_mod ('a % 'b) ((mod 'a 'b))

macro op_add ('a + 'b) ((add 'a 'b))
macro op_sub ('a - 'b) ((sub 'a 'b))

macro op_shl ('a << 'b) ((shl 'a 'b))
macro op_shr ('a >> 'b) ((shr 'a 'b))

macro op_and ('a and 'b) ((and 'a 'b))
macro op_or  ('a or 'b) ((or 'a 'b))
macro op_xor ('a xor 'b) ((xor 'a 'b))

macro op_eq  ('a == 'b) ((eq 'a 'b))
macro op_neq ('a != 'b) ((not (eq 'a 'b)))
macro op_gt  ('a > 'b)  ((gt 'a 'b))
macro op_gte ('a >= 'b) ((ge 'a 'b))
macro op_lt  ('a < 'b)  ((lt 'a 'b))
macro op_lte ('a <= 'b) ((le 'a 'b))

macro op_ternary ('a ? 'b : 'c) (if ('a) ('b) ('c))

macro op_set_fn_with_return (fn 'f 'args 'rt 'body) (set mut 'f (fn ('args 'rt 'body)))
macro op_set_fn_without_return (fn 'f 'args 'body) (set mut 'f (fn ('args 'body)))

macro op_set_mut_generic_struct (mut struct 'a = 'b 'c) (set mut 'a (struct 'b 'c))
macro op_set_generic_struct (struct 'a = 'b 'c) (set const 'a (struct ('b 'c)))

macro op_set_mut_struct (mut struct 'a = 'b) (set mut 'a (struct (() 'b)))
macro op_set_struct (struct 'a = 'b) (set const 'a (struct (() 'b)))

macro op_set_mut (mut 't 'a = 'b) (set mut 'a ('t 'b))
macro op_set_const ('t 'a = 'b) (set const 'a ('t 'b))

macro ret (ret) ()
"""
    fn_li = _get_list_from_expr(default)
    eval.eval(fn_li, scope)


if __name__ == "__main__":

    # set up command line argument parsing
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--src")
    group.add_argument("--expr")

    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument("--print-token-list", action="store_true")
    print_group.add_argument("--print-token-tree", action="store_true")
    print_group.add_argument("--print-output", action="store_true")

    parser.add_argument("--compile-time-scope", action="store_true")

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

        from shared import read_file
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
        args.print_output,
        args.compile_time_scope
    )
