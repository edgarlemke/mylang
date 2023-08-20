def __add_int_int__(node, scope):
    # print(f"__add_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = add i64 {x}, {y}
ret i64 %result"""


def __sub_int_int__(node, scope):
    # print(f"__sub_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = sub i64 {x}, {y}
ret i64 %result"""


def __mul_int_int__(node, scope):
    # print(f"__mul_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = mul i64 {x}, {y}
ret i64 %result"""


def __div_int_int__(node, scope):
    # print(f"__div_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""
%x_float = sitofp i64 {x} to float
%y_float = sitofp i64 {y} to float

%result = fdiv float %x_float, %y_float

ret float %result"""


def __and_int_int__(node, scope):
    # print(f"__and_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = and i64 {x}, {y}
ret i64 %result"""


def __or_int_int__(node, scope):
    # print(f"__or_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = or i64 {x}, {y}
ret i64 %result"""


def __xor_int_int__(node, scope):
    # print(f"__xor_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = xor i64 {x}, {y}
ret i64 %result"""


def __not_int__(node, scope):
    # print(f"__not_int_int__ {node}")

    x = f"%{node[1]}"

    return f"""%result = xor i64 {x}, -1
ret i64 %result"""


def __eq_int_int__(node, scope):
    # print(f"__eq_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp eq i64 {x}, {y}
ret i1 %result"""


def __gt_int_int__(node, scope):
    # print(f"__gt_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp sgt i64 {x}, {y}
ret i1 %result"""


def __ge_int_int__(node, scope):
    # print(f"__ge_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp sge i64 {x}, {y}
ret i1 %result"""


def __lt_int_int__(node, scope):
    # print(f"__lt_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp slt i64 {x}, {y}
ret i1 %result"""


def __le_int_int__(node, scope):
    # print(f"__le_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp sle i64 {x}, {y}
ret i1 %result"""


def __shl_int_int__(node, scope):
    # print(f"__shl_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = shl i64 {x}, {y}
ret i64 %result"""


def __shr_int_int__(node, scope):
    # print(f"__shr_int_int__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = lshr i64 {x}, {y}
ret i64 %result"""
