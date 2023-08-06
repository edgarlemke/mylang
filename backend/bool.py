def __and_bool_bool__(node, scope):
    # prbool(f"__and_bool_bool__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = and i1 {x}, {y}
ret i1 %result"""


def __or_bool_bool__(node, scope):
    # prbool(f"__or_bool_bool__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = or i1 {x}, {y}
ret i1 %result"""


def __xor_bool_bool__(node, scope):
    # prbool(f"__xor_bool_bool__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = xor i1 {x}, {y}
ret i1 %result"""


def __not_bool__(node, scope):
    # prbool(f"__not_bool_bool__ {node}")

    x = f"%{node[1]}"

    return f"""%result = xor i1 {x}, -1
ret i1 %result"""


def __eq_bool_bool__(node, scope):
    # prbool(f"__eq_bool_bool__ {node}")

    x = f"%{node[1]}"
    y = f"%{node[2]}"

    return f"""%result = icmp eq i1 {x}, {y}
ret i1 %result"""
