def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stop", action="store_true", help="Stop testing when the first test fails")
    parser.add_argument("-k", "--keep", action="store_true", help="Keep compilation files instead of deleting them after the tests")
    parser.add_argument("--debug", action="store_true", help="Enable debug messages")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fast", action="store_true", help="Run only fast tests")
    group.add_argument("-f", help="Run only the given test function")
    args = parser.parse_args()

    return vars(args)


def run(*args, **kwargs):  # eval_str, msg, slow, globals_, f= None, fast= False, stop= False, keep= False):
    return _run("{t}({debug})", *args, **kwargs)


def run_keep(*args, **kwargs):  # eval_str, msg, slow, globals_, f= None, fast= False, stop= False, keep= False):
    return _run("{t}({keep}, {debug})", *args, **kwargs)


def _run(eval_str, msg, slow, globals_, f=None, fast=False, stop=False, keep=False, debug=False):

    fast_str = "(fast only tests)" if fast else ""
    print(f"{msg} {fast_str}\n")

    test_ct, ok_ct, failed_ct = 0, 0, 0

    if f is None:
        tests = [t for t in globals_ if t[0:5] == "test_" and callable(eval(t, globals_))]
        for t in tests:

            if fast and t in slow:
                continue

            result = eval(eval_str.format(t=t, keep=keep, debug=debug), globals_)
            test_ct += 1
            if result:
                ok_ct += 1
            else:
                failed_ct += 1

                if stop:
                    break

    else:
        result = eval(eval_str.format(t=f, keep=keep, debug=debug), globals_)
        test_ct += 1
        if result:
            ok_ct += 1
        else:
            failed_ct += 1

    print(f"\nTests: {test_ct} - Passed: {ok_ct} - Failed: {failed_ct}")

    return (test_ct, ok_ct, failed_ct)
