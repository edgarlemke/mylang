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
    # print(f"back-end __set__: {node}")

    # compile-time validation
    import frontend.compiletime as ct
    ct._validate_set(node, scope)

    # back-end validation
    _validate_set(node, scope)

    names = scope[0]
    set_, mutdecl, name, data = node
    type_ = data[0]

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

    ["int", "const", "type", [8]],
    ["uint", "const", "type", [8]],
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
