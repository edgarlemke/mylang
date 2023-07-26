import argparse
import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)


def run_li(li, print_output=False):
    import eval
    import backend.scope as scope

    eval_li = eval.eval(li, scope.scope, ["handle"])

    if print_output:
        print(list_.list_print(eval_li))
        exit()

    return eval_li


def run(expr, print_output=False):
    import eval
    import backend.scope as scope
    import list as list_

    expr_li = _get_list_from_expr(expr)
    eval_li = eval.eval(expr_li, scope.scope, ["handle"])

    if print_output:
        print(list_.list_print(eval_li))
        exit()

    return eval_li


def _get_list_from_expr(expr, print_token_list=False, print_token_tree=False):
    import frontend.run as fer
    return fer._get_list_from_expr(expr, print_token_list, print_token_tree)


def _read_file(src):
    import run
    return run.read_file(src)


if __name__ == "__main__":

    # set up command line argument parsing
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--src")
    group.add_argument("--expr")

    print_group = parser.add_mutually_exclusive_group()
#    print_group.add_argument("--print-token-list", action="store_true")
#    print_group.add_argument("--print-token-tree", action="store_true")
    print_group.add_argument("--print-output", action="store_true")

#    parser.add_argument("--compile-time-scope", action="store_true")

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

        expr = _read_file(src)

    elif expr is not None:
        expr = str(expr)

    elif src is None and expr is None:
        raise Exception("Either --src or --expr argument must be provided")

    run(
        expr,
#        src,
#        args.print_token_list,
#        args.print_token_tree,
        args.print_output,
#        args.compile_time_scope
    )
