#!/usr/bin/python3

import argparse

import list as list_
import frontend
import backend


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

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--src")
    input_group.add_argument("--expr")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--output")
    output_group.add_argument("--frontend-print-token-list", action="store_true")
    output_group.add_argument("--frontend-print-token-tree", action="store_true")

    parser.add_argument("--frontend-compile-time-scope", action="store_true")

    args = parser.parse_args()

    # get the output file argument
    output = args.output

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # if src argument was given, extract expr from src file
    if src is not None:
        src = str(src)

        import os
        src = os.path.abspath(src)

        expr = read_file(src)

    # if expr argument was given, just convert expr to str
    elif expr is not None:
        expr = str(expr)

    # if none was given, raise exception
    elif src is None and expr is None:
        raise Exception("Either --src or --expr argument must be provided")

    # if no output argument was given, raise exception
    if output is None and args.frontend_print_token_list is False and args.frontend_print_token_tree is False:
        raise Exception("Either --output, --frontend-print-token-list or --frontend-print-token-tree argument must be provided")

    # run frontend to get tree
    frontend_tree = frontend.run(
        expr,
        src,
        args.frontend_print_token_list,
        args.frontend_print_token_tree,
        args.frontend_compile_time_scope
    )

    # run backend on tree
    result = backend.run(frontend_tree)

    print(f"result: {result}")

    # stringfy tree
    result = list_.list_stringfy(result)

    # write result to file
    output_ll = f"{output}.ll"
    with open(output_ll, "w") as output_fd:
        output_fd.write(result)

#    # run llvm optimization step
#    opt_output_ll = f"opt_{output_ll}"
#    f"opt -O3 {output_ll} -o {opt_output_ll}"
#
#    # generate assembly code
#    output_s = f"{output}.s"
#    f"llc {opt_output_ll} -o {output_s}"
#
#    # assemble to binary
#    f"llvm-as {output_s} -o {output}"
