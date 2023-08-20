def __add_uint_uint__(node, scope):
    # pruint(f"__add_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = add i64 {x}, {y}
ret i64 %result"""


def __sub_uint_uint__(node, scope):
    # pruint(f"__sub_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = sub i64 {x}, {y}
ret i64 %result"""


def __mul_uint_uint__(node, scope):
    # pruint(f"__mul_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = mul i64 {x}, {y}
ret i64 %result"""


def __div_uint_uint__(node, scope):
    # pruint(f"__div_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""
%x_float = sitofp i64 {x} to float
%y_float = sitofp i64 {y} to float

%result = fdiv float %x_float, %y_float

ret float %result"""


def __and_uint_uint__(node, scope):
    # pruint(f"__and_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = and i64 {x}, {y}
ret i64 %result"""


def __or_uint_uint__(node, scope):
    # pruint(f"__or_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = or i64 {x}, {y}
ret i64 %result"""


def __xor_uint_uint__(node, scope):
    # pruint(f"__xor_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = xor i64 {x}, {y}
ret i64 %result"""


def __not_uint__(node, scope):
    # pruint(f"__not_uint_uint__ {node}")

    x = f"%{node[1]}"

    return f"""%result = xor i64 {x}, -1
ret i64 %result"""


def __eq_uint_uint__(node, scope):
    # pruint(f"__eq_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp eq i64 {x}, {y}
ret i1 %result"""


def __gt_uint_uint__(node, scope):
    # pruint(f"__gt_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp ugt i64 {x}, {y}
ret i1 %result"""


def __ge_uint_uint__(node, scope):
    # pruint(f"__ge_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp uge i64 {x}, {y}
ret i1 %result"""


def __lt_uint_uint__(node, scope):
    # pruint(f"__lt_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp ult i64 {x}, {y}
ret i1 %result"""


def __le_uint_uint__(node, scope):
    # pruint(f"__le_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp ule i64 {x}, {y}
ret i1 %result"""


def __shl_uint_int__(node, scope):
    # pruint(f"__shl_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = shl i64 {x}, {y}
ret i64 %result"""


def __shr_uint_int__(node, scope):
    # pruint(f"__shr_uint_uint__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = lshr i64 {x}, {y}
ret i64 %result"""
