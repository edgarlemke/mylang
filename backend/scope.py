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

        # sort out body IR
        result = eval.eval(fn_body, scope)
        # print(f"result: {result}")
        # if len(result) == 0:
        body = ["start:"]
        # body = ["br label %start", "start:"]
        # else:

        if len(result) > 0:
            body.append(result)

        body.append([f"ret {return_type}"])

        # declaration, definition = _write_fn(uname, args, return_type, body)
        retv = _write_fn(uname, args, return_type, body)

    else:
        if type_ == "Str":
            str_, size = _convert_str(data[1])

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

# """
#
# %{name}_ptr = getelementptr [{size} x i8], i8* %{name}_str
#
# %{name}_addr_ptr = getelementptr %struct.Str, %struct.Str* %{name}
# %{name}_size = getelementptr %struct.Str, %struct.Str* %{name}, i64 1
#
#
# store i8* %{name}_ptr, i8* %{name}_addr_ptr
# store i64 2, i64* %{name}_size
# """
#            retv = f"""

# %{name} = alloca [{size} x i8], align 1
# store [{size} x i8] c"{str_}", [{size} x i8]* %{name}, align 1""".split("\n")

        elif type_ in ["int", "uint"]:
            t = _cvt_type(type_)
            retv = f"@{name} = constant {t} {data[1]}"
        else:
            raise Exception(f"meh {type_}")

    return retv


def _convert_str(str_):
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
        arg_types.append(arg[1][1])

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


def __write_file__(node, scope):
    # print(f"calling __write_file__: {node}")
    # print(f"SCOPE: {scope}")

    _validate_write_file(node, scope)

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

call void @write_file({fd_arg}, i8* %addr, i64 %size)
"""

    return template.split("\n")


def _validate_write_file(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for write_file: {node}")


def return_call(node, scope):
    import eval
    # print(f"!! return_call: {node} {scope}")

    # find out function name
    name = node[0]
    value = eval._get_name_value(name, scope)

    # print(f"value: {value}")

    fn_args = value[3][0][0][0]
    fn_name = _unoverload(name, fn_args)

    # find out args
    # print(f"fn_args: {fn_args}")
    cvt_args = []
    for arg_i, arg in enumerate(fn_args):
        name, type_ = arg
        cvt_type = _cvt_type(type_)
        arg_value = node[arg_i + 1]
        cvt_args.append(f"{cvt_type} %{arg_value}")

    cvt_fn_args = ", ".join(cvt_args)

    # find out return type
    fn_ret_type = "void"

    return f"call {fn_ret_type} @{fn_name}({cvt_fn_args})"


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

    ["write_file", "const", "internal", __write_file__],

    ["i8", "const", "type", [1]],
    ["i16", "const", "type", [2]],
    ["i32", "const", "type", [4]],
    ["i64", "const", "type", [8]],
    ["int", "const", "type", [8]],

    ["ui8", "const", "type", [1]],
    ["ui16", "const", "type", [2]],
    ["ui32", "const", "type", [4]],
    ["ui64", "const", "type", [8]],
    ["uint", "const", "type", [8]],

    ["ptr", "const", "type", [8]],

    ["byte", "const", "type", [1]],
    ["bool", "const", "type", [1]],

    ["f32", "const", "type", [4]],
    ["f64", "const", "type", [8]],
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
