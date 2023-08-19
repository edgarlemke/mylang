import argparse
import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)


def run_li(li, print_output=False):
    # print(f"!! run_li: {li}")
    import eval
    import backend.scope as scope

    default = """(
(set const stdin (int 0))
(set const stdout (int 1))
(set const stderr (int 2))

(set mut print (fn (((text Str)) ((linux_write stdout text)))))

(set mut add (fn (((x int) (y int)) int ((add_int_int x y)))))
(set mut sub (fn (((x int) (y int)) int ((sub_int_int x y)))))
(set mut mul (fn (((x int) (y int)) int ((mul_int_int x y)))))
(set mut div (fn (((x int) (y int)) float ((div_int_int x y)))))
(set mut and (fn (((x int) (y int)) int ((and_int_int x y)))))
(set mut or (fn (((x int) (y int)) int ((or_int_int x y)))))
(set mut xor (fn (((x int) (y int)) int ((xor_int_int x y)))))
(set mut not (fn (((x int)) int ((not_int x)))))
(set mut eq (fn (((x int) (y int)) bool ((eq_int_int x y)))))
(set mut gt (fn (((x int) (y int)) bool ((gt_int_int x y)))))
(set mut ge (fn (((x int) (y int)) bool ((ge_int_int x y)))))
(set mut lt (fn (((x int) (y int)) bool ((lt_int_int x y)))))
(set mut le (fn (((x int) (y int)) bool ((le_int_int x y)))))

(set mut add (fn (((x uint) (y uint)) uint ((add_uint_uint x y)))))
(set mut sub (fn (((x uint) (y uint)) uint ((sub_uint_uint x y)))))
(set mut mul (fn (((x uint) (y uint)) uint ((mul_uint_uint x y)))))
(set mut div (fn (((x uint) (y uint)) float ((div_uint_uint x y)))))
(set mut and (fn (((x uint) (y uint)) uint ((and_uint_uint x y)))))
(set mut or (fn (((x uint) (y uint)) uint ((or_uint_uint x y)))))
(set mut xor (fn (((x uint) (y uint)) uint ((xor_uint_uint x y)))))
(set mut not (fn (((x uint)) uint ((not_uint x)))))
(set mut eq (fn (((x uint) (y uint)) bool ((eq_uint_uint x y)))))
(set mut gt (fn (((x uint) (y uint)) bool ((gt_uint_uint x y)))))
(set mut ge (fn (((x uint) (y uint)) bool ((ge_uint_uint x y)))))
(set mut lt (fn (((x uint) (y uint)) bool ((lt_uint_uint x y)))))
(set mut le (fn (((x uint) (y uint)) bool ((le_uint_uint x y)))))

(set mut add (fn (((x float) (y float)) float ((add_float_float x y)))))
(set mut sub (fn (((x float) (y float)) float ((sub_float_float x y)))))
(set mut mul (fn (((x float) (y float)) float ((mul_float_float x y)))))
(set mut div (fn (((x float) (y float)) float ((div_float_float x y)))))
(set mut eq (fn (((x float) (y float)) bool ((eq_float_float x y)))))
(set mut gt (fn (((x float) (y float)) bool ((gt_float_float x y)))))
(set mut ge (fn (((x float) (y float)) bool ((ge_float_float x y)))))
(set mut lt (fn (((x float) (y float)) bool ((lt_float_float x y)))))
(set mut le (fn (((x float) (y float)) bool ((le_float_float x y)))))

(set mut eq (fn (((x bool) (y bool)) bool ((eq_bool_bool x y)))))
(set mut and (fn (((x bool) (y bool)) bool ((and_bool_bool x y)))))
(set mut or (fn (((x bool) (y bool)) bool ((or_bool_bool x y)))))
(set mut xor (fn (((x bool) (y bool)) bool ((xor_bool_bool x y)))))
(set mut not (fn (((x bool)) bool ((not_bool x)))))

)
"""
    li = _get_list_from_expr(default) + li

    eval_li = eval.eval(li, scope.scope, ["handle"])

    default_llvm_ir = """define i64 @linux_write (i64 %fildes, i8* %buf, i64 %nbyte) {
start:
%retv = call i64 asm sideeffect "syscall",
        "={rax},{rax},{rdi},{rsi},{rdx}"
        (i64 1, i64 %fildes, i8* %buf, i64 %nbyte)
ret i64 %retv
}

%struct.Str = type {i8*, i64}

"""

    output = default_llvm_ir + _join_lists(eval_li)

    if print_output:
        # print(list_.list_print(eval_li))
        print(output)
        exit()

    return output


def run(expr, print_output=False):
    import eval
    import backend.scope as scope
    import list as list_

    DEBUG = False

    expr_li = _get_list_from_expr(expr)
    eval_li = eval.eval(expr_li, scope.scope, ["handle"])

    if DEBUG:
        print(f"run():  eval_li: {eval_li}")

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

    DEBUG = False

    lines = []

    def iter(li):
        # print(f"li: {li}")
        for item in li:
            if isinstance(item, list):
                iter(item)
            else:
                lines.append(item)
    iter(li)

    if DEBUG:
        print(f"lines: {lines}")

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
#        src,
#        args.print_token_list,
#        args.print_token_tree,
        args.print_output,
#        args.compile_time_scope
    )
