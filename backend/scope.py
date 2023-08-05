import argparse
import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)


def __fn__(node, scope):
    # print(f"back-end __fn__: {node}")

    # compile-time validation
    import frontend.compiletime as ct
    ct.validate_fn(node, scope)

    # back-end validation
    _validate_fn(node, scope)
    return []


def _validate_fn(node, scope):
    import frontend.compiletime as ct

    fn, args, ret_type, body = node
    types = [t[0] for t in scope[0] if t[2] == "type"]

    # check if types of the arguments are valid
    split_args = ct._split_fn_args(args)
    for arg in split_args:
        # type_, name = arg
        name, type_ = arg
        if type_ not in types:
            raise Exception(f"Function argument has invalid type: {arg} {node}")

    # check if the return type is valid
    if ret_type not in types:
        raise Exception(f"Function return type has invalid type: {ret_type} {node}")


def __handle__(node, scope):
    return []


def __set__(node, scope):
    import eval
    # print(f"back-end __set__: {node}")

    # compile-time validation
    import frontend.compiletime as ct
    # ct._validate_set(node, scope)
    ct.__set__(node, scope, split_args=False)

    # print(f"\nscope: {scope}\n\n")

    # back-end validation
    _validate_set(node, scope)

    names = scope[0]
    set_, mutdecl, name, data = node
    type_ = data[0]
    fn_content = data[1]

    # if node sets a function
    if type_ == "fn":
        # solve function overloaded name to a single function name
        uname = _unoverload(name, fn_content[0])

        # get argument types
        args = []

        # convert argument types
        fn_args = fn_content[0]
        # print(f"fn_args: {fn_args}")
        for arg in fn_args:
            # print(f"arg: {arg}")
            args.append(f"{_cvt_type(arg[1])} %{arg[0]}")

        # get return type and body
        if len(fn_content) == 2:
            fn_return_type = None
            fn_body = fn_content[1]

        elif len(fn_content) == 3:
            fn_return_type = fn_content[1]
            fn_body = fn_content[2]

        # convert return type
        return_type = "void"
        if fn_return_type is not None:
            return_type = _cvt_type(fn_return_type)
        # print(f"return_type: {return_type}")

        # sort out body IR
        result = eval.eval(fn_body, scope)
        # print(f"result: {result}")
        # if len(result) == 0:
        body = ["start:"]
        # body = ["br label %start", "start:"]
        # else:

        if len(result) > 0:
            body.append(result)

        # print(f"body: {body}")
        serialized_body = _serialize_body(body)
        # print(f"serialized_body: {serialized_body}")

        if "ret" not in serialized_body[len(serialized_body) - 1]:
            serialized_body.append([f"ret {return_type}"])

        # declaration, definition = _write_fn(uname, args, return_type, body)
        retv = _write_fn(uname, args, return_type, serialized_body)

    else:
        if type_ == "Str":
            str_, size = _cvt_str(data[1])

            retv = f"""
%{name} = alloca %struct.Str, align 8

%{name}_str = alloca [{size} x i8]
store [{size} x i8] c"{str_}", i8* %{name}_str

%{name}_str_ptr = getelementptr [{size} x i8], [{size} x i8]* %{name}_str, i64 0, i64 0

%{name}_addr_ptr = getelementptr %struct.Str, %struct.Str* %{name}, i32 0, i32 0
store i8* %{name}_str_ptr, i8* %{name}_addr_ptr, align 8

%{name}_size_ptr = getelementptr %struct.Str, %struct.Str* %{name}, i32 0, i32 1
store i64 {size}, i64* %{name}_size_ptr, align 8
""".split("\n")

        elif type_ in ["int", "uint", "float", "bool"]:
            t = _cvt_type(type_)
            value = data[1]

            if isinstance(value, list):
                value = return_call(value, scope)
                retv = f"%{name} = {value}"
                # print(f"retv: {retv}")

            else:
                retv = f"@{name} = constant {t} {value}"

        else:
            raise Exception(f"meh {type_}")

    return retv


def _cvt_str(str_):
    encoded = str_.encode('utf-8')

    buf = []
    size = 0
    for ch in encoded:
        size += 1

        if ch < 128:
            buf.append(chr(ch))

        else:
            buf.append(f"\\{format(ch, 'x')}")

    result = "".join(buf)

    return (result, size)


def _validate_set(node, scope):

    set_, mutdecl, name, data = node
    type_ = data[0]
    value = data[1]

    # check type
    types = [t[0] for t in scope[0] if t[2] == "type"]
    structs = [s[0] for s in scope[0] if s[2] == "struct"]
    exceptions = ["fn"]

    valid_types = (types + structs + exceptions)
    # print(f"valid_types: {valid_types}")
    if type_ not in valid_types:
        raise Exception(f"Constant assignment has invalid type {type_} {node}")

    return


def _unoverload(name, fn_args):
    # print(f"_unoverload: {node}")

    # extract node, get function name
    # set_, mutdecl, name, data = node
    # type_ = data[0]
    # fn_content = data[1]

    # fn_args = fn_content[0]
    # print(f"fn_args: {fn_args}")

    arg_types = []
    for arg in fn_args:
        # print(f"arg: {arg} -  {node}")
        arg_types.append(arg[1])

    unamel = [name]
    if len(arg_types) > 0:
        unamel += ["__", "_".join(arg_types)]
    uname = "".join(unamel)
    # print(f"uname: {uname}")

    return uname


def _cvt_type(type_):
    # print(f"_cvt_type: {type_}")

    # convert integers
    if type_ in ["int", "uint"]:
        cvtd_type = "i64"

    # convert booleans
    elif type_ == "bool":
        cvtd_type = "i1"

    # convert floats
    elif type_ == "float":
        cvtd_type = "float"

    # convert Str (strings)
    elif type_ == "Str":
        cvtd_type = "%struct.Str*"

    return cvtd_type


def _write_fn(fn, args, return_type, body):
    # arg_types = [ arg[1] for arg in args ]
    # decl_args = ", ".join(arg_types)
    # declaration = f"declare {return_type} @{fn}({decl_args})"
    # print(f"declaration: {declaration}")

    def_args = ", ".join(args)
    definition = [f"define {return_type} @{fn}({def_args}) {{", body, "}"]
    # print(f"definition: {definition}")

    # return [declaration, definition]
    return definition


def _serialize_body(body):
    serialized = []

    def iter(li):
        for child in li:
            if isinstance(child, list):
                iter(child)
            else:
                serialized.append(child)

    iter(body)

    return serialized


def __macro__(node, scope):
    return []


def __if__(node, scope):
    return []


def __data__(node, scope):
    return node[1:]


def __write_ptr__(node, scope):
    return []


def __read_ptr__(node, scope):
    return []


def __get_ptr__(node, scope):
    return []


def __size_of__(node, scope):
    return []


def __unsafe__(node, scope):
    return []


def __linux_write__(node, scope):
    # print(f"calling __linux_write__: {node}")
    # print(f"SCOPE: {scope}")

    _validate_linux_write(node, scope)

    # convert fd
    from eval import eval
    fd = eval([node[1]], scope)
    fd[0] = _cvt_type(fd[0])
    fd_arg = " ".join(fd)
    # print(f"fd: {fd}")

    # if type(node[2]) == list:
    #    print(f"node[2]: {node[2]}")
    # text = eval([ node[2] ], scope)
    text = node[2]
    # print(f"text: {text}")

    template = f"""
%str_addr_ptr = getelementptr %struct.Str, %struct.Str* %text, i32 0, i32 0
%str_size_ptr = getelementptr %struct.Str, %struct.Str* %text, i32 0, i32 1

%addr = load i8*, %struct.Str* %str_addr_ptr
%size = load i64, %struct.Str* %str_size_ptr

call void @linux_write({fd_arg}, i8* %addr, i64 %size)
"""

    return template.split("\n")


def _validate_linux_write(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for linux_write: {node}")


def return_call(node, scope):
    import eval
    # print(f"return_call: {node}")

    # find out function name
    li_fn_name = node[0]

    # value = eval._get_name_value(name, scope)
    # print(f"scope[0]: {scope[0]}")

    matches = [name for name in scope[0] if name[0] == li_fn_name]

    if len(matches) == 0:
        raise Exception(f"No name matches for function: {li_fn_name}")

    value = matches[0]
    # print(f"value: {value}")

    method, solved_args = eval.find_fn_method(node, value, scope)
    # print(f"method: {method}")

    fn_args = method[0]
    # print(f"fn_args: {fn_args}")

    fn_name = _unoverload(li_fn_name, fn_args)

    # find out args

    cvt_args = []
    for arg_i, arg in enumerate(fn_args):
        # print(f"arg: {arg}")
        name, type_ = arg
        cvt_type = _cvt_type(type_)

        # fulfill llvm requirement to convert float values types to doubles
        if cvt_type == "float":
            cvt_type = "double"

        arg_value = node[arg_i + 1]

        scope_arg_value = eval._get_name_value(arg_value, scope)
        if scope_arg_value != []:
            arg_value = f"%{arg_value}"

        cvt_arg = f"{cvt_type} {arg_value}"
        # print(f"cvt_arg: {cvt_arg}")
        cvt_args.append(cvt_arg)

    cvt_fn_args = ", ".join(cvt_args)

    # find out return type
    if len(method) == 2:
        fn_ret_type = "void"

    elif len(method) == 3:
        fn_ret_type = _cvt_type(method[1])

    return f"call {fn_ret_type} @{fn_name}({cvt_fn_args})"


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


scope = [
  [  # names
    ["fn", "mut", "internal", __fn__],
    ["handle", "mut", "internal", __handle__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["data", "mut", "internal", __data__],
    ["write_ptr", "mut", "internal", __write_ptr__],
    ["read_ptr", "mut", "internal", __read_ptr__],
    ["get_ptr", "mut", "internal", __get_ptr__],
    ["size_of", "mut", "internal", __size_of__],
    ["unsafe", "mut", "internal", __unsafe__],

    ["linux_write", "const", "internal", __linux_write__],

    ["add_int_int", "const", "internal", __add_int_int__],
    ["sub_int_int", "const", "internal", __sub_int_int__],
    ["mul_int_int", "const", "internal", __mul_int_int__],
    ["div_int_int", "const", "internal", __div_int_int__],
    ["and_int_int", "const", "internal", __and_int_int__],
    ["or_int_int", "const", "internal", __or_int_int__],
    ["xor_int_int", "const", "internal", __xor_int_int__],
    ["not_int", "const", "internal", __not_int__],
    ["eq_int_int", "const", "internal", __eq_int_int__],
    ["gt_int_int", "const", "internal", __gt_int_int__],
    ["ge_int_int", "const", "internal", __ge_int_int__],
    ["lt_int_int", "const", "internal", __lt_int_int__],
    ["le_int_int", "const", "internal", __le_int_int__],

    ["add_float_float", "const", "internal", __add_float_float__],
    ["sub_float_float", "const", "internal", __sub_float_float__],
    ["mul_float_float", "const", "internal", __mul_float_float__],
    ["div_float_float", "const", "internal", __div_float_float__],
    ["eq_float_float", "const", "internal", __eq_float_float__],
    ["gt_float_float", "const", "internal", __gt_float_float__],
    ["ge_float_float", "const", "internal", __ge_float_float__],
    ["lt_float_float", "const", "internal", __lt_float_float__],
    ["le_float_float", "const", "internal", __le_float_float__],

    ["int", "const", "type", [8]],

    ["uint", "const", "type", [8]],

    ["ptr", "const", "type", [8]],

    ["byte", "const", "type", [1]],
    ["bool", "const", "type", [1]],

    ["float", "const", "type", [8]],

    ["array", "const", "type", ['?']],
    ["struct", "const", "type", ['?']],
    ["enum", "const", "type", ['?']],

    ["Str", "const", "type", ['?']],
  ],
  [],    # macros
  None,  # parent scope
  [],    # children scope
  True,  # is safe scope
  None,  # forced handler
  return_call   # eval return call handler
]


def _setup_scope():
    from . import bool as bool_

    names = [

    ["and_bool_bool", "const", "internal", bool_.__and_bool_bool__],
    ["or_bool_bool", "const", "internal", bool_.__or_bool_bool__],
    ["xor_bool_bool", "const", "internal", bool_.__xor_bool_bool__],
    ["not_bool", "const", "internal", bool_.__not_bool__],
    ["eq_bool_bool", "const", "internal", bool_.__eq_bool_bool__],

    ]

    for name in names:
        scope[0].append(name)


_setup_scope()
