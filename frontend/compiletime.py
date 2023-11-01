import copy
import eval
from shared import debug


def __fn__(node, scope, split_args=True):
    debug(f"__fn__():  compiletime - node: {node}")

    validate_fn(node, scope)

    # check for functions without return value
    if len(node) == 4:
        fn_, name, arguments, body = node
        method = [arguments, body]

    # check for functions with return value
    elif len(node) == 5:
        fn_, name, arguments, return_type, body = node
        method = [arguments, return_type, body]

    # split arguments if needed
    if split_args:
        # value[0][0] = split_function_arguments(value[0][0])
        arguments = split_function_arguments(arguments)
        method[0] = arguments

    debug(f"value after split fn args: {arguments}")

    # get all functions with the function-to-be-set name
    names = scope["names"]
    all_fn = [(i, var) for i, var in enumerate(names) if var[2] == "fn" and var[0] == name]

    # if there's no function with the function-to-be-set name, create a new function value in scope
    if all_fn == []:
        debug(f"empty all_fn")

        names.append([name, "mut", "fn", [method]])

    # else, add a method to the existing function value
    else:
        match_fn = all_fn[0]
        i, var = match_fn

        names[i][3].append(method)

    debug(f"\n__fn__():  frontend compiletime - names after fn: {names}\n")

    return []


def validate_fn(node, scope):
    # check fn arguments number
    if len(node) != 4 and len(node) != 5:
        raise Exception(f"Wrong number of arguments for fn: {node}")


def __def__(node, scope):
    debug(f"__def__():  compiletime - node: {node}")

    validate_def(node, scope)

    names = scope["names"]
    def_, mutdecl, name, data = node

    if len(data) == 1:
        if isinstance(name, list):
            debug(f"__def__():  compiletime - name is list - name: {name}")

            type_ = _solve_list_name_type(name, scope)

        else:
            name_candidate = eval.get_name_value(name, scope)
            if name_candidate == []:
                raise Exception(f"Unassigned name: {name}")

            type_ = name_candidate[2]

    elif len(data) == 2:
        type_ = data[0]

    if len(data) == 1:
        value = data[0]

    elif len(data) == 2:
        value = data[1]

    if not isinstance(name, list):
        debug(f"__def__():  value: {value} - typeof {name} not list")

        # remove old value from names
        for index, v in enumerate(names):
            if v[0] == name:
                names.remove(v)
                break

        # add string length to output ;)
        if type_ == "Str":
            value = [value, len(value)]

        # insert new value into names
        names.append([name, mutdecl, type_, value])

    else:
        debug(f"__def__():  frontend compiletime - name is list - name: {name} type: {type_}")

        if isinstance(type_, list):
            if type_[0] == "Array":
                _set_array_member(name, scope, value)

        else:
            _set_struct_member(name, scope, value)

    debug(f"\n__def__():  frontend compiletime - names after def: {names}\n")

    # retv = ["data", [type_, value]]
    # print(f"returning {retv}")
    return []


def validate_def(node, scope):
    debug(f"""validate_def():  frontend compiletime - node: {node} scope["names"]: {scope["names"]}""")

    # check def arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for def: {node}")

    def_, mutdecl, name, data = node

    is_reassignment = False
    type_ = None

    generic_types_values = [t for t in scope["names"] if isinstance(t[2], list) and len(t[2]) > 0]
    debug(f"validate_def():  generic_types_values: {generic_types_values}")

    structs = [s[0] for s in scope["names"] if s[2] == "struct"]
    debug(f"validate_def():  structs: {structs}")

    if len(data) == 1:

        # gets correct name to search
        search_name = name

        # if type of name is list, take the first
        if isinstance(name, list):
            search_name = name[0]

        name_candidate = eval.get_name_value(search_name, scope)

        if name_candidate == []:
            raise Exception(f"Reassignment of unassigned name - name: {name} value: {data[0]}")

        type_ = name_candidate[2]
        value = data[0]

    elif len(data) == 2:
        type_ = data[0]
        value = data[1]

    if type_ is None:
        raise Exception("Type not found!")

    # check mutability declaration
    if mutdecl not in ["const", "mut"]:
        raise Exception(f"Assignment with invalid mutability declaration: {node}")

    if type_ in structs:
        struct_type = [st for st in scope["names"] if st[2] == "struct" and st[0] == type_][0]
        debug(f"validate_def():  frontend compiletime - struct_type: {struct_type}")

        if len(value) != len(struct_type[3]):
            raise Exception(f"Initializing struct with wrong number of member values: {value} {struct_type[3]}")

        for value_member in value:
            for struct_member in struct_type[3]:
                # print(f"value_member {value_member} {struct_type} {structs}")
                value_member_type = None
                struct_names = []
                for st in structs:
                    for sts in scope["names"]:
                        # print(f"st {st} sts {sts}")
                        if st == sts[2]:
                            struct_names.append(sts)
                # print(f"struct_names {struct_names}")
                found_value_member = False
                value_member_type = None
                for s in struct_names:
                    if value_member == s[0]:
                        found_value_member = True
                        value_member_type = s[2]

                if found_value_member:
                    value_member_type = value_member_type
                else:
                    it_value_member = eval._infer_type(value_member)
                    # print(f"it_value_member: {it_value_member} struct_member: {struct_member}")
                    if it_value_member is not None:
                        value_member_type = it_value_member[0]
                    else:
                        # value_member_type = value_member[1]
                        pass

                if len(struct_member) == 2:
                    struct_member_type = struct_member[1]
                elif struct_member[0] == "mut":
                    struct_member_type = struct_member[2]
                else:
                    debug(f"validate_def():  frontend compiletime - struct_member: {struct_member}")

                if value_member_type != struct_member_type:
                    raise Exception(f"Initializing struct with invalid value type for member: value_member_type: {value_member_type}  struct_member_type: {struct_member_type}")

    elif type_ in generic_types_values:
        debug(f"validate_def():  frontend compiletime - Generic type value!")

    # check reassignment over const
    # check const reassignment over mut
    if type_ != "fn" and not isinstance(name, list):
        debug(f"validate_def():  frontend compiletime - value isn't function and name isn't list")
        debug(f"""validate_def():  frontend compiletime - scope["names"]:  {scope["names"]}""")

        for index, v in enumerate(scope["names"]):
            if v[0] == name:
                if v[1] == "const":
                    raise Exception(f"Trying to reassign constant: {node}")

                elif v[1] == "mut" and mutdecl == "const":
                    raise Exception(f"Trying to reassign a constant name over a mutable name: {node}")


def _set_struct_member(li, scope, value):
    # print(f"_set_struct_member {li} {scope} {value}")

    def myfn(n, index):
        new_li = n[3][index]
        if len(li) > 2:
            return _set_struct_member([new_li] + li[2:], scope)
        else:
            # print(f"n: {n}")
            value_type = eval._infer_type(value)[0]
            # print(f"value_type: {value_type}")

            n_type = n[2]
            struct_matches = [n for n in scope["names"] if n[0] == n_type and n[2] == "struct"]
            member_type = struct_matches[0][3][0][2]

            # print(f"member_type: {member_type}")

            if value_type != member_type:
                raise Exception("Setting struct member with invalid value type: {value_type}")

            n[3][index] = value
            # print(f"value: {value}")

    return eval._seek_struct_ref(li, scope, myfn)


def _set_array_member(li, scope, value):
    debug(f"_set_array_member():  li: {li} value: {value}")

    def myfn(n, index):
        debug(f"myfn():  - n: {n} index: {index} value: {value}")

        if not scope["backend_scope"]:
            n[3][index] = value

        debug(f"myfn():  - n after def: {n}")

    return eval._seek_array_ref(li, scope, myfn)


def _solve_list_name_type(name, scope):
    debug(f"_solve_list_name_type()  - name: {name}")

    def iter(li, scope):
        debug(f"iter():  - li: {li}")

        name_value = eval.get_name_value(li[0], scope)
        debug(f"iter():  - name_value: {name_value}")

        name_, mutdecl, type_, value = name_value

        if type_[0] == "Array":
            debug(f"iter():  - type_[0] is Array")

            return type_

        if type_[0] == "ptr":
            debug(f"iter():  - type[0] is ptr")

            return type_

    type_ = iter(name, scope)

    debug(f"_solve_list_name_type():  type_: {type_}")

    return type_


def split_function_arguments(arg_pieces):
    debug(f"split_function_arguments():  arg_pieces: {arg_pieces}")

    split_args = []
    buf = []

    for piece in arg_pieces:
        debug(f"split_function_arguments():  piece: {piece}")

        is_comma = piece == ","
        if is_comma:
            # print(f"buf: {buf}")
            split_args.append(buf.copy())
            buf = []
        else:
            buf.append(piece)
    if len(buf) > 0:
        split_args.append(buf.copy())

    debug(f"split_function_arguments():  split_args: {split_args}")

    return split_args


def __set__(node, scope):
    debug("__set__():  frontend compiletime")

    validate_set(node, scope)

    set, name, value = node

    name_value = eval.get_name_value(name, scope)
    name_value[3] = value

    return []


def validate_set(node, scope):
    debug("validate_set():  frontend compiletime")

    # validate node size
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for set: {node}")

    # validate name
    name_value = eval.get_name_value(node[1], scope)
    if name_value == []:
        raise Exception(f"Resetting undefined name: {node}")

    # validate name mutability
    debug(f"validate_set():  name_value: {name_value}")
    if name_value[1] == "const":
        raise Exception(f"Resetting constant name: {node} {name_value}")


def __set_member__(node, scope):
    validate_set_member(node, scope)

    return []


def validate_set_member(node, scope):
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for set_member: {node}")


def __macro__(node, scope):
    """
    Set a new macro in the current scope.

    Syntax:
    macro alias (syntax) (expanded)
    """

    # print(f"calling __macro__ {node}")

    validate_macro(node, scope)

    macro, alias, syntax, expanded = node

    def join_quotes(li):
        # print(f"join_quotes {li}")

        to_join = []

        kuote = False
        for index, i in enumerate(li.copy()):
            if i == "'":
                kuote = True

            elif kuote == True:
                to_join.append([index - 1, index])
                kuote = False

            elif isinstance(i, list):
                li[index] = join_quotes(i)

        for j in reversed(to_join):
            start, end = j
            # print(f"start {start} {li[start]}")
            # print(f"end {end} {li[end]}")

            # print(f"old li {li} {li[start]}")
            quote = li.pop(start)
            # print(f"old li2 {li} {li[start]}")
            value = li.pop(start)
            # print(f"new_li {li}")

            li.insert(start, "".join([quote, value]))

        return li

    new_syntax = join_quotes(syntax)
    # print(f"new_syntax: {new_syntax}")

    new_expanded = join_quotes(expanded)
    # print(f"new_expanded: {new_expanded}")

    scope["macros"].append([alias, new_syntax, new_expanded])

    return []


def validate_macro(node, scope):
    # check macro arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for macro: {node}")


def __if__(node, scope):
    debug(f"calling __if__:  compiletime - node: {node}")

    validate_if(node, scope)

    return []

#    if_, condition_list, true_list, false_list = node
#
#    result = eval(condition_list)
#    # print(f"result: {result}")
#
#    is_true = result[0] == 'data' and result[1][0] == 'bool' and result[1][1] == 'true'
#
#    if is_true:
#        return true_list
#
#    else:
#        return false_list


def validate_if(node, scope):
    # check if arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for if: {node}")

    # check if condition is of type bool
    pass


def __else__(node, scope):
    debug(f"__else__():  frontend compiletime - node: {node}")

    return []


def __data__(node, scope):
    # print(f"calling __data__: {node}")

    # validate_data(node, scope)

    return node[1:]


# def validate_data(node, scope):
#    # check data arguments number
#    if len(node) != 2:
#        raise Exception(f"Wrong number of arguments for data: {node}")


def __write_ptr__(node, scope):
    validate_write_ptr(node, scope)
    return node


def validate_write_ptr(node, scope):
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for write_ptr: {node}")

    if scope["safe"] == True:
        raise Exception(f"Trying to write_ptr outside of unsafe scope: {node}")


def __read_ptr__(node, scope):
    validate_read_ptr(node, scope)
    return node


def validate_read_ptr(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for read_ptr: {node}")

    if scope["safe"] == True:
        raise Exception(f"Trying to read_ptr outside of unsafe scope: {node}")


def __get_ptr__(node, scope):
    validate_get_ptr(node, scope)
    return node


def validate_get_ptr(node, scope):
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for get_ptr: {node}")


def __size_of__(node, scope):
    validate_size_of(node, scope)
    return node


def validate_size_of(node, scope):
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for size_of: {node}")


def __unsafe__(node, scope):
    validate_unsafe(node, scope)
    return node[1]


def validate_unsafe(node, scope):
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for unsafe: {node}")


scope = copy.deepcopy(eval.default_scope)
scope["names"] = [  # names
    ["fn", "mut", "internal", __fn__],
    ["def", "mut", "internal", __def__],
    ["set", "mut", "internal", __set__],
    ["set_member", "mut", "internal", __set_member__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["else", "mut", "internal", __else__],
    ["data", "mut", "internal", __data__],
    # ["meta", "mut", "internal", __meta__],
    ["write_ptr", "mut", "internal", __write_ptr__],
    ["read_ptr", "mut", "internal", __read_ptr__],
    ["get_ptr", "mut", "internal", __get_ptr__],
    ["size_of", "mut", "internal", __size_of__],
    ["unsafe", "mut", "internal", __unsafe__],
  ]
