def ui(value, size, T):
    # check if it's an unsigned integer number
    int_value = 0
    is_int = False
    try:
        int_value = int(value)
        is_int = True
    except BaseException:
        is_int = False

    is_list = isinstance(value, list)

    if not is_int and not is_list:
        raise Exception(f"Value attributed to {T} isn't a valid unsigned integer value: {value}")

    # check if it's in valid range
    min_ = 0
    max_ = pow(2, size)
    if not (int_value >= min_ and int_value <= max_):
        raise Exception(f"Value attributed to type {T} isn't in valid range: {value}i\nMinimum: {min_}  Maximum: {max_}")

    return value


def ui8(value):
    # print(f"ui8 {value}")
    return ui(value, 8, "ui8")


types = [
  ["ui8", ui8]
]
