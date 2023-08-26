from . import compiletime
import eval


def __fn__(node, scope):
    compiletime.validate_fn(node, scope)
    return node


def __handle__(node, scope):
    compiletime._validate_handle(node, scope)
    return node


def __set__(node, scope):
    DEBUG = False
    if DEBUG:
        print(f"calling runtime __set__")

    # compiletime._validate_set(node, scope)
    compiletime.__set__(node, scope)

    return node


def __macro__(node, scope):
    # print(f"__macro__ {node}")
    return compiletime.__macro__(node, scope)


def __if__(node, scope):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"__if__():  frontend runtime - node: {node}")

    compiletime.validate_if(node, scope)
    return node


def __else__(node, scope):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"__else__():  frontend runtime - node: {node}")

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
    compiletime._validate_unsafe(node, scope)
    return node[1]


scope = eval.default_scope.copy()
scope[0] = [  # names
     ["fn", "mut", "internal", __fn__],
    ["handle", "mut", "internal", __handle__],
    ["set", "mut", "internal", __set__],
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
