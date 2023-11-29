import copy

from . import compiletime
import eval
from shared import debug


def __fn__(node, scope):
    debug(f"__fn__():  frontend runtime - node: {node}")

    compiletime.__fn__(node, scope)
    # _validate_fn(node, scope)

    split_arguments = compiletime.split_function_arguments(node[2])
    debug(f"__fn__():  frontend runtime - split_arguments: {split_arguments}")

    node_copy = node.copy()
    node_copy[2] = split_arguments

    debug(f"__fn__():  frontend runtime - node_copy: {node_copy}")

    return node_copy


def _validate_fn(node, scope):

    if len(node) == 4:
        fn_, name, arguments, body = node

    elif len(node) == 5:
        fn_, name, arguments, return_type, body = node

    split_arguments = compiletime.split_function_arguments(arguments)

    # create body scope
    parent_scope = copy.deepcopy(scope)
    body_scope = copy.deepcopy(eval.default_scope)

    # set dummy arguments in the body scope
    body_scope["parent"] = parent_scope
    for argument in split_arguments:
        debug("__fn__():  frontend runtime - argument: {argument}")

        mutdecl = "const"
        if argument[0][0] == "mut":
            mutdecl = "mut"
            argument[0].remove(0)

        compiletime.__set__(["set", mutdecl, argument[0], [argument[1], '?']], body_scope)

    debug(f"__fn__():  frontend runtime - body_scope: {body_scope}")

    # evaluate body to check for errors
    # eval.eval(body, body_scope)


def __def__(node, scope):
    debug(f"__def__():  frontend runtime")
    compiletime.__def__(node, scope)
    return node


def __set__(node, scope):
    debug(f"__set__():  frontend runtime")
    compiletime.__set__(node, scope)
    return node


# ARRAY INTERNALS
#
def __set_array_member__(node, scope):
    debug(f"__set_array_member__():  frontend runtime")
    compiletime.__set_array_member__(node, scope)
    return node


def __get_array_member__(node, scope):
    debug(f"__get_array_member__():  frontend runtime")
    compiletime.__get_array_member__(node, scope)
    return node
#
#


# STRUCT INTERNALS
#
def __set_struct_member__(node, scope):
    debug(f"__set_struct_member__():  frontend runtime")
    compiletime.__set_struct_member__(node, scope)
    return node


def __get_struct_member__(node, scope):
    debug(f"__get_struct_member__():  frontend runtime")
    compiletime.__get_struct_member__(node, scope)
    return node
#
#


def __ref_member__(node, scope):
    compiletime.__ref_member__(node, scope)
    return node


def __macro__(node, scope):
    # print(f"__macro__ {node}")
    return compiletime.__macro__(node, scope)


def __if__(node, scope):
    debug(f"__if__():  frontend runtime - node: {node}")


def __macro__(node, scope):
    # print(f"__macro__ {node}")
    return compiletime.__macro__(node, scope)


def __if__(node, scope):
    debug(f"__if__():  frontend runtime - node: {node}")

    compiletime.validate_if(node, scope)
    return node


def __else__(node, scope):
    debug(f"__else__():  frontend runtime - node: {node}")

    compiletime.validate_else(node, scope)
    return node


def __data__(node, scope):
    return node


def __meta__(node, scope):
    #    print(f"calling __meta__: {node}")
    return eval(node[1:], compiletime.scope)


def __write_ptr__(node, scope):
    compiletime._validate_write_ptr(node, scope)
    return node


def __read_ptr__(node, scope):
    compiletime._validate_read_ptr(node, scope)
    return node


def __get_ptr__(node, scope):
    compiletime._validate_get_ptr(node, scope)
    return node


def __size_of__(node, scope):
    compiletime._validate_size_of(node, scope)
    return node


def __unsafe__(node, scope):
    compiletime.validate_unsafe(node, scope)
    return node[1]


scope = copy.deepcopy(eval.default_scope)
scope["names"] = [  # names
    ["fn", "mut", "internal", __fn__],
    ["def", "mut", "internal", __def__],
    ["set", "mut", "internal", __set__],
    ["set_array_member", "mut", "internal", __set_array_member__],
    ["get_array_member", "mut", "internal", __get_array_member__],
    ["set_struct_member", "mut", "internal", __set_struct_member__],
    ["get_struct_member", "mut", "internal", __get_struct_member__],
    ["ref_member", "mut", "internal", __ref_member__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["else", "mut", "internal", __else__],
    ["data", "mut", "internal", __data__],
    ["meta", "mut", "internal", __meta__],
    ["write_ptr", "mut", "internal", __write_ptr__],
    ["read_ptr", "mut", "internal", __read_ptr__],
    ["get_ptr", "mut", "internal", __get_ptr__],
    ["size_of", "mut", "internal", __size_of__],
    ["unsafe", "mut", "internal", __unsafe__],
  ]
scope["step"] = "frontend"
