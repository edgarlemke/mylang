#!/usr/bin/python3

import inspect as i
from subprocess import Popen, PIPE
from shlex import split


def _test (fn_name, expr, expected) :
    print(f"TEST {fn_name} - ", end="", flush= True)

    stdout, stderr = _expr(expr)

    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}")
        #exit()

    if stdout != expected:
        print(f"""FAIL - stdout not correct:
            expected:   {expected}
            got:        {stdout}""")
        #exit()

    print("OK")

def justprint (msg, expr, expected) :
    print(msg, end="", flush= True)

    stdout, stderr = _expr(expr)

    print(f"stdout: {stdout}")
    print(f"stderr: {stderr}")

    #exit()


#def test_rule__expr__value () :
#    _test(i.getframeinfo( i.currentframe() ).function, "anyvalue", """((EXPR ((VALUE 0 8 anyvalue))))""")

def test_rule__expr__quote_qvalue_quote () :
    _test(i.getframeinfo( i.currentframe() ).function, "\\\" \\\"", """((EXPR ((QUOTE 0 1 "\\\"") (QVALUE 1 2 " ") (QUOTE 2 3 "\\\""))))""")

def test_rule__expr__int () :
    _test(i.getframeinfo( i.currentframe() ).function, "1", """((EXPR ((INT 0 1 1))))""")

def test_rule__expr__float () :
    _test(i.getframeinfo( i.currentframe() ).function, "3.14", """((EXPR ((FLOAT 0 4 3.14))))""")

def test_rule__expr__true () :
    _test(i.getframeinfo( i.currentframe() ).function, "true", """((EXPR ((BOOL 0 4 true))))""")

def test_rule__expr__false () :
    _test(i.getframeinfo( i.currentframe() ).function, "false", """((EXPR ((BOOL 0 5 false))))""")


def test_rule__par_group__par_open_par_close () :
    _test(i.getframeinfo( i.currentframe() ).function, "()", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (PAR_CLOSE 1 2 ")"))))))""")

def test_rule__par_group__par_open_expr_par_close () :
    _test(i.getframeinfo( i.currentframe() ).function, "(\\\"abc\\\")", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (PAR_CLOSE 6 7 ")"))))))""")

#def test_rule__expr_group__expr_space_expr () :
#    """
#    Tests
#        EXPR_GROUP -> EXPR SPACE EXPR
#        PAR_GROUP -> PAR_OPEN EXPR_GROUP PAR_CLOSE
#    """
#    _test(i.getframeinfo( i.currentframe() ).function, "(\\\"abc\\\" \\\"xyz\\\")", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR_GROUP ((EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (SPACE 6 7 " ") (EXPR ((QUOTE 7 8 "\\\"") (QVALUE 8 11 xyz) (QUOTE 11 12 "\\\""))))) (PAR_CLOSE 12 13 ")"))))))""")

#def test_rule__expr_group__expr_group_space_expr () :
#    """
#    Tests
#        EXPR_GROUP -> EXPR_GROUP SPACE EXPR
#        PAR_GROUP -> PAR_OPEN EXPR_GROUP PAR_CLOSE
#    """
#    _test(
#            "TEST RULE  EXPR_GROUP -> EXPR_GROUP SPACE EXPR - ",
#            "(\\\"abc\\\" \\\"jkl\\\" \\\"xyz\\\")",
#            """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR_GROUP ((EXPR_GROUP ((EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (SPACE 6 7 " ") (EXPR ((QUOTE 7 8 "\\\"") (QVALUE 8 11 jkl) (QUOTE 11 12 "\\\""))))) (SPACE 12 13 " ") (EXPR ((QUOTE 13 14 "\\\"") (QVALUE 14 17 xyz) (QUOTE 17 18 "\\\""))))) (PAR_CLOSE 18 19 ")"))))))"""
#    )

def test_struct_0 () :
    _test(i.getframeinfo( i.currentframe() ).function, """struct MyStruct\n\tui8 i\n""", """((EXPR ((STRUCT_DECL ((STRUCT 0 6 struct) (SPACE 6 7 " ") (NAME 7 15 MyStruct) (STRUCT_BLOCK ((BLOCK_START 0) (NAMEPAIR ((NAME 17 20 ui8) (SPACE 20 21 " ") (NAME 21 22 i))) (BLOCK_END 0))))))))""")

def test_struct_1 () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """struct MyStruct\n\tui8 i\n\tui8 y\n""",
            """((EXPR ((STRUCT_DECL ((STRUCT 0 6 struct) (SPACE 6 7 " ") (NAME 7 15 MyStruct) (STRUCT_BLOCK ((BLOCK_START 0) (STRUCT_DEF_GROUP ((NAMEPAIR ((NAME 17 20 ui8) (SPACE 20 21 " ") (NAME 21 22 i))) (NAMEPAIR ((NAME 24 27 ui8) (SPACE 27 28 " ") (NAME 28 29 y))))) (BLOCK_END 0))))))))"""
    )

def test_res_struct () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """res struct MyStruct\n\tui8 i\n\tui8 y\n""",
            """((EXPR ((RES_STRUCT_DECL ((RES 0 3 res) (SPACE 3 4 " ") (STRUCT 4 10 struct) (SPACE 10 11 " ") (NAME 11 19 MyStruct) (STRUCT_BLOCK ((BLOCK_START 0) (STRUCT_DEF_GROUP ((NAMEPAIR ((NAME 21 24 ui8) (SPACE 24 25 " ") (NAME 25 26 i))) (NAMEPAIR ((NAME 28 31 ui8) (SPACE 31 32 " ") (NAME 32 33 y))))) (BLOCK_END 0))))))))"""
    )




def test_fn_decl_0 () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x)  ui8
\tnop""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 23 26 nop))) (BLOCK_END 0))))))))"""
    )

def test_fn_decl_1 () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x  ui8 y)  ui8
\tnop""",
"""((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (SPACE 15 16 " ") (SPACE 16 17 " ") (NAMEPAIR ((NAME 17 20 ui8) (SPACE 20 21 " ") (NAME 21 22 y))))) (PAR_CLOSE 22 23 ")"))) (SPACE 23 24 " ") (SPACE 24 25 " ") (NAME 25 28 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 30 33 nop))) (BLOCK_END 0))))))))"""
    )

def test_fn_decl_2 () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x)  ui8
\tnop
\tnop""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((EXPR ((NOP 23 26 nop))) (EXPR ((NOP 28 31 nop))))) (BLOCK_END 0))))))))"""
    )

def test_call_0 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn  ()""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (SPACE 29 30 " ") (SPACE 30 31 " ") (PAR_GROUP ((PAR_OPEN 31 32 "(") (PAR_CLOSE 32 33 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_call_1 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn  x""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (SPACE 29 30 " ") (SPACE 30 31 " ") (NAME 31 32 x))))) (BLOCK_END 0))))))))"""
    )

def test_call_2() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn  x y""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (SPACE 29 30 " ") (SPACE 30 31 " ") (NAMEPAIR ((NAME 31 32 x) (SPACE 32 33 " ") (NAME 33 34 y))))))) (BLOCK_END 0))))))))"""
    )

def test_call_3() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8\n
\tsomefn  x y z""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 24 30 somefn) (SPACE 30 31 " ") (SPACE 31 32 " ") (NAMEPAIR ((NAME 32 33 x) (SPACE 33 34 " ") (NAME 34 35 y))) (SPACE 35 36 " ") (NAME 36 37 z))))) (BLOCK_END 0))))))))"""
    )

def test_call_4() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn  x y z a""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (SPACE 29 30 " ") (SPACE 30 31 " ") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 31 32 x) (SPACE 32 33 " ") (NAME 33 34 y))) (SPACE 34 35 " ") (NAMEPAIR ((NAME 35 36 z) (SPACE 36 37 " ") (NAME 37 38 a))))))))) (BLOCK_END 0))))))))"""
    )

def test_call_5() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn  x y z a b""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (SPACE 29 30 " ") (SPACE 30 31 " ") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 31 32 x) (SPACE 32 33 " ") (NAME 33 34 y))) (SPACE 34 35 " ") (NAMEPAIR ((NAME 35 36 z) (SPACE 36 37 " ") (NAME 37 38 a))))) (SPACE 38 39 " ") (NAME 39 40 b))))) (BLOCK_END 0))))))))"""
    )

def test_call_6() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn  x y z a b c""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (SPACE 29 30 " ") (SPACE 30 31 " ") (NAMEPAIR_GROUP ((NAMEPAIR_GROUP ((NAMEPAIR ((NAME 31 32 x) (SPACE 32 33 " ") (NAME 33 34 y))) (SPACE 34 35 " ") (NAMEPAIR ((NAME 35 36 z) (SPACE 36 37 " ") (NAME 37 38 a))))) (SPACE 38 39 " ") (NAMEPAIR ((NAME 39 40 b) (SPACE 40 41 " ") (NAME 41 42 c))))))))) (BLOCK_END 0))))))))"""
    )

def test_call_7() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn(a)""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (PAR_GROUP ((PAR_OPEN 29 30 "(") (NAME 30 31 a) (PAR_CLOSE 31 32 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_call_8() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn(a b)""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (ARG_PAR_GROUP ((PAR_OPEN 29 30 "(") (NAMEPAIR ((NAME 30 31 a) (SPACE 31 32 " ") (NAME 32 33 b))) (PAR_CLOSE 33 34 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_call_9() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn(a b c)""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (ARG_PAR_GROUP ((PAR_OPEN 29 30 "(") (NAMEPAIR ((NAME 30 31 a) (SPACE 31 32 " ") (NAME 32 33 b))) (SPACE 33 34 " ") (NAME 34 35 c) (PAR_CLOSE 35 36 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_call_10() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn(a b c d)""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (ARG_PAR_GROUP ((PAR_OPEN 29 30 "(") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 30 31 a) (SPACE 31 32 " ") (NAME 32 33 b))) (SPACE 33 34 " ") (NAMEPAIR ((NAME 34 35 c) (SPACE 35 36 " ") (NAME 36 37 d))))) (PAR_CLOSE 37 38 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_call_11() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn(a b c d e)""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (ARG_PAR_GROUP ((PAR_OPEN 29 30 "(") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 30 31 a) (SPACE 31 32 " ") (NAME 32 33 b))) (SPACE 33 34 " ") (NAMEPAIR ((NAME 34 35 c) (SPACE 35 36 " ") (NAME 36 37 d))))) (SPACE 37 38 " ") (NAME 38 39 e) (PAR_CLOSE 39 40 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_call_12() :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tsomefn(a b c d e f)""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((NAME 23 29 somefn) (ARG_PAR_GROUP ((PAR_OPEN 29 30 "(") (NAMEPAIR_GROUP ((NAMEPAIR_GROUP ((NAMEPAIR ((NAME 30 31 a) (SPACE 31 32 " ") (NAME 32 33 b))) (SPACE 33 34 " ") (NAMEPAIR ((NAME 34 35 c) (SPACE 35 36 " ") (NAME 36 37 d))))) (SPACE 37 38 " ") (NAMEPAIR ((NAME 38 39 e) (SPACE 39 40 " ") (NAME 40 41 f))))) (PAR_CLOSE 41 42 ")"))))))) (BLOCK_END 0))))))))"""
    )

def test_ret () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tret true""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((RET_DECL ((RET 23 26 ret) (SPACE 26 27 " ") (EXPR ((BOOL 27 31 true))))))) (BLOCK_END 0))))))))"""
    )


def test_multiblock () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x)  ui8
\tnop
\tif true
\t\tif true
\t\t\tnop
\tnop
""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((EXPR ((EXPR ((NOP 23 26 nop))) (EXPR ((IF_DECL ((IF 28 30 if) (SPACE 30 31 " ") (EXPR ((BOOL 31 35 true))) (BLOCK ((BLOCK_START 1) (EXPR ((IF_DECL ((IF 38 40 if) (SPACE 40 41 " ") (EXPR ((BOOL 41 45 true))) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 49 52 nop))) (BLOCK_END 2))))))) (BLOCK_END 1))))))))) (EXPR ((NOP 54 57 nop))))) (BLOCK_END 0))))))))"""
            )


def test_set () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x)  ui8\n
\tset x ui8 1\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((SET_DECL ((SET 24 27 set) (SPACE 27 28 " ") (NAMEPAIR ((NAME 28 29 x) (SPACE 29 30 " ") (NAME 30 33 ui8))) (SPACE 33 34 " ") (EXPR ((INT 34 35 1))))))) (BLOCK_END 0))))))))"""
            )


def test_mut () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x)  ui8\n
\tmut x ui8 1\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((MUT_DECL ((MUT 24 27 mut) (SPACE 27 28 " ") (NAMEPAIR ((NAME 28 29 x) (SPACE 29 30 " ") (NAME 30 33 ui8))) (SPACE 33 34 " ") (EXPR ((INT 34 35 1))))))) (BLOCK_END 0))))))))"""
)


def test_if () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """fn main  (ui8 x)  ui8
\tif true
\t\tnop""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_DECL ((IF 23 25 if) (SPACE 25 26 " ") (EXPR ((BOOL 26 30 true))) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 33 36 nop))) (BLOCK_END 1))))))) (BLOCK_END 0))))))))"""
    )

def test_if_else () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tif true
\t\tnop
\telse
\t\tnop""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELSE_DECL ((IF_DECL ((IF 23 25 if) (SPACE 25 26 " ") (EXPR ((BOOL 26 30 true))) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 33 36 nop))) (BLOCK_END 1))))) (ELSE_DECL ((ELSE 38 42 else) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 45 48 nop))) (BLOCK_END 1))))))))) (BLOCK_END 0))))))))"""
    )

def test_if_elif () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tif test0
\t\tnop
\telif test1
\t\tnop""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_DECL ((IF_DECL ((IF 23 25 if) (SPACE 25 26 " ") (NAME 26 31 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 34 37 nop))) (BLOCK_END 1))))) (ELIF_DECL ((ELIF 39 43 elif) (SPACE 43 44 " ") (NAME 44 49 test1) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 52 55 nop))) (BLOCK_END 1))))))))) (BLOCK_END 0))))))))"""
    )

def test_if_elif_elif_elif () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tif test0
\t\tnop
\telif test1
\t\tnop
\telif test2
\t\tnop
\telif test3
\t\tnop""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_GROUP_DECL ((IF_DECL ((IF 23 25 if) (SPACE 25 26 " ") (NAME 26 31 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 34 37 nop))) (BLOCK_END 1))))) (ELIF_GROUP ((ELIF_GROUP ((ELIF_DECL ((ELIF 39 43 elif) (SPACE 43 44 " ") (NAME 44 49 test1) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 52 55 nop))) (BLOCK_END 1))))) (ELIF_DECL ((ELIF 57 61 elif) (SPACE 61 62 " ") (NAME 62 67 test2) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 70 73 nop))) (BLOCK_END 1))))))) (ELIF_DECL ((ELIF 75 79 elif) (SPACE 79 80 " ") (NAME 80 85 test3) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 88 91 nop))) (BLOCK_END 1))))))))))) (BLOCK_END 0))))))))"""
    )

def test_if_elif_else () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tif test0
\t\tnop
\telif test1
\t\tnop
\t\tnop
\telse
\t\tnop""",
    """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_ELSE_DECL ((IF_DECL ((IF 23 25 if) (SPACE 25 26 " ") (NAME 26 31 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 34 37 nop))) (BLOCK_END 1))))) (ELIF_DECL ((ELIF 39 43 elif) (SPACE 43 44 " ") (NAME 44 49 test1) (BLOCK ((BLOCK_START 1) (EXPR ((EXPR ((NOP 52 55 nop))) (EXPR ((NOP 58 61 nop))))) (BLOCK_END 1))))) (ELSE_DECL ((ELSE 63 67 else) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 70 73 nop))) (BLOCK_END 1))))))))) (BLOCK_END 0))))))))"""
    )

def test_if_elif_elif_elif_else () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tif test0
\t\tnop
\telif test1
\t\tnop
\telif test2
\t\tnop
\telif test3
\t\tnop
\telse
\t\tnop\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_GROUP_ELSE_DECL ((IF_DECL ((IF 23 25 if) (SPACE 25 26 " ") (NAME 26 31 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 34 37 nop))) (BLOCK_END 1))))) (ELIF_GROUP ((ELIF_GROUP ((ELIF_DECL ((ELIF 39 43 elif) (SPACE 43 44 " ") (NAME 44 49 test1) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 52 55 nop))) (BLOCK_END 1))))) (ELIF_DECL ((ELIF 57 61 elif) (SPACE 61 62 " ") (NAME 62 67 test2) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 70 73 nop))) (BLOCK_END 1))))))) (ELIF_DECL ((ELIF 75 79 elif) (SPACE 79 80 " ") (NAME 80 85 test3) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 88 91 nop))) (BLOCK_END 1))))))) (ELSE_DECL ((ELSE 93 97 else) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 100 103 nop))) (BLOCK_END 1))))))))) (BLOCK_END 0))))))))"""
    )


def test_while () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\twhile true
\t\tnop""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((WHILE_DECL ((WHILE 23 28 while) (SPACE 28 29 " ") (EXPR ((BOOL 29 33 true))) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 36 39 nop))) (BLOCK_END 1))))))) (BLOCK_END 0))))))))"""
    )

def test_for () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tfor i  array
\t\tnop""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((FOR_DECL ((FOR 23 26 for) (SPACE 26 27 " ") (NAME 27 28 i) (SPACE 28 29 " ") (SPACE 29 30 " ") (NAME 30 35 array) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 38 41 nop))) (BLOCK_END 1))))))) (BLOCK_END 0))))))))"""
    )

def test_for_2 () :
    _test(
        i.getframeinfo( i.currentframe() ).function,
        """fn main  (ui8 x)  ui8
\tfor i item  array
\t\tnop""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (ARG_PAR_GROUP ((PAR_OPEN 9 10 "(") (NAMEPAIR ((NAME 10 13 ui8) (SPACE 13 14 " ") (NAME 14 15 x))) (PAR_CLOSE 15 16 ")"))) (SPACE 16 17 " ") (SPACE 17 18 " ") (NAME 18 21 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((FOR_DECL ((FOR 23 26 for) (SPACE 26 27 " ") (NAMEPAIR ((NAME 27 28 i) (SPACE 28 29 " ") (NAME 29 33 item))) (SPACE 33 34 " ") (SPACE 34 35 " ") (NAME 35 40 array) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 43 46 nop))) (BLOCK_END 1))))))) (BLOCK_END 0))))))))"""
    )


def test_incl_pkg () :
    """
    Test for simple package incl-usion
    """
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """incl somepkg""",
            """((EXPR ((INCL_DECL ((INCL 0 4 incl) (SPACE 4 5 " ") (NAME 5 12 somepkg))))))"""
    )

def test_incl_pkg_2 () :
    """
    Test for package incl-usion with alias
    """
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """incl somepkg alias""",
            """((EXPR ((INCL_DECL ((INCL 0 4 incl) (SPACE 4 5 " ") (NAMEPAIR ((NAME 5 12 somepkg) (SPACE 12 13 " ") (NAME 13 18 alias))))))))"""
    )


#def test_incl_path () :
#    _test(
#            "TEST INCL \"path\" - ",
#            "incl \\\"path\\\"",
#            """((EXPR ((INCL_DECL ((INCL 0 4 incl) (SPACE 4 5 " ") (EXPR ((QUOTE 5 6 "\\\"") (QVALUE 6 10 path) (QUOTE 10 11 "\\\""))))))))"""
#    )

#def test_pkg () :
#    _test(
#            "TEST PKG somepkg - ",
#            """pkg somepkg
#\tnop\n""",
#        """((EXPR ((PKG_DECL ((PKG 0 3 pkg) (SPACE 3 4 " ") (NAME 4 11 somepkg) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 13 16 nop))) (BLOCK_END 0))))))))"""
#    )

def test_typedef () :
    _test(
            i.getframeinfo( i.currentframe() ).function,
            """typedef ui8 1
typedef i8 1

typedef ui16 2
typedef i16 2

typedef ui32 4
typedef i32 4

typedef ui64 8
typedef i64 8""",
    """((EXPR ((EXPR ((EXPR ((EXPR ((EXPR ((EXPR ((EXPR ((EXPR ((TYPEDEF_DECL ((TYPEDEF 0 7 typedef) (SPACE 7 8 " ") (NAME 8 11 ui8) (SPACE 11 12 " ") (EXPR ((INT 12 13 1))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 14 21 typedef) (SPACE 21 22 " ") (NAME 22 24 i8) (SPACE 24 25 " ") (EXPR ((INT 25 26 1))))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 28 35 typedef) (SPACE 35 36 " ") (NAME 36 40 ui16) (SPACE 40 41 " ") (EXPR ((INT 41 42 2))))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 43 50 typedef) (SPACE 50 51 " ") (NAME 51 54 i16) (SPACE 54 55 " ") (EXPR ((INT 55 56 2))))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 58 65 typedef) (SPACE 65 66 " ") (NAME 66 70 ui32) (SPACE 70 71 " ") (EXPR ((INT 71 72 4))))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 73 80 typedef) (SPACE 80 81 " ") (NAME 81 84 i32) (SPACE 84 85 " ") (EXPR ((INT 85 86 4))))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 88 95 typedef) (SPACE 95 96 " ") (NAME 96 100 ui64) (SPACE 100 101 " ") (EXPR ((INT 101 102 8))))))))) (EXPR ((TYPEDEF_DECL ((TYPEDEF 103 110 typedef) (SPACE 110 111 " ") (NAME 111 114 i64) (SPACE 114 115 " ") (EXPR ((INT 115 116 8))))))))))"""
    )



def test_invalid_syntax () :
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    stdout, stderr = _expr("())")

    expected = "Invalid syntax!"
    if not (expected in stderr):
        print(f"""FAIL - stderr not correct
                expected: {expected}
                got: {stderr}
                stdout: {stdout}""")
        #exit()

    print("OK")

def test_abstract () :
    print(f"TEST {i.getframeinfo( i.currentframe() ).function} - ", end="")

    expr = """fn main  (ui8 x)  ui8
\tif true
\t\tnop
\telif true
\t\tnop
\telse
\t\tnop
\twhile true
\t\tnop
\tfor i  array
\t\tnop
"""

    expected = """(EXPR (FN_DECL ((NAME main) (ARG_PAR_GROUP (((NAME ui8) (NAME x)))) (NAME ui8) ((EXPR ((EXPR ((EXPR (IF_ELIF_ELSE_DECL ((IF_DECL ((EXPR (BOOL true)) ((EXPR (NOP))))) (ELIF_DECL ((EXPR (BOOL true)) ((EXPR (NOP))))) (ELSE_DECL ((EXPR (NOP))))))) (EXPR (WHILE_DECL ((EXPR (BOOL true)) ((EXPR (NOP)))))))) (EXPR (FOR_DECL ((NAME i) (NAME array) ((EXPR (NOP))))))))))))"""

    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-raw-ast"
    sp = split(cmd)

    stdout, stderr = _popen(sp)

    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}")

    if stdout != expected:
        print(f"""FAIL - stdout not correct:
            expected:   {expected}
            got:        {stdout}""")

    print("OK")



def _expr (expr):
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-parse-tree"
#    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-token-list"
    sp = split(cmd)
    return _popen(sp)

def _popen (sp) :
    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f")
    args = parser.parse_args()

    if args.f is None:
        tests = [t for t in globals() if t[0:5] == "test_"]
        for t in tests:
            eval(f"{t}()")

    else:
        eval(f"{args.f}()")
