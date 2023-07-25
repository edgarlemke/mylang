import eval


def __fn__(node, scope):
    """
    Validate function declarations.

    Syntax:
    fn ((argtype1 arg1)(argtype2 arg2)) ret_type (body)
    """

    # print(f"calling __fn__ {node}")

    validate_fn(node, scope)

    # create new scope
    child_scope = [[], [], scope, []]
    scope[3].append(child_scope)

    return node


def validate_fn(node, scope):
    # check fn arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for fn: {node}")

    fn, args, ret_type, body = node
    types = [t[0] for t in scope[0] if t[2] == "type"]

#    # check if types of the arguments are valid
#    split_args = _split_fn_args(args)
#    for arg in split_args:
#        # type_, name = arg
#        name, type_ = arg
#        if type_ not in types:
#            raise Exception(f"Function argument has invalid type: {arg} {node}")

#    # check if the return type is valid
#    if ret_type not in types:
#        raise Exception(f"Function return type has invalid type: {ret_type} {node}")


def __handle__(node, scope):
    # print(f"__handle__ node: {node} {scope[5][0]}")
    _validate_handle(node, scope)

    first_cond = (not isinstance(node[1], list) and scope[5][0] == node[1])
    second_cond = (isinstance(node[1], list) and scope[5][0] in node[1])

    if scope[5] is not None and (first_cond or second_cond):
        handler_scope = eval.default_scope.copy()
        handler_scope[2] = scope
        scope[3].append(handler_scope)

        # print(f"node: {node}")
        if len(node) == 4:
            __set__(['set', 'const', node[3], ['data', scope[5]]], handler_scope)
            eval.eval(node[len(node) - 1], handler_scope)

        scope[3].remove(handler_scope)

        li = eval.eval(node[len(node) - 1], handler_scope)

        # clear forced handler field
        scope[5] = None

        return li[0]

    return []


def _validate_handle(node, scope):
    if len(node) not in [3, 4]:
        raise Exception(f"Wrong number of arguments for handle: {node}")


def __set__(node, scope):
    """
    Validate set i.e. constant setting.

    Syntax:
    set name mutability (type value)

    mutablity values can be "const" or "mut", without the quotes
    """

    # print(f"calling __set__ {node}")

    _validate_set(node, scope)

    names = scope[0]
    set_, mutdecl, name, data = node
    type_ = data[0]

    if type_ == "fn":
        value = list(data[1:4])
        value[0][0] = _split_fn_args(value[0][0])

        all_fn = [(i, var) for i, var in enumerate(names) if var[1] == "fn" and var[0] == name]
        # print(f"all_fn: {all_fn}")

        if all_fn == []:
            # print(f"empty all_fn")
            names.append([name, mutdecl, type_, [value]])

        else:
            match_fn = all_fn[0]
            i, var = match_fn

            names[i][3].append(value)

    else:
        value = data[1]

        if not isinstance(name, list):
            # print(f"value: {value}")
            # print(f"typeof {name} not list")

            # valid_value = None
            # types = [t for t in scope[0] if t[2] == "type"]
            # structs = [s for s in scope[0] if s[2] == "struct"]
            # valid_types = types + structs

            # for T in valid_types:
            #    # print(f"T[0]: {T[0]} type_: {type_}")
            #    if T[0] == type_:
            #        valid_value = _validate_value(type_, value, scope)
            #        #print(f"valid_value: {valid_value}")
            #        break

            # remove old value from names
            for index, v in enumerate(names):
                if v[0] == name:
                    names.remove(v)
                    break

            # insert new value into names
            names.append([name, mutdecl, type_, value])

        else:
            # print(f"name: {name}")
            _set_struct_member(name, scope, value)

    # print(f"names after set: {names}")

    # retv = ["data", [type_, value]]
    # print(f"returning {retv}")
    return []


def _validate_set(node, scope):
    # check set arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for set: {node}")

    set_, mutdecl, name, data = node
    type_ = data[0]
    value = data[1]

    # check mutability declaration
    if mutdecl not in ["const", "mut"]:
        raise Exception(f"Assignment with invalid mutability declaration: {node}")

    types = [t[0] for t in scope[0] if t[2] == "type"]
    structs = [s[0] for s in scope[0] if s[2] == "struct"]
    exceptions = ["fn"]

#    # check type
#    valid_types = (types + structs + exceptions)
#    # print(f"valid_types: {valid_types}")
#    if type_ not in valid_types:
#        raise Exception(f"Constant assignment has invalid type {type_} {node}")

    # check if value is valid for type
    # print(f"type_ {type_}")
    # print(f"structs {structs}")
    if type_ in structs:
        struct_type = [st for st in scope[0] if st[2] == "struct" and st[0] == type_][0]
        # print(f"struct_type: {struct_type}")

        if len(value) != len(struct_type[3]):
            raise Exception("Initializing struct with wrong number of member values: {value} {struct_type[3]}")

        for value_member in value:
            for struct_member in struct_type[3]:
                # print(f"value_member {value_member} {struct_type} {structs}")
                value_member_type = None
                struct_names = []
                for st in structs:
                    for sts in scope[0]:
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
                    value_member_type = it_value_member[0]

                struct_member_type = struct_member[2]
                if value_member_type != struct_member_type:
                    raise Exception(f"Initializing struct with invalid value type for member: {value_member_type} {struct_member_type}")

    # check reassignment over const
    # check const reassignment over mut
    if type_ != "fn" and not isinstance(name, list):
        for index, v in enumerate(scope[0]):
            if v[0] == name:
                if v[1] == "const":
                    raise Exception("Trying to reassign constant: {node}")

                elif v[1] == "mut" and mutdecl == "const":
                    raise Exception("Trying to reassign a constant name over a mutable name: {node}")


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
            struct_matches = [n for n in scope[0] if n[0] == n_type and n[2] == "struct"]
            member_type = struct_matches[0][3][0][2]

            # print(f"member_type: {member_type}")

            if value_type != member_type:
                raise Exception("Setting struct member with invalid value type: {value_type}")

            n[3][index] = value
            # print(f"value: {value}")

    return eval._seek_struct_ref(li, scope, myfn)


def _split_fn_args(args):
    # print(f"args: {args}")

    split_args = []
    buf = []
    ct = 0

    for arg in args:
        buf.append(arg)

        if ct == 1:
            split_args.append(buf.copy())
            buf = []
            ct = 0
        else:
            ct += 1

    # print(f"split_args: {split_args}")

    return split_args


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

    scope[1].append([alias, new_syntax, new_expanded])

    return []


def validate_macro(node, scope):
    # check macro arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for macro: {node}")


def __if__(node, scope):
    """
    """
#    print(f"calling __if__: {node}")

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


def __data__(node, scope):
    # print(f"calling __data__: {node}")

    # validate_data(node, scope)

    return node[1:]


# def validate_data(node, scope):
#    # check data arguments number
#    if len(node) != 2:
#        raise Exception(f"Wrong number of arguments for data: {node}")


def __write_ptr__(node, scope):
    _validate_write_ptr(node, scope)
    return node


def _validate_write_ptr(node, scope):
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for write_ptr: {node}")

    if scope[4] == True:
        raise Exception(f"Trying to write_ptr outside of unsafe scope: {node}")


def __read_ptr__(node, scope):
    _validate_read_ptr(node, scope)
    return node


def _validate_read_ptr(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for read_ptr: {node}")

    if scope[4] == True:
        raise Exception(f"Trying to read_ptr outside of unsafe scope: {node}")


def __get_ptr__(node, scope):
    _validate_get_ptr(node, scope)
    return node


def _validate_get_ptr(node, scope):
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for get_ptr: {node}")


def __size_of__(node, scope):
    _validate_size_of(node, scope)
    return node


def _validate_size_of(node, scope):
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for size_of: {node}")


def __unsafe__(node, scope):
    _validate_unsafe(node, scope)
    return node[1]


def _validate_unsafe(node, scope):
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for unsafe: {node}")


scope = [
  [  # names
    ["fn", "mut", "internal", __fn__],
    ["handle", "mut", "internal", __handle__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["data", "mut", "internal", __data__],
    # ["meta", "mut", "internal", __meta__],
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
