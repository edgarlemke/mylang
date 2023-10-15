#!/usr/bin/python3

import argparse
import os
from subprocess import run
import shlex

import list as list_
import frontend
import backend
# from shared import read_file
import shared


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
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # get the output file argument
    output = args.output

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # setup DEBUG
    shared.DEBUG = args.debug

    # if src argument was given, extract expr from src file
    if src is not None:
        src = str(src)
        src = os.path.abspath(src)
        expr = shared.read_file(src)

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
    # print("Running frontend on input")
    from frontend.run import run as frontend_run
    frontend_tree = frontend_run(
        expr,
        src,
        args.frontend_print_token_list,
        args.frontend_print_token_tree,
        args.frontend_compile_time_scope
    )

    output_parse = f"{output}.parse"
    with open(output_parse, "w") as output_fd:
        output_fd.write(list_.list_print(frontend_tree))

    # run backend on tree
    # print("Running backend on frontend result...")
    from backend.run import run_li as backend_run_li
    result = backend_run_li(frontend_tree)

    # write result to file
    output_ll = f"{output}.ll"
    # print(f"Writing backend result to {output_ll}")
    with open(output_ll, "w") as output_fd:
        output_fd.write(result)

#    # run llvm optimization step
#    opt_output_ll = f"opt_{output_ll}"
#    f"opt -O3 {output_ll} -o {opt_output_ll}"
#

    # generate assembly code
    output_s = f"{output}.s"
    # print(f"Generating assembly code to {output_s}")
    run(shlex.split(f"llc {output_ll} -o {output_s}"))

    # assemble it
    # print(f"Running assembler on {output_s}")
    run(shlex.split(f"as {output_s} -o {output}"))

    # print(f"Done")
