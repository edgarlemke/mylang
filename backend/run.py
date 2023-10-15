import argparse

import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)

import eval
import backend.scope as scope
import list as list_
import shared
from shared import debug


def run_li(li, print_output=False):
    # print(f"!! run_li: {li}")

    default = """(
(set const stdin (int 0))
(set const stdout (int 1))
(set const stderr (int 2))

(fn print ((text Str)) ((linux_write stdout text)))
(fn print ((text (Array byte))) ((linux_write stdout text)))

(fn add ((x int) (y int)) int ((add_int_int x y)))
(fn sub ((x int) (y int)) int ((sub_int_int x y)))
(fn mul ((x int) (y int)) int ((mul_int_int x y)))
(fn div ((x int) (y int)) float ((div_int_int x y)))
(fn and ((x int) (y int)) int ((and_int_int x y)))
(fn or ((x int) (y int)) int ((or_int_int x y)))
(fn xor ((x int) (y int)) int ((xor_int_int x y)))
(fn not ((x int)) int ((not_int x)))
(fn eq ((x int) (y int)) bool ((eq_int_int x y)))
(fn gt ((x int) (y int)) bool ((gt_int_int x y)))
(fn ge ((x int) (y int)) bool ((ge_int_int x y)))
(fn lt ((x int) (y int)) bool ((lt_int_int x y)))
(fn le ((x int) (y int)) bool ((le_int_int x y)))
(fn shl ((x int) (y int)) int ((shl_int_int x y)))
(fn shr ((x int) (y int)) int ((shr_int_int x y)))

(fn add ((x uint) (y uint)) uint ((add_uint_uint x y)))
(fn sub ((x uint) (y uint)) uint ((sub_uint_uint x y)))
(fn mul ((x uint) (y uint)) uint ((mul_uint_uint x y)))
(fn div ((x uint) (y uint)) float ((div_uint_uint x y)))
(fn and ((x uint) (y uint)) uint ((and_uint_uint x y)))
(fn or ((x uint) (y uint)) uint ((or_uint_uint x y)))
(fn xor ((x uint) (y uint)) uint ((xor_uint_uint x y)))
(fn not ((x uint)) uint ((not_uint x)))
(fn eq ((x uint) (y uint)) bool ((eq_uint_uint x y)))
(fn gt ((x uint) (y uint)) bool ((gt_uint_uint x y)))
(fn ge ((x uint) (y uint)) bool ((ge_uint_uint x y)))
(fn lt ((x uint) (y uint)) bool ((lt_uint_uint x y)))
(fn le ((x uint) (y uint)) bool ((le_uint_uint x y)))
(fn shl ((x uint) (y int)) int ((shl_uint_int x y)))
(fn shr ((x uint) (y int)) int ((shr_uint_int x y)))

(fn add ((x float) (y float)) float ((add_float_float x y)))
(fn sub ((x float) (y float)) float ((sub_float_float x y)))
(fn mul ((x float) (y float)) float ((mul_float_float x y)))
(fn div ((x float) (y float)) float ((div_float_float x y)))
(fn eq ((x float) (y float)) bool ((eq_float_float x y)))
(fn gt ((x float) (y float)) bool ((gt_float_float x y)))
(fn ge ((x float) (y float)) bool ((ge_float_float x y)))
(fn lt ((x float) (y float)) bool ((lt_float_float x y)))
(fn le ((x float) (y float)) bool ((le_float_float x y)))

(fn eq ((x bool) (y bool)) bool ((eq_bool_bool x y)))
(fn and ((x bool) (y bool)) bool ((and_bool_bool x y)))
(fn or ((x bool) (y bool)) bool ((or_bool_bool x y)))
(fn xor ((x bool) (y bool)) bool ((xor_bool_bool x y)))
(fn not ((x bool)) bool ((not_bool x)))
)
"""
    li = _get_list_from_expr(default) + li

    eval_li = eval.eval(li, scope.scope)

    default_llvm_ir = """define i64 @linux_write (i64 %fildes, i8* %buf, i64 %nbyte) {
start:
%retv = call i64 asm sideeffect "syscall",
        "={rax},{rax},{rdi},{rsi},{rdx}"
        (i64 1, i64 %fildes, i8* %buf, i64 %nbyte)
ret i64 %retv
}

%struct.Str = type {i8*, i64}

%Array_byte = type {i8*, i64}
"""

    output = default_llvm_ir + _join_lists(eval_li)

    if print_output:
        # print(list_.list_print(eval_li))
        print(output)
        exit()

    return output


def run(expr, print_output=False):
    expr_li = _get_list_from_expr(expr)
    eval_li = eval.eval(expr_li, scope.scope)

    debug(f"run():  eval_li: {eval_li}")

    output = _join_lists(eval_li)

    if print_output:
        # print(list_.list_print(eval_li))
        print(output)
        exit()

    return output


def _get_list_from_expr(expr, print_token_list=False, print_token_tree=False):
    import frontend.run as fer
    return fer._get_list_from_expr(expr, print_token_list, print_token_tree)


def _join_lists(li):
    # print(f"_join_lists: {li}")

    lines = []

    def iter(li):
        # print(f"li: {li}")
        for item in li:
            if isinstance(item, list):
                iter(item)
            else:
                lines.append(item)
    iter(li)

    debug(f"lines: {lines}")

    return "\n".join(lines)


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
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # setup DEBUG
    shared.DEBUG = args.debug

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
#        src,
#        args.print_token_list,
#        args.print_token_tree,
        args.print_output,
#        args.compile_time_scope
    )
