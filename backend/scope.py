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
    split_args = ct._split_function_arguments(args)
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
    DEBUG = False

    import eval

    if DEBUG:
        print(f"back-end __set__: {node}")

    # compile-time validation
    import frontend.compiletime as ct
    ct.__set__(node, scope, split_args=False)

    # if DEBUG:
    #    print(f"\nscope: {scope}\n\n")

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
        function_arguments = fn_content[0]
        # print(f"function_arguments: {function_arguments}")
        for arg in function_arguments:
            # print(f"arg: {arg}")
            args.append(f"{_converted_type(arg[1])} %{arg[0]}")

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
            return_type = _converted_type(fn_return_type)

        if DEBUG:
            print(f"return_type: {return_type}")

        # create function body scope
        function_body_scope = eval.default_scope.copy()

        # set scope child
        scope[3].append(function_body_scope)

        # set function body scope parent
        function_body_scope[2] = scope

        # set scope return calls
        function_body_scope[6] = scope[6]

        # set scope as backend scope
        function_body_scope[7] = True

        if DEBUG:
            print(f"function_body_scope: {function_body_scope}")

        # sort out body IR
        result = eval.eval(fn_body, function_body_scope)
        # print(f"result: {result}")
        # if len(result) == 0:
        body = ["start:"]
        # body = ["br label %start", "start:"]
        # else:

        if len(result) > 0:
            body.append(result)

        if DEBUG:
            print(f"body: {body}")

        serialized_body = _serialize_body(body)

        if DEBUG:
            print(f"serialized_body: {serialized_body}")

        if "ret" not in serialized_body[len(serialized_body) - 1]:
            serialized_body.append([f"ret {return_type}"])

        # declaration, definition = _write_fn(uname, args, return_type, body)
        retv = _write_fn(uname, args, return_type, serialized_body)

    else:
        if type_ == "Str":
            str_, size = _converted_str(data[1])

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
            t = _converted_type(type_)
            value = data[1]

            if isinstance(value, list):
                value, stack = return_call(value, scope)
                stack.append(f"%{name} = {value}")
                retv = "\n".join(stack)
                if DEBUG:
                    print(f"retv: {retv}")

            else:
                # check if it's at global backend scope
                if scope[2] is None:
                    retv = f"@{name} = global {t} {value}"

                # not global backend scope
                else:
                    # allocate space in stack and set value
                    retv = f"""%{name}_stack = alloca {t}
store {t} {value}, {t}* %{name}_stack
%{name} = load {t}, {t}* %{name}_stack
"""

        else:
            raise Exception(f"meh {type_}")

    return retv


def _converted_str(str_):
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
    # print(f"backend _validate_set - node: {node}")

    set_, mutdecl, name, data = node
    type_ = data[0]
    value = data[1]

    # get types and structs from scope and parent scopes
    all_types = []
    all_structs = []

    def iterup(scope, all_types, all_structs):
        # print(f"\n!! iterup - scope: {scope}\n")

        parent_scope = scope[2]
        children_scopes = scope[3]

        if parent_scope is not None:
            iterup(parent_scope, all_types, all_structs)

        types = [t[0] for t in scope[0] if t[2] == "type" and t[0] not in all_types]
        all_types += types
        # print(f"types: {types}")

        structs = [s[0] for s in scope[0] if s[2] == "struct" and s[0] not in all_structs]
        all_structs += structs
        # print(f"structs: {structs}")

    iterup(scope, all_types, all_structs)

    # validate type
    exceptions = ["fn"]
    valid_types = (all_types + all_structs + exceptions)
    if type_ not in valid_types:
        raise Exception(f"Constant assignment has invalid type - type_: {type_} - valid_types: {valid_types} - node: {node}")

    return


def _unoverload(name, function_arguments):
    # print(f"_unoverload: {node}")

    # extract node, get function name
    # set_, mutdecl, name, data = node
    # type_ = data[0]
    # fn_content = data[1]

    # function_arguments = fn_content[0]
    # print(f"function_arguments: {function_arguments}")

    arg_types = []
    for arg in function_arguments:
        # print(f"arg: {arg} -  {node}")
        arg_types.append(arg[1])

    unamel = [name]
    if len(arg_types) > 0:
        unamel += ["__", "_".join(arg_types)]
    uname = "".join(unamel)
    # print(f"uname: {uname}")

    return uname


def _converted_type(type_):
    # print(f"_converted_type: {type_}")

    # convert integers
    if type_ in ["int", "uint"]:
        convertedd_type = "i64"

    # convert booleans
    elif type_ == "bool":
        convertedd_type = "i1"

    # convert floats
    elif type_ == "float":
        convertedd_type = "float"

    # convert Str (strings)
    elif type_ == "Str":
        convertedd_type = "%struct.Str*"

    return convertedd_type


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
    fd[0] = _converted_type(fd[0])
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


def return_call(node, scope, stack=[]):
    DEBUG = False

    import eval

    if DEBUG:
        print(f"return_call():  {node}")

    # find out function name
    li_function_name = node[0]

    value = eval.get_name_value(li_function_name, scope)
    if DEBUG:
        print(f"return_call():  value: {value}")

    # matches = [name for name in scope[0] if name[0] == li_function_name]

    # if len(matches) == 0:
    #    raise Exception(f"No name matches for function: {li_function_name}")

    # value = matches[0]
    # print(f"value2: {value}")

    if value == False:
        raise Exception(f"No name matches for function: {li_function_name}")

    method, solved_arguments = eval.find_function_method(node, value, scope)
    if DEBUG:
        print(f"return_call():  method: {method}")

    function_arguments = method[0]
    if DEBUG:
        print(f"return_call():  function_arguments: {function_arguments}")

    function_name = _unoverload(li_function_name, function_arguments)
    if DEBUG:
        print(f"return_call():  function_name: {function_name}")

    # find out arguments
    converted_arguments = []
    for argument_index, argument in enumerate(function_arguments):
        if DEBUG:
            print(f"return_call():  argument: {argument}")

        name, type_ = argument
        converted_type = _converted_type(type_)

        # fulfill llvm requirement to convert float values types to doubles
        if converted_type == "float":
            converted_type = "double"

        argument_value = node[argument_index + 1]
        if DEBUG:
            print(f"return_call():  argument_value: {argument_value}")

        if isinstance(argument_value, list):
            scope_argument_value = eval.get_name_value(argument_value[0], scope)
            result, stack = return_call(argument_value, scope, stack)
            tmp = "tmp0"  # TODO: get a proper temporary name generator
            call_ = f"%{tmp} = {result}"
            stack.append(call_)
            argument_value = f"%{tmp}"

        else:
            scope_argument_value = eval.get_name_value(argument_value, scope)
            if DEBUG:
                print(f"return_call():  scope_argument_value: {scope_argument_value}")

            if scope_argument_value != []:
                argument_value = f"%{argument_value}"

        converted_argument = f"{converted_type} {argument_value}"

        if DEBUG:
            print(f"return_call():  converted_argument: {converted_argument}")

        converted_arguments.append(converted_argument)

    converted_function_arguments = ", ".join(converted_arguments)

    # find out return type
    if len(method) == 2:
        function_return_type = "void"

    elif len(method) == 3:
        function_return_type = _converted_type(method[1])

    value = f"call {function_return_type} @{function_name}({converted_function_arguments})"

    return value, stack


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
  return_call,   # eval return call handler
  True   # backend scope
]


def _setup_scope():
    from . import bool as bool_
    from . import uint as uint
    from . import int as int_
    from . import float as float_

    names = [

    ["and_bool_bool", "const", "internal", bool_.__and_bool_bool__],
    ["or_bool_bool", "const", "internal", bool_.__or_bool_bool__],
    ["xor_bool_bool", "const", "internal", bool_.__xor_bool_bool__],
    ["not_bool", "const", "internal", bool_.__not_bool__],
    ["eq_bool_bool", "const", "internal", bool_.__eq_bool_bool__],

    ["add_int_int", "const", "internal", int_.__add_int_int__],
    ["sub_int_int", "const", "internal", int_.__sub_int_int__],
    ["mul_int_int", "const", "internal", int_.__mul_int_int__],
    ["div_int_int", "const", "internal", int_.__div_int_int__],
    ["and_int_int", "const", "internal", int_.__and_int_int__],
    ["or_int_int", "const", "internal", int_.__or_int_int__],
    ["xor_int_int", "const", "internal", int_.__xor_int_int__],
    ["not_int", "const", "internal", int_.__not_int__],
    ["eq_int_int", "const", "internal", int_.__eq_int_int__],
    ["gt_int_int", "const", "internal", int_.__gt_int_int__],
    ["ge_int_int", "const", "internal", int_.__ge_int_int__],
    ["lt_int_int", "const", "internal", int_.__lt_int_int__],
    ["le_int_int", "const", "internal", int_.__le_int_int__],

    ["add_uint_uint", "const", "internal", uint.__add_uint_uint__],
    ["sub_uint_uint", "const", "internal", uint.__sub_uint_uint__],
    ["mul_uint_uint", "const", "internal", uint.__mul_uint_uint__],
    ["div_uint_uint", "const", "internal", uint.__div_uint_uint__],
    ["and_uint_uint", "const", "internal", uint.__and_uint_uint__],
    ["or_uint_uint", "const", "internal", uint.__or_uint_uint__],
    ["xor_uint_uint", "const", "internal", uint.__xor_uint_uint__],
    ["not_uint", "const", "internal", uint.__not_uint__],
    ["eq_uint_uint", "const", "internal", uint.__eq_uint_uint__],
    ["gt_uint_uint", "const", "internal", uint.__gt_uint_uint__],
    ["ge_uint_uint", "const", "internal", uint.__ge_uint_uint__],
    ["lt_uint_uint", "const", "internal", uint.__lt_uint_uint__],
    ["le_uint_uint", "const", "internal", uint.__le_uint_uint__],

    ["add_float_float", "const", "internal", float_.__add_float_float__],
    ["sub_float_float", "const", "internal", float_.__sub_float_float__],
    ["mul_float_float", "const", "internal", float_.__mul_float_float__],
    ["div_float_float", "const", "internal", float_.__div_float_float__],
    ["eq_float_float", "const", "internal", float_.__eq_float_float__],
    ["gt_float_float", "const", "internal", float_.__gt_float_float__],
    ["ge_float_float", "const", "internal", float_.__ge_float_float__],
    ["lt_float_float", "const", "internal", float_.__lt_float_float__],
    ["le_float_float", "const", "internal", float_.__le_float_float__],

    ]

    for name in names:
        scope[0].append(name)


_setup_scope()
