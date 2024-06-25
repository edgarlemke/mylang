def __add_float_float__(node, scope):
    # prfloat(f"__add_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fadd float {x}, {y}
ret float %result"""


def __sub_float_float__(node, scope):
    # prfloat(f"__sub_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fsub float {x}, {y}
ret float %result"""


def __mul_float_float__(node, scope):
    # prfloat(f"__mul_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fmul float {x}, {y}
ret float %result"""


def __div_float_float__(node, scope):
    # prfloat(f"__div_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fdiv float {x}, {y}
ret float %result"""


def __eq_float_float__(node, scope):
    # prfloat(f"__eq_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fcmp oeq float {x}, {y}
ret i1 %result"""


def __gt_float_float__(node, scope):
    # prfloat(f"__gt_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fcmp ogt float {x}, {y}
ret i1 %result"""


def __ge_float_float__(node, scope):
    # prfloat(f"__ge_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fcmp oge float {x}, {y}
ret i1 %result"""


def __lt_float_float__(node, scope):
    # prfloat(f"__lt_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fcmp olt float {x}, {y}
ret i1 %result"""


def __le_float_float__(node, scope):
    # prfloat(f"__le_float_float__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = fcmp ole float {x}, {y}
ret i1 %result"""
