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
    ct._validate_set(node, scope)

    # back-end validation
    _validate_set(node, scope)

    names = scope[0]
    set_, mutdecl, name, data = node
    type_ = data[0]
    fn_content = data[1]

    # if node sets a function
    if type_ == "fn":
        # solve function overloaded name to a single function name
        uname = _unoverload(node, scope)

        # get argument types
        args = []

        # convert argument types
        fn_args = fn_content[0]
        for arg in fn_args:
            args.append(_cvt_type(arg[1]))

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
        body = f"""
start:
ret {return_type}
"""
        # result = eval.eval(fn_body, scope)
        # print(f"result: {result}")
        # if len(result) > 0:
        #    pass

        # declaration, definition = _write_fn(uname, args, return_type, body)
        return _write_fn(uname, args, return_type, body)

    return []


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


def _unoverload(node, scope):
    # print(f"_unoverload: {node}")

    # extract node, get function name
    set_, mutdecl, name, data = node
    type_ = data[0]
    fn_content = data[1]

    fn_args = fn_content[0]

    arg_types = []
    for arg in fn_args:
        # print(f"arg: {arg}")
        arg_types.append(arg[1])

    uname = "__".join([name] + arg_types)
    # print(f"uname: {uname}")

    return uname


def _cvt_type(type_):
    # print(f"_cvt_type: {type_}")

    # convert int
    if type_ == "int":
        cvtd_type = "i64"

    # conver uint
    elif type_ == "uint":
        cvtd_type = "ui64"

    return cvtd_type


def _write_fn(fn, args, return_type, body):
    # arg_types = [ arg[1] for arg in args ]
    # decl_args = ", ".join(arg_types)
    # declaration = f"declare {return_type} @{fn}({decl_args})"
    # print(f"declaration: {declaration}")

    def_args = ", ".join(args)
    definition = f"""define {return_type} @{fn}({def_args}) {{{body}}}"""
    # print(f"definition: {definition}")

    # return [declaration, definition]
    return definition


def __macro__(node, scope):
    return []


def __if__(node, scope):
    return []


def __data__(node, scope):
    return []


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

    ["f32", "const", "type", [4]],
    ["f64", "const", "type", [8]],
    ["float", "const", "type", [8]],

    ["byte", "const", "type", [1]],
    ["bool", "const", "type", [1]],

    ["struct", "mut", "type", ['?']],
    ["enum", "mut", "type", ['?']],

    ["ptr", "mut", "type", [8]],
  ],
  [],    # macros
  None,  # parent scope
  [],    # children scope
  True,  # is safe scope
  None   # forced handler
]
