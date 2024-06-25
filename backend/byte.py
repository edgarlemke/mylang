def __add_byte_byte__(node, scope):
    # print(f"__add_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = add i8 {x}, {y}
ret i8 %result"""


def __sub_byte_byte__(node, scope):
    # print(f"__sub_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = sub i8 {x}, {y}
ret i8 %result"""


def __mul_byte_byte__(node, scope):
    # print(f"__mul_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = mul i8 {x}, {y}
ret i8 %result"""


def __div_byte_byte__(node, scope):
    # print(f"__div_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""
%x_float = sitofp i8 {x} to float
%y_float = sitofp i8 {y} to float

%result = fdiv float %x_float, %y_float

ret float %result"""


def __and_byte_byte__(node, scope):
    # print(f"__and_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = and i8 {x}, {y}
ret i8 %result"""


def __or_byte_byte__(node, scope):
    # print(f"__or_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = or i8 {x}, {y}
ret i8 %result"""


def __xor_byte_byte__(node, scope):
    # print(f"__xor_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = xor i8 {x}, {y}
ret i8 %result"""


def __not_int__(node, scope):
    # print(f"__not_byte_byte__ {node}")

    x = f"%{node[1]}"

    return f"""%result = xor i8 {x}, -1
ret i8 %result"""


def __eq_byte_byte__(node, scope):
    # print(f"__eq_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp eq i8 {x}, {y}
ret i1 %result"""


def __gt_byte_byte__(node, scope):
    # print(f"__gt_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp sgt i8 {x}, {y}
ret i1 %result"""


def __ge_byte_byte__(node, scope):
    # print(f"__ge_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp sge i8 {x}, {y}
ret i1 %result"""


def __lt_byte_byte__(node, scope):
    # print(f"__lt_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp slt i8 {x}, {y}
ret i1 %result"""


def __le_byte_byte__(node, scope):
    # print(f"__le_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp sle i8 {x}, {y}
ret i1 %result"""


def __shl_byte_byte__(node, scope):
    # print(f"__shl_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = shl i8 {x}, {y}
ret i8 %result"""


def __shr_byte_byte__(node, scope):
    # print(f"__shr_byte_byte__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = lshr i8 {x}, {y}
ret i8 %result"""
