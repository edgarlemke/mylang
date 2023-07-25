from . import compiletime


# def __fn__ (node, scope):
#  return []


def __handle__(node, scope):
    compiletime._validate_handle(node, scope)
    return []


# def __set__ (node, scope):
#  return []


# def __macro__ (node, scope):
#  return []


def __if__(node, scope):
    return []


# def __data__ (node, scope):
#  return []


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


scope = [
  [  # names
    ["fn", "mut", "internal", compiletime.__fn__],
    ["handle", "mut", "internal", compiletime.__handle__],
    ["set", "mut", "internal", compiletime.__set__],
    ["macro", "mut", "internal", compiletime.__macro__],
    ["if", "mut", "internal", compiletime.__if__],
    ["data", "mut", "internal", compiletime.__data__],
    ["meta", "mut", "internal", __meta__],
    ["write_ptr", "mut", "internal", __write_ptr__],
    ["read_ptr", "mut", "internal", __read_ptr__],
    ["get_ptr", "mut", "internal", __get_ptr__],
    ["size_of", "mut", "internal", __size_of__],
    ["unsafe", "mut", "internal", __unsafe__],
  ],
  [],    # macros
  None,  # parent scope
  [],    # children scope
  True,  # is safe scope
  None   # forced handler
]
