import eval_types
import re


def eval(li, scope):
    # print(f"\neval {li} {scope}")

    if scope is None:
        scope = runtime_scope

    if len(li) == 0:
        # print(f"exiting eval {li}")
        return li

#    if li[0] == "data":
#        return li

    new_li = None
    macros = scope[1]
    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            new_li, found_macro = expand_macro(new_li, scope)
            # print(f"expand new_li: {new_li}")
            expand = found_macro

        # print(f"over new_li: {new_li}")

        li = new_li

    is_macro = li[0] == "macro"
    is_list = isinstance(li[0], list)

    if is_list:
        evaled_li = []
        for key, item in enumerate(li):
            # li[key] = eval(item, scope)
            e = eval(item, scope)
            if len(e) > 0:
                evaled_li.append(e)
        li = evaled_li

    else:
        # get all names matching list's first value
        name_matches = [n for n in scope[0] if n[0] == li[0]]

        # check name_matches size
        if len(name_matches) == 0:
            raise Exception(f"Unassigned name: {li[0]}")
        elif len(name_matches) > 1:
            raise Exception(f"More than one name set, it's a bug! {li[0]}")

        # get the only valid name
        n = name_matches[0]
        # print(f"n: {n}")

        if n[2] in ["fn", "internal"]:
            # print(f"fn/internal")
            # len 1, so is a reference
            if len(li) == 1:
                # print(f"fn ref {li}")
                li = n[1:]

            # len > 1, so is a function call
            else:
                if n[2] == "fn":
                    x = call_fn(li, n, scope)
                    li = x
                elif n[2] == "internal":
                    # print(f"!!! internal")
                    x = n[3](li, scope)
                    li = x

        else:
            if len(li) == 1:
                if isinstance(n[3], list):
                    # print(f"evaling {n[3]}")
                    evaled_n3 = eval(n[3], scope)
                    if n[2] != evaled_n3[0]:
                        raise Exception(f"Wrong type! {n[2]} {evaled_n3[0]}")
                    li = evaled_n3

                else:
                    li = n[2:]
            else:
                li = _get_struct_member(li, scope)

    # print(f"exiting eval {li}")
    return li


def call_fn(li, fn, scope):
    # print(f"call_fn {li}")

    name = fn[0]
    methods = fn[3]
    candidates = []
    for m in methods:
        # print(f"method: {m}")

        # match types
        match = True
        for arg_i, arg in enumerate(li[1:]):
            # print(f"argument: {arg_i} {arg}")

            # break in methods without the arguments
            if len(m[0]) < arg_i + 1:
                match = False
                break

            # if an argument name starts with ', consider anything a match
            # print(f"m0: {m[0][arg_i]}")
            # if m[0][arg_i][0][0][0] == "'":
            #    continue

            # solve argument
            solved_arg = None

            is_list = isinstance(arg, list)
            if is_list:
                solved_arg = eval(arg, scope)

            else:
                name_value = get_name_value(arg, scope)
                found_value = name_value != []

                if found_value:
                    solved_arg = name_value

                else:
                    solved_arg = infer_type(arg)

            if solved_arg is None:
                match = False
                break

            if len(solved_arg) == 0:
                pass

            else:
                # print(f"solved_arg: {solved_arg}")
                # print(f"m: {m}")
                # print(f"m[0]: {m[0][0][arg_i]} {arg_i}")
                marg = m[0][0][arg_i]
                # print(f"marg: {marg}")

                if solved_arg[0] != marg[0]:
                    match = False
                    break

        if match:
            candidates.append(m)

    if len(candidates) == 0:
        fns = [n for n in scope[0] if n[2] == "fn"]
        raise Exception(f"No candidate function found: {name} {fns}")
    if len(candidates) > 1:
        raise Exception(f"Method candidates mismatch: {name} {candidates}")

    the_method = candidates[0][0]
    # print(f"the_method: {the_method}")

    retv = eval(the_method[2], scope)
    # print(f"exiting call_fn {li}")
    return retv


def get_name_value(name, scope):
    def iterup(scope):
        # print(f"interup {scope}")
        for n in scope[0]:
            # print(f"n: {n}")
            if n[0] == name:
                return list(n[2:])

        # didn't return found value...

        # if has parent scope, iterup
        if scope[2] is not None:
            return iterup(scope[2])
        # else, return empty list
        else:
            return []

    return iterup(scope)


def infer_type(arg):
    candidates = []

    int_regexp = "[0-9]+"
    m = re.match(int_regexp, arg)
    if m:
        candidates.append([m, "int"])

    float_regexp = "[0-9]+\\.[0-9]+"
    m = re.match(float_regexp, arg)
    if m:
        candidates.append([m, "float"])

    bool_regexp = "true|false"
    m = re.match(bool_regexp, arg)
    if m:
        candidates.append([m, "bool"])

    biggest = None
    for c in candidates:
        if biggest is None:
            biggest = c
        else:
            if len(c[0].group()) > len(biggest[0].group()):
                biggest = c

            elif len(c[0].group()) == len(biggest[0].group()):
                raise Exception("Two candidates with same size!")

    if biggest is None:
        return None

    return [biggest[1], arg]


def expand_macro(li, scope):
    # print(f"expand_macro: {li}")

    new_li = li.copy()
    found_macro = False

    # for each item in li
    for index, item in enumerate(li):
        # print(f"LI index: {index} item: {item}")

        found_macro = False
        for macro in scope[1]:
            # print(f"macro: {macro}")

            found_macro, full_match, bindings = match_macro(li, index, macro)
            # print(f"AA> {new_li} {found_macro}")

            if found_macro:
                # expand macro
                new_li = li.copy()
                # print(f"full_match: {full_match}")

                for i in reversed(full_match):
                    new_li.pop(i)

                # print(f"all bindings: {bindings}")

                def subst_item(extended):
                    # print(f"subs_item: {extended}")
                    new_extended = extended.copy()

                    for index, item in enumerate(extended):
                        # print(f"ext index: {index} item: {item}")
                        if isinstance(item, list):
                            new_extended[index] = subst_item(item)

                        else:
                            for b in bindings:
                                name, value = b
                                # print(f"bindings name {name} value {value} item {item}")

                                if name == item:
                                    new_extended[index] = value

                    return new_extended

                subst_extended = subst_item(macro[2])
                for i in reversed(subst_extended):
                    new_li.insert(full_match[0], i)

                break

        if found_macro:
            break

    return [new_li, found_macro]


def match_macro(li, index, macro):
    # print(f"match_macro - li: {li} index: {index} macro: {macro}")

    alias, syntax, extended = macro

    # li_piece = li[index : index+len(syntax)]
    li_piece = li[index:]
    bindings = []

    full_match = False
    for cur_index, cur in enumerate(li_piece):
        # print(f"cur {cur_index} {cur}")

        matching = []

        for cur_index2, cur2 in enumerate(li_piece[cur_index:cur_index + len(syntax)]):
            # print(f"cur2 {cur_index2} {cur2}")
            if syntax[cur_index2] == cur2:
                matching.append(cur_index + cur_index2)
                # print(f">>> common matching {cur2} against {syntax[cur_index2]}")

            elif syntax[cur_index2][0] == "'":
                bindings.append([syntax[cur_index2], cur2])
                matching.append(cur_index + cur_index2)
                # print(f">>> quoted maching {cur2} against {syntax[cur_index2]}")

            else:
                # print(f">>> no match {cur2} against {syntax[cur_index2]}")
                bindings = []
                break

        if len(matching) == len(syntax):
            # print(f"BINGO ==> matching: {matching} syntax: {syntax}\n")
            full_match = matching
            break

    if not full_match:
        return (False, full_match, [])

    return (True, full_match, bindings)


def _get_struct_member(li, scope):
    def myfn(n, index):
        new_li = n[3][index]

        if len(li) > 2:
            return _get_struct_member([new_li] + li[2:], scope)
        else:
            # print(f"n: {n}")
            # print(f"new_li: {new_li}")
            matches = [name for name in scope[0] if name[0] == n[2] and name[2] == "struct"]
            # print(f"matches: {matches}")
            member_type = matches[0][3][index][2]
            # print(f"member_type: {member_type}")

            return [member_type, new_li]

    return _seek_struct_ref(li, scope, myfn)


def _set_struct_member(li, scope, value):
    # print(f"_set_struct_member {li} {scope} {value}")

    def myfn(n, index):
        new_li = n[3][index]
        if len(li) > 2:
            return _set_struct_member([new_li] + li[2:], scope)
        else:
            # print(f"n: {n}")
            value_type = infer_type(value)[0]
            # print(f"value_type: {value_type}")

            n_type = n[2]
            struct_matches = [n for n in scope[0] if n[0] == n_type and n[2] == "struct"]
            member_type = struct_matches[0][3][0][2]

            # print(f"member_type: {member_type}")

            if value_type != member_type:
                raise Exception("Setting struct member with invalid value type: {value_type}")

            n[3][index] = value
            # print(f"value: {value}")

    return _seek_struct_ref(li, scope, myfn)


def _seek_struct_ref(li, scope, fn):
    # print(f"_get_struct_member li: {li}")

    # seeks names matching with li[0]
    name_matches = [n for n in scope[0] if n[0] == li[0]]
    n = name_matches[0]

    # get possible struct name
    struct_name = n[2]

    # check if there's some struct set with this name
    candidates = [s for s in scope[0] if s[2] == "struct" and s[0] == struct_name]
    # print(f"candidates: {candidates}")

    # get the candidate struct
    c = candidates[0]

    # check if member name exists
    member_name = li[1]
    members_match = [(index, m) for index, m in enumerate(c[3]) if m[1] == member_name][0]
    # print(f"members_match: {members_match}")

    if len(members_match) == 0:
        raise Exception(f"Struct {struct_name} has no member {member_name}")

    # get value
    # print(f"n: {n}")
    index, m = members_match
    # new_li = n[3][index]
    return fn(n, index)

    # check if member access "goes deeper"
    # if len(li) > 2:
    #    # print(f"len(li) > 2: {li} {new_li}")
    #    return _get_struct_member([new_li] + li[2:], scope)
    # else:
    #    return new_li


# RUNTIME INTERNALS
#
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

    # check if types of the arguments are valid
    for arg in args:
        type_, name = arg
        if type_ not in types:
            raise Exception(f"Function argument has invalid type: {arg} {node}")

    # check if the return type is valid
    if ret_type not in types:
        raise Exception(f"Function return type has invalid type: {ret_type} {node}")


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
                    if v[1] == "const":
                        raise Exception("Trying to reassign constant: {node}")

                    elif v[1] == "mut":
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

    types = [t[0] for t in scope[0] if t[2] == "type"]
    structs = [s[0] for s in scope[0] if s[2] == "struct"]
    exceptions = ["fn"]

    # check type
    valid_types = (types + structs + exceptions)
    # print(f"valid_types: {valid_types}")
    if type_ not in valid_types:
        raise Exception(f"Constant assignment has invalid type {type_} {node}")

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
                    it_value_member = infer_type(value_member)
                    # print(f"it_value_member: {it_value_member} struct_member: {struct_member}")
                    value_member_type = it_value_member[0]

                struct_member_type = struct_member[2]
                if value_member_type != struct_member_type:
                    raise Exception(f"Initializing struct with invalid value type for member: {value_member_type} {struct_member_type}")

    else:
        pass


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


def __let__(node, scope):
    """
    Shortcut for defining an anonymous function and calling it with the given arguments
    """
#    print(f"calling __let__: {node}")

    validate_let(node, scope)

    let_, args, body = node

    return []


def validate_let(node, scope):
    # check let arguments number
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for let: {node}")


def __data__(node, scope):
    # print(f"calling __data__: {node}")

    validate_data(node, scope)

    return node[1]


def validate_data(node, scope):
    # check data arguments number
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for data: {node}")


def __meta__(node, scope):
    #    print(f"calling __meta__: {node}")

    return eval(node[1:], meta_scope)


def __write_ptr__(node, scope):
    _validate_write_ptr(node, scope)
    return node


def _validate_write_ptr(node, scope):
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for write_ptr: {node}")


def __read_ptr__(node, scope):
    _validate_read_ptr(node, scope)
    return node


def _validate_read_ptr(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for read_ptr: {node}")


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
#
#


meta_scope = [
  [
    ["fn", "mut", "internal", __fn__],
    ["let", "mut", "internal", __let__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["data", "mut", "internal", __data__],
  ],
  [],
  None,
  []
]
runtime_scope = [
  [
    ["fn", "mut", "internal", __fn__],
    ["let", "mut", "internal", __let__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["data", "mut", "internal", __data__],
    ["meta", "mut", "internal", __meta__],
    ["write_ptr", "mut", "internal", __write_ptr__],
    ["read_ptr", "mut", "internal", __read_ptr__],
    ["get_ptr", "mut", "internal", __get_ptr__],
    ["size_of", "mut", "internal", __size_of__],
  ],
  [],
  None,
  []
]


def _add_types():
    types = [
#      ["i8", "mut", "type", [1]],
#      ["i16", "mut", "type", [2]],
#      ["i32", "mut", "type", [4]],
#      ["i64", "mut", "type", [8]],
      ['int', "mut", 'type', ['?']],  # signed int, register width

#      ["u8", "mut", "type", [1]],
#      ["u16", "mut", "type", [2]],
#      ["u32", "mut", "type", [4]],
#      ["u64", "mut", "type", [8]],
      ['uint', "mut", 'type', ['?']],  # unsigned int, register width

      ["byte", "mut", "type", [1]],
      ["bool", "mut", "type", [1]],

#      ["f32", "mut", "type", [4]],
#      ["f64", "mut", "type", [8]],
      ['float', "mut", 'type', ['?']],

      ["struct", "mut", "type", ['?']],
      ["enum", "mut", "type", ['?']],
      ["ptr", "mut", "type", ['?']],  # the size will probably be the same of int, have complementary type
    ]

    for s in [meta_scope, runtime_scope]:
        for t in types:
            s[0].append(t)


_add_types()
