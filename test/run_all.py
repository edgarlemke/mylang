#!/usr/bin/python3

from subprocess import run


import shared
import lex
import frontend_eval
import frontend_eval_runtime
import backend
import run.run


if __name__ == "__main__":

    args = shared.parse_args()

    test_ct, ok_ct, failed_ct = 0, 0, 0

    for mod in [lex, frontend_eval, frontend_eval_runtime, backend, run.run]:
        result = mod.run(**args)
        test_ct += result[0]
        ok_ct += result[1]
        failed_ct += result[2]

        print("\n.....\n")

        if args["stop"] and failed_ct > 0:
            break

    ok_perc = ok_ct * 100 / test_ct
    failed_perc = failed_ct * 100 / test_ct

    print(f"""RESULTS
Tests: {test_ct} - Passed: {ok_ct} ({ok_perc:.2f}%) - Failed: {failed_ct} ({failed_perc:.2f}%)
""")
