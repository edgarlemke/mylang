#!/usr/bin/python3

from subprocess import Popen, PIPE
from shlex import split


def basictest (msg, expr, expected) :
    print(msg, end="", flush= True)

    stdout, stderr = _popen(expr)

    if stderr != "":
        print(f"FAIL - stderr not empty: {stderr}")
        exit()

    if stdout != expected:
        print(f"""FAIL - stdout not corrent:
            expected:   {expected}
            got:        {stdout}""")
        exit()

    print("OK")

def justprint (msg, expr, expected) :
    print(msg, end="", flush= True)

    stdout, stderr = _popen(expr)

    print(f"stdout: {stdout}")
    print(f"stderr: {stderr}")

    exit()


#def test_rule__expr__value () :
#    basictest("TEST RULE  EXPR -> VALUE - ", "anyvalue", """((EXPR ((VALUE 0 8 anyvalue))))""")

def test_rule__expr__quote_qvalue_quote () :
    basictest("TEST RULE  EXPR -> QUOTE QVALUE QUOTE - ", "\\\" \\\"", """((EXPR ((QUOTE 0 1 "\\\"") (QVALUE 1 2 " ") (QUOTE 2 3 "\\\""))))""")

def test_rule__expr__int () :
    basictest("TEST RULE  EXPR -> INT - ", "1", """((EXPR ((INT 0 1 1))))""")

def test_rule__expr__float () :
    basictest("TEST RULE  EXPR -> FLOAT - ", "3.14", """((EXPR ((FLOAT 0 4 3.14))))""")


def test_rule__par_group__par_open_par_close () :
    basictest("TEST RULE  PAR_GROUP -> PAR_OPEN PAR_CLOSE - ", "()", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (PAR_CLOSE 1 2 ")"))))))""")

def test_rule__par_group__par_open_expr_par_close () :
    basictest("TEST RULE  PAR_GROUP -> PAR_OPEN EXPR PAR_CLOSE - ", "(\\\"abc\\\")", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (PAR_CLOSE 6 7 ")"))))))""")

#def test_rule__expr_group__expr_space_expr () :
#    """
#    Tests
#        EXPR_GROUP -> EXPR SPACE EXPR
#        PAR_GROUP -> PAR_OPEN EXPR_GROUP PAR_CLOSE
#    """
#    basictest("TEST RULE  EXPR_GROUP -> EXPR SPACE EXPR - ", "(\\\"abc\\\" \\\"xyz\\\")", """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR_GROUP ((EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (SPACE 6 7 " ") (EXPR ((QUOTE 7 8 "\\\"") (QVALUE 8 11 xyz) (QUOTE 11 12 "\\\""))))) (PAR_CLOSE 12 13 ")"))))))""")

#def test_rule__expr_group__expr_group_space_expr () :
#    """
#    Tests
#        EXPR_GROUP -> EXPR_GROUP SPACE EXPR
#        PAR_GROUP -> PAR_OPEN EXPR_GROUP PAR_CLOSE
#    """
#    basictest(
#            "TEST RULE  EXPR_GROUP -> EXPR_GROUP SPACE EXPR - ",
#            "(\\\"abc\\\" \\\"jkl\\\" \\\"xyz\\\")",
#            """((EXPR ((PAR_GROUP ((PAR_OPEN 0 1 "(") (EXPR_GROUP ((EXPR_GROUP ((EXPR ((QUOTE 1 2 "\\\"") (QVALUE 2 5 abc) (QUOTE 5 6 "\\\""))) (SPACE 6 7 " ") (EXPR ((QUOTE 7 8 "\\\"") (QVALUE 8 11 jkl) (QUOTE 11 12 "\\\""))))) (SPACE 12 13 " ") (EXPR ((QUOTE 13 14 "\\\"") (QVALUE 14 17 xyz) (QUOTE 17 18 "\\\""))))) (PAR_CLOSE 18 19 ")"))))))"""
#    )

def test_struct_0 () :
    basictest("TEST STRUCT 0 - ", """struct MyStruct\n\tui8 i\n""", """((EXPR ((STRUCT_DECL ((STRUCT 0 6 struct) (SPACE 6 7 " ") (NAME 7 15 MyStruct) (STRUCT_BLOCK ((BLOCK_START 0) (NAMEPAIR ((NAME 17 20 ui8) (SPACE 20 21 " ") (NAME 21 22 i))) (BLOCK_END 0 expr_end))))))))""")

def test_struct_1 () :
    basictest(
            "TEST STRUCT 1 - ",
            """struct MyStruct\n\tui8 i\n\tui8 y\n""",
            """((EXPR ((STRUCT_DECL ((STRUCT 0 6 struct) (SPACE 6 7 " ") (NAME 7 15 MyStruct) (STRUCT_BLOCK ((BLOCK_START 0) (STRUCT_DEF_GROUP ((NAMEPAIR ((NAME 17 20 ui8) (SPACE 20 21 " ") (NAME 21 22 i))) (NAMEPAIR ((NAME 24 27 ui8) (SPACE 27 28 " ") (NAME 28 29 y))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_res_struct () :
    basictest(
            "TEST RES STRUCT - ",
            """res struct MyStruct\n\tui8 i\n\tui8 y\n""",
            """((EXPR ((RES_STRUCT_DECL ((RES 0 3 res) (SPACE 3 4 " ") (STRUCT 4 10 struct) (SPACE 10 11 " ") (NAME 11 19 MyStruct) (STRUCT_BLOCK ((BLOCK_START 0) (STRUCT_DEF_GROUP ((NAMEPAIR ((NAME 21 24 ui8) (SPACE 24 25 " ") (NAME 25 26 i))) (NAMEPAIR ((NAME 28 31 ui8) (SPACE 31 32 " ") (NAME 32 33 y))))) (BLOCK_END 0 expr_end))))))))"""
    )




def test_fn_decl_0 () :
    basictest(
            "TEST FN_DECL 0 - ",
            """fn main  ui8 x  ui8\n
\tnop\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 22 25 nop))) (BLOCK_END 0 expr_end))))))))""",
    )

def test_fn_decl_1 () :
    basictest(
            "TEST FN_DECL 1 - ",
            """fn main  ui8 x ui8 y  ui8\n
\tnop\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR_GROUP ((NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (NAMEPAIR ((NAME 15 18 ui8) (SPACE 18 19 " ") (NAME 19 20 y))))) (SPACE 20 21 " ") (SPACE 21 22 " ") (NAME 22 25 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 28 31 nop))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_fn_decl_2 () :
    basictest(
            "TEST FN_DECL 2 - ",
            """fn main  ui8 x  ui8\n
\tnop\n
\tnop\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR_GROUP ((EXPR ((NOP 22 25 nop))) (EXPR ((NOP 28 31 nop))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_call () :
    basictest(
        "TEST CALL - ",
        """fn main  ui8 x  ui8\n
\tcall somefn\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((CALL_DECL ((CALL 22 26 call) (SPACE 26 27 " ") (NAME 27 33 somefn))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_ret () :
    basictest(
        "TEST RET - ",
        """fn main  ui8 x  ui8\n
\tret true\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((RET_DECL ((RET 22 25 ret) (SPACE 25 26 " ") (NAME 26 30 true))))) (BLOCK_END 0 expr_end))))))))"""
    )


def test_multiblock () :
    basictest(
            "TEST MULTIBLOCK - ",
            """fn main  ui8 x  ui8\n
\tnop\n
\tif true\n
\t\tif true\n
\t\t\tnop\n
\tnop\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR_GROUP ((EXPR_GROUP ((EXPR ((NOP 22 25 nop))) (EXPR ((IF_DECL ((IF 28 30 if) (SPACE 30 31 " ") (NAME 31 35 true) (BLOCK ((BLOCK_START 1) (EXPR ((IF_DECL ((IF 39 41 if) (SPACE 41 42 " ") (NAME 42 46 true) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 51 54 nop))) (BLOCK_END 2 return))))))) (BLOCK_END 1 return))))))))) (EXPR ((NOP 57 60 nop))))) (BLOCK_END 0 expr_end))))))))"""
            )


def test_set () :
    basictest(
            "TEST SET - ",
            """fn main  ui8 x  ui8\n
\tset x ui8 1\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((SET_DECL ((SET 22 25 set) (SPACE 25 26 " ") (NAMEPAIR ((NAME 26 27 x) (SPACE 27 28 " ") (NAME 28 31 ui8))) (SPACE 31 32 " ") (EXPR ((INT 32 33 1))))))) (BLOCK_END 0 expr_end))))))))""")


def test_mut () :
    basictest(
            "TEST MUT - ",
            """fn main  ui8 x  ui8\n
\tmut x ui8 1\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((MUT_DECL ((MUT 22 25 mut) (SPACE 25 26 " ") (NAMEPAIR ((NAME 26 27 x) (SPACE 27 28 " ") (NAME 28 31 ui8))) (SPACE 31 32 " ") (EXPR ((INT 32 33 1))))))) (BLOCK_END 0 expr_end))))))))""")




def test_if () :
    basictest(
            "TEST IF - ",
            """fn main  ui8 x  ui8\n
\tif true\n
\t\tnop\n""",
            """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_DECL ((IF 22 24 if) (SPACE 24 25 " ") (NAME 25 29 true) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 33 36 nop))) (BLOCK_END 1 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_if_else () :
    basictest(
        "TEST IF ELSE - ",
        """fn main  ui8 x  ui8\n
\tif true\n
\t\tnop\n
\telse\n
\t\tnop\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELSE_DECL ((IF 22 24 if) (SPACE 24 25 " ") (NAME 25 29 true) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 33 36 nop))) (BLOCK_END 1 return))) (ELSE 39 43 else) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 47 50 nop))) (BLOCK_END 2 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_if_elif () :
    basictest(
        "TEST IF ELIF - ",
        """fn main  ui8 x  ui8\n
\tif test0\n
\t\tnop\n
\telif test1\n
\t\tnop\n""",
"""((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_DECL ((IF 22 24 if) (SPACE 24 25 " ") (NAME 25 30 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 34 37 nop))) (BLOCK_END 1 return))) (ELIF_DECL ((ELIF 40 44 elif) (SPACE 44 45 " ") (NAME 45 50 test1) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 54 57 nop))) (BLOCK_END 2 expr_end))))))))) (BLOCK_END 0 expr_end))))))))"""
#        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_DECL ((IF 22 24 if) (SPACE 24 25 " ") (NAME 25 30 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 34 37 nop))) (BLOCK_END 1 return))) (ELIF 40 44 elif) (SPACE 44 45 " ") (NAME 45 50 test1) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 54 57 nop))) (BLOCK_END 2 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_if_elif_elif_elif () :
    basictest(
        "TEST IF ELIF ELIF ELIF - ",
        """fn main  ui8 x  ui8
\tif test0
\t\tnop
\telif test1
\t\tnop
\telif test2
\t\tnop
\telif test3
\t\tnop\n""",
    """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_GROUP_DECL ((IF 21 23 if) (SPACE 23 24 " ") (NAME 24 29 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 32 35 nop))) (BLOCK_END 1 return))) (ELIF_GROUP ((ELIF_GROUP ((ELIF_DECL ((ELIF 37 41 elif) (SPACE 41 42 " ") (NAME 42 47 test1) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 50 53 nop))) (BLOCK_END 2 return))))) (ELIF_DECL ((ELIF 55 59 elif) (SPACE 59 60 " ") (NAME 60 65 test2) (BLOCK ((BLOCK_START 3) (EXPR ((NOP 68 71 nop))) (BLOCK_END 3 return))))))) (ELIF_DECL ((ELIF 73 77 elif) (SPACE 77 78 " ") (NAME 78 83 test3) (BLOCK ((BLOCK_START 4) (EXPR ((NOP 86 89 nop))) (BLOCK_END 4 expr_end))))))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_if_elif_else () :
    basictest(
        "TEST IF ELIF ELSE - ",
        """fn main  ui8 x  ui8
\tif test0
\t\tnop
\telif test1
\t\tnop
\t\tnop
\telse
\t\tnop\n""",
    """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_ELSE_DECL ((IF 21 23 if) (SPACE 23 24 " ") (NAME 24 29 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 32 35 nop))) (BLOCK_END 1 return))) (ELIF_DECL ((ELIF 37 41 elif) (SPACE 41 42 " ") (NAME 42 47 test1) (BLOCK ((BLOCK_START 2) (EXPR_GROUP ((EXPR ((NOP 50 53 nop))) (EXPR ((NOP 56 59 nop))))) (BLOCK_END 2 return))))) (ELSE 61 65 else) (BLOCK ((BLOCK_START 3) (EXPR ((NOP 68 71 nop))) (BLOCK_END 3 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_if_elif_elif_elif_else () :
    basictest(
        "TEST IF ELIF ELIF ELIF ELSE - ",
        """fn main  ui8 x  ui8
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
    """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((IF_ELIF_GROUP_ELSE_DECL ((IF 21 23 if) (SPACE 23 24 " ") (NAME 24 29 test0) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 32 35 nop))) (BLOCK_END 1 return))) (ELIF_GROUP ((ELIF_GROUP ((ELIF_DECL ((ELIF 37 41 elif) (SPACE 41 42 " ") (NAME 42 47 test1) (BLOCK ((BLOCK_START 2) (EXPR ((NOP 50 53 nop))) (BLOCK_END 2 return))))) (ELIF_DECL ((ELIF 55 59 elif) (SPACE 59 60 " ") (NAME 60 65 test2) (BLOCK ((BLOCK_START 3) (EXPR ((NOP 68 71 nop))) (BLOCK_END 3 return))))))) (ELIF_DECL ((ELIF 73 77 elif) (SPACE 77 78 " ") (NAME 78 83 test3) (BLOCK ((BLOCK_START 4) (EXPR ((NOP 86 89 nop))) (BLOCK_END 4 return))))))) (ELSE 91 95 else) (BLOCK ((BLOCK_START 5) (EXPR ((NOP 98 101 nop))) (BLOCK_END 5 expr_end))))))) (BLOCK_END 0 expr_end))))))))""")



def test_while () :
    basictest(
        "TEST WHILE - ",
        """fn main  ui8 x  ui8\n
\twhile true\n
\t\tnop\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((WHILE_DECL ((WHILE 22 27 while) (SPACE 27 28 " ") (NAME 28 32 true) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 36 39 nop))) (BLOCK_END 1 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_for () :
    basictest(
        "TEST FOR - ",
        """fn main  ui8 x  ui8\n
\tfor i  array\n
\t\tnop\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((FOR_DECL ((FOR 22 25 for) (SPACE 25 26 " ") (NAME 26 27 i) (SPACE 27 28 " ") (SPACE 28 29 " ") (NAME 29 34 array) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 38 41 nop))) (BLOCK_END 1 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_for_2 () :
    basictest(
        "TEST FOR 2 - ",
        """fn main  ui8 x  ui8\n
\tfor i item  array\n
\t\tnop\n""",
        """((EXPR ((FN_DECL ((FN 0 2 fn) (SPACE 2 3 " ") (NAME 3 7 main) (SPACE 7 8 " ") (SPACE 8 9 " ") (NAMEPAIR ((NAME 9 12 ui8) (SPACE 12 13 " ") (NAME 13 14 x))) (SPACE 14 15 " ") (SPACE 15 16 " ") (NAME 16 19 ui8) (BLOCK ((BLOCK_START 0) (EXPR ((FOR_DECL ((FOR 22 25 for) (SPACE 25 26 " ") (NAMEPAIR ((NAME 26 27 i) (SPACE 27 28 " ") (NAME 28 32 item))) (SPACE 32 33 " ") (SPACE 33 34 " ") (NAME 34 39 array) (BLOCK ((BLOCK_START 1) (EXPR ((NOP 43 46 nop))) (BLOCK_END 1 expr_end))))))) (BLOCK_END 0 expr_end))))))))"""
    )


def test_incl_pkg () :
    basictest(
            "TEST INCL somepkg - ",
            """incl somepkg""",
            """((EXPR ((INCL_DECL ((INCL 0 4 incl) (SPACE 4 5 " ") (NAME 5 12 somepkg))))))"""
    )

def test_incl_path () :
    basictest(
            "TEST INCL \"path\" - ",
            "incl \\\"path\\\"",
            """((EXPR ((INCL_DECL ((INCL 0 4 incl) (SPACE 4 5 " ") (EXPR ((QUOTE 5 6 "\\\"") (QVALUE 6 10 path) (QUOTE 10 11 "\\\""))))))))"""
    )

def test_incl_pkg () :
    basictest(
            "TEST PKG somepkg - ",
            """pkg somepkg
\tnop\n""",
        """((EXPR ((PKG_DECL ((PKG 0 3 pkg) (SPACE 3 4 " ") (NAME 4 11 somepkg) (BLOCK ((BLOCK_START 0) (EXPR ((NOP 13 16 nop))) (BLOCK_END 0 expr_end))))))))"""
    )

def test_invalid_syntax () :
    print("TEST INVALID SYNTAX - ", end="")

    stdout, stderr = _popen("())")

    expected = "Invalid syntax!"
    if not (expected in stderr):
        print(f"""FAIL - stderr not correct
                expected: {expected}
                got: {stderr}""")
        exit()

    print("OK")


def _popen (expr) :
    cmd = f"/usr/bin/python3 ../run.py --expr \"{expr}\" --print-parse-tree"
    sp = split(cmd)

    p = Popen(sp, stdout= PIPE, stderr= PIPE, encoding= "utf-8")
    return p.communicate()


if __name__ == "__main__":
    tests = [t for t in globals() if t[0:5] == "test_"]
    for t in tests:
        eval(f"{t}()")
