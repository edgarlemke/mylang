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

    # extract type
    if len(data) == 1:
        if isinstance(name, list):
            debug(f"__def__():  compiletime - name is list - name: {name}")

            type_ = _solve_list_name_type(name, scope)

        else:
            name_candidate = eval.get_name_value(name, scope)
            if name_candidate == []:
                raise Exception(f"Unassigned name: {name}")

            type_ = name_candidate[2]

    elif len(data) >= 2:
        type_ = data[0]

    debug(f"__def__():  extracted type_: {type_}")

    # extract value
    if len(data) == 1:
        value = data[0]

    elif len(data) >= 2:
        if type_ in ["struct", "TUnion"]:
            value = data[1:]
        else:
            value = data[1]

#    if not isinstance(name, list):
#    debug(f"__def__():  value: {value} - typeof {name} not list")

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

#    else:
#        debug(f"__def__():  frontend compiletime - name is list - name: {name} type: {type_}")
#
#        if isinstance(type_, list):
#            if type_[0] == "Array":
#                _set_array_member(name, scope, value)
#
#        else:
#            _set_struct_member(name, scope, value)

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
    debug(f"validate_def():  data: {data}")

    is_reassignment = False
    type_ = None

    generic_types_values = [t for t in scope["names"] if isinstance(t[2], list) and len(t[2]) > 0]
    debug(f"validate_def():  generic_types_values: {generic_types_values}")

    # FIXME: get all structs from all scopes
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

    elif len(data) >= 2:
        type_ = data[0]

        debug(f"validate_def():  type_: {type_}")

        if type_ in structs:
            value = data[1:][0]
        else:
            value = data[1]

        debug(f"validate_def():  value: {value}")

    if type_ is None:
        raise Exception(f"Type not found: {type_}")

    # check mutability declaration
    if mutdecl not in ["const", "mut"]:
        raise Exception(f"Assignment with invalid mutability declaration: {node}")

    # validate structs declarations
    if type_ in structs:
        struct_type = [st for st in scope["names"] if st[2] == "struct" and st[0] == type_][0]
        debug(f"validate_def():  frontend compiletime - struct_type: {struct_type}")

        if len(value) != len(struct_type[3][0]):
            raise Exception(f"Initializing struct with wrong number of member values: {value} {struct_type[3][0]}")

        debug(f"validate_def():  value: {value}")

        found_struct_members = []
        for value_member in value:
            debug(f"validate_def():  value_member: {value_member} struct_type[3][0]: {struct_type[3][0]}")

            for struct_member in struct_type[3][0]:
                debug(f"validate_def():  value_member: {value_member} struct_member: {struct_member}")

                if struct_member in found_struct_members:
                    debug(f"validate_def():  struct_member already found")
                    continue

                value_member_type = None
                struct_names = []
                for st in structs:
                    for sts in scope["names"]:
                        # print(f"st {st} sts {sts}")
                        if st == sts[2]:
                            struct_names.append(sts)

                debug(f"validate_def():  struct_names {struct_names}")

                found_value_member = False
                for s in struct_names:
                    if value_member == s[0]:
                        found_value_member = True
                        value_member_type = s[2]

                if found_value_member:
                    # value_member_type = value_member_type
                    pass

                else:
                    debug(f"validate_def():  frontend compiletime - not found value member")

                    it_value_member = None
                    it_value_member = eval._infer_type(value_member)
                    debug(f"validate_def():  it_value_member: {it_value_member} struct_member: {struct_member}")

                    if it_value_member is not None:
                        value_member_type = it_value_member[0]

                    else:
                        # value_member_type = value_member[1]
                        debug(f"validate_def():  value_member_type is None")
                        pass

                    debug(f"validate_def():  value_member_type: {value_member_type}")

                debug(f"validate_def():  struct_member: {struct_member}")

                if len(struct_member) == 2:
                    debug(f"validate_def():  len(struct_member) == 2")
                    struct_member_type = struct_member[1]

                elif struct_member[0] == "mut":
                    struct_member_type = struct_member[2]

                else:
                    debug(f"validate_def():  frontend compiletime - struct_member: {struct_member}")

                if value_member_type != struct_member_type:
                    raise Exception(f"Initializing struct with invalid value type for member: value_member_type: {value_member_type}  struct_member_type: {struct_member_type}")

                found_struct_members.append(struct_member)

                break

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


# def _set_struct_member(li, scope, value):
#    # print(f"_set_struct_member {li} {scope} {value}")
#
#    def myfn(n, index):
#        new_li = n[3][index]
#        if len(li) > 2:
#            return _set_struct_member([new_li] + li[2:], scope)
#        else:
#            # print(f"n: {n}")
#            value_type = eval._infer_type(value)[0]
#            # print(f"value_type: {value_type}")
#
#            n_type = n[2]
#            struct_matches = [n for n in scope["names"] if n[0] == n_type and n[2] == "struct"]
#            member_type = struct_matches[0][3][0][2]
#
#            # print(f"member_type: {member_type}")
#
#            if value_type != member_type:
#                raise Exception("Setting struct member with invalid value type: {value_type}")
#
#            n[3][index] = value
#            # print(f"value: {value}")
#
#    return eval._seek_struct_ref(li, scope, myfn)


# def _set_array_member(li, scope, value):
#    debug(f"_set_array_member():  li: {li} value: {value}")
#
#    def myfn(n, index):
#        debug(f"myfn():  - n: {n} index: {index} value: {value}")
#
#        if scope["step"] in ["frontend"]:
#            n[3][index] = value
#
#        debug(f"myfn():  - n after def: {n}")
#
#    return eval._seek_array_ref(li, scope, myfn)


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


# MEMBERS INTERNALS
#
def __ref_member__(node, scope):
    debug(f"__ref_member__():  frontend compiletime - node: {node}")
    validate_ref_member(node, scope)

    ref_member_, base, member = node

    # handling simple member access
    if not isinstance(base, list):
        debug(f"__ref_member__():  base isn't list")
        base_name_value = eval.get_name_value(base, scope)

        debug(f"__ref_member__():  base_name_value: {base_name_value}")
        base_type = base_name_value[2]

        # handle arrays
        if base_type[0] == "Array":
            member_type = base_type[1][0]
            retv = [member_type, base_name_value[3][member]]

        # handle structs
        else:
            debug(f"__ref_member__():  handling struct")

            struct_name_value = eval.get_name_value(base_type, scope)
            for member_index, struct_member in enumerate(struct_name_value[3][0]):
                debug(f"__ref_member__():  member_index: {member_index} - struct_member: {struct_member}")

                member_name, member_type = struct_member
                if member_name == member:
                    break

            member_value = base_name_value[3][member_index]
            debug(f"__ref_member__():  member_value: {member_value}")

            def _seek(mv, mt):
                debug(f"_seek(): mv: {mv} mt: {mt}")

                # check if member value isn't a name
                member_value_name_value = eval.get_name_value(mv, scope)
                debug(f"_seek():  member_value_name_value: {member_value_name_value}")
                if member_value_name_value == []:
                    debug(f"_seek():  returning [mt, mv]")
                    return [mt, mv]

                # member value is name...

                member_value_type = member_value_name_value[2]
                member_value_value = member_value_name_value[3]
                member_value_type_name_value = eval.get_name_value(member_value_type, scope)
                debug(f"_seek():  member_value_type_name_value: {member_value_type_name_value}")

                if member_value_type_name_value[2] == "struct":
                    return [member_value_type, member_value_value]

            seek_result = _seek(member_value, member_type)
            debug(f"__ref_member__():  seek_result: {seek_result}")

            # retv = [member_type, member_value]
            retv = seek_result

    else:
        debug(f"__ref_member__():  frontend compiletime - deep member access - base: {base}")
        evalret = eval.eval(base, scope)
        debug(f"__ref_member__():  frontend compiletime - evalret: {evalret} - member: {member}")

        evalret_type, evalret_value = evalret

        evalret_type_name_value = eval.get_name_value(evalret_type, scope)
        debug(f"__ref_member__():  frontend compiletime - evalret_type_name_value: {evalret_type_name_value}")
        index = None
        type_ = None

        for evalret_type_member_index, evalret_type_member in enumerate(evalret_type_name_value[3][0]):
            debug(f"__ref_member__():  frontend compiletime - evalret_type_member_index: {evalret_type_member_index}")
            debug(f"__ref_member__():  frontend compiletime - evalret_type_member: {evalret_type_member}")
            if evalret_type_member[0] == member:
                index = evalret_type_member_index
                type_ = evalret_type_member[1]
                break

        if index is None:
            raise Exception(f"Couldn't find member {member} in {evalret_type}")

        debug(f"__ref_member__():  frontend compiletime - candidate: {evalret_type_name_value[3][0][index]}")
        debug(f"__ref_member__():  frontend compiletime - candidate: {evalret_value[index]}")

        struct_names = eval.get_type_values("struct", scope)
        structs = [s[0] for s in struct_names]
        debug(f"__ref_member__():  frontend compiletime - structs: {structs}")

        # handle structs
        if evalret_type_name_value[3][0][index][1] in structs:
            debug(f"__ref_member__():  frontend compiletime - struct member value is struct")

            structref = evalret_value[index]
            debug(f"__ref_member__():  frontend compiletime - structref: {structref}")

            structref_name_value = eval.get_name_value(structref, scope)
            if structref_name_value == []:
                raise Exception(f"Invalid reference to struct in struct member value: {structref}")

            retv = structref_name_value[2:]

        else:
            retv = [type_, evalret_value[index]]

        return retv

    debug(f"__ref_member__():  retv: {retv}")

    return retv


def validate_ref_member(node, scope):

    # TODO: check node length
    # TODO: check for base type

    pass
#
#


# ARRAY INTERNALS
#
def __set_array_member__(node, scope):
    validate_set_array_member(node, scope)

    return []


def validate_set_array_member(node, scope):
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for set_array_member: {node}")


def __get_array_member__(node, scope):
    validate_get_array_member(node, scope)

    return []


def validate_get_array_member(node, scope):
    if len(node) != 3:
        raise Exception("Wrong number of arguments for get_array_member: {node}")


def __ref_array_member__(node, scope):
    debug(f"__ref_array_member__():  frontend compiletime - node: {node}")

    ref_array_member, array_base, array_index = node

    debug(f"__ref_array_member__():  frontend compiletime - array_base: {array_base}")

    if isinstance(array_base, list):
        debug(f"__ref_array_member__():  frontend compiletime - array_base is list")

        def iter_is_list(value):
            debug(f"iter_is_list():  value: {value}")

            if len(value) > 0 and value[0] == "ref_array_member":
                debug(f"iter_is_list():  ref_array_member!")

                value_ = eval.get_name_value(value[1], scope)
                debug(f"iter_is_list():  value_: {value_}")

                retv = [False]

                balue_type = value_[2]
                balue_balue = value_[3]

                debug(f"iter_is_list():  balue_type: {balue_type}")
                debug(f"iter_is_list():  balue_balue: {balue_balue}")

                katapimbas = []
                for wer in balue_balue:
                    zxcc = iter_is_list(wer)
                    debug(f"iter_is_list():  zxcc: {zxcc}")

                    katapimbas.append(zxcc)

                debug(f"iter_is_list():  katapimbas: {katapimbas}")

                mir = katapimbas[0][1]

                mir_T = mir[0]
                mir_V = mir[int(array_index) + 1]

                debug(f"iter_is_list():  mir: {mir}")

                retv.append([mir_T[1], mir_V])

                return retv

            else:
                debug(f"iter_is_list():  not ref_array_member!")

                value_ = eval.get_name_value(value, scope)
                debug(f"iter_is_list():  value_: {value_}")

                if value_ != []:
                    debug(f"iter_is_list():  value_ found!")

                    type_ = value_[2]
                    debug(f"iter_is_list():  type_: {type_}")

                    if isinstance(type_, list) and value_[2][0] == "Array":

                        retv = []
                        for item in value_[3]:
                            iter_result = iter_is_list(item)
                            retv.append(iter_result)

                        debug(f"iter_is_list():  retv: {retv}")

                        all_not_found_values = all([i[0] == False for i in retv])
                        debug(f"iter_is_list():  all_not_found_values: {all_not_found_values}")

                        if all_not_found_values:
                            retv = [True, [type_] + [i[1] for i in retv]]

                        else:
                            retv = [True, retv[0][1]]

                        return retv

                else:
                    debug(f"iter_is_list():  value_ not found! {value}")
                    return [False, value]

        iter_value = array_base[1]
        debug(f"__ref_array_member__():  frontned compiletime - iter_value: {iter_value}")

        iter_result = iter_is_list(iter_value)[1]
        debug(f"__ref_array_member__():  frontend compiletime - iter_result: {iter_result}")

        type_ = iter_result[0]
        value = iter_result[1:]

        retv = [type_] + value

#
#        array_base_value = eval.get_name_value(array_base[1], scope)
#        debug(f"__ref_array_member__():  frontend compiletime - array_base_value: {array_base_value}")
#
#        for item in array_base_value[3]:
#            debug(f"__ref_array_member__():  item: {item}")
#
#            item_name_value = eval.get_name_value(item, scope)
#            if item_name_value == []:
#                raise Exception(f"Unassigned array value: {item}")
#
#            debug(f"__ref_array_member__():  item_name_value: {item_name_value}")
#
#            item_type, item_value = item_name_value[2:]
#
#            # handle composite types
#            if isinstance(item_type, list):
#                type_ = item_type[1]
#                value = item_value[int(array_index)]
#
#            # handle simple types
#            else:
#                raise Exception("Not implemented!")
#                type_ = 'MWER'
#                value = 'MWER!'
#
#            debug(f"__ref_array_member__():  type_: {type_} value: {value}")

    else:
        debug(f"__ref_array_member__():  frontend compiletime - array_base isn't list")

        def iter_isnt_list(value, original_type=None):
            debug(f"iter_isnt_list():  start - value: {value}")

            abc_value = eval.get_name_value(value, scope)
            otwasnone = original_type is None

            if abc_value != []:
                debug(f"iter_isnt_list():  abc_value found! abc_value: {abc_value}")

                type_ = abc_value[2][1]
                if otwasnone:
                    original_type = type_

                debug(f"iter_isnt_list():  type_: {type_}")

                if isinstance(type_, list) and type_[0] == "Array":
                    debug(f"iter_isnt_list():  type_ is Array")

                    new_value = abc_value[3]
                    debug(f"iter_isnt_list():  new_value: {new_value}")

                    retv = []
                    for array_member in new_value:
                        iter_isnt_list_result = iter_isnt_list(array_member, original_type)
                        debug(f"iter_isnt_list():  iter_isnt_list_result: {iter_isnt_list_result}")
                        retv.append(iter_isnt_list_result)

                else:
                    debug(f"iter_isnt_list():  type_ isn't Array")
                    retv = abc_value[3]

                if otwasnone:
                    retv = [original_type, retv[int(array_index)][0]]

                debug(f"iter_isnt_list():  retv: {retv}")
                return retv

            else:
                debug(f"iter_isnt_list():  abc_value not found!")
                raise Exception("abc_value not found!")

#        type_, value = iter_isnt_list(array_base)
        retv = iter_isnt_list(array_base)

#        array_base_value = eval.get_name_value(array_base, scope)
#        debug(f"__ref_array_member__():  frontend compiletime - array_base_value: {array_base_value}")
#
#        type_ = array_base_value[2][1]
#        debug(f"__ref_array_member__():  frontend compiletime - type_: {type_}")
#
#        # handle arrays
#        if isinstance(type_, list) and type_[0] == "Array":
#
#            value = array_base_value[3][int(array_index)]
#            debug(f"__ref_array_member():  frontend compiletime - value: {value}")
#
#            value_name_value = eval.get_name_value(value, scope)
#            debug(f"__ref_array_member__():  frontend compiletime - value_name_value: {value_name_value}")
#
#            if value_name_value != []:
#                new_type, new_value = value_name_value[2:]
#                value = [new_type]
#                value += new_value
#
#                debug(f"__ref_array_member__():  frontend compiletime - new value: {value}")
#
#                return value
#
#            else:
#                pass
#
#        else:
#            debug(f"__ref_array_member__():  frontend compiletime - type_ isn't Array")
#            value = array_base_value[3][int(array_index)]

#    retv = [type_, value]
    debug(f"__ref_array_member__():  frontend compiletime - retv: {retv}")

    return retv
#
#


# STRUCT INTERNALS
#
def __set_struct_member__(node, scope):
    validate_set_struct_member(node, scope)

    get_struct_member_, struct_name, struct_member, value = node

    struct_name_value = eval.get_name_value(struct_name, scope)
    struct_type = struct_name_value[2]

    struct_type_value = eval.get_name_value(struct_type, scope)
    for struct_type_member in struct_type_value[3]:
        debug(f"__set_struct_member__():  member: {member}")
        if struct_type_member[1] == struct_member:
            debug(f"__set_struct_member__():  member match: {member}")
            break

    member_type = struct_type_member[0]

    for member_index, member in enumerate(struct_name_value[3]):
        if member[0] == struct_member:
            struct_name_value[3][member_index] = [struct_member, member_type, value]
            debug(f"__set_struct_member__():  new member value: {struct_name_value[3][member_index]}")
            break

    return []


def validate_set_struct_member(node, scope):
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for set_struct_member: {node}")


def __get_struct_member__(node, scope):
    validate_get_struct_member(node, scope)

    get_struct_member_, struct_name, struct_member = node

    struct_name_value = eval.get_name_value(struct_name, scope)
    struct_type = struct_name_value[2]

    struct_type_value = eval.get_name_value(struct_type, scope)
    member_type = None
    for member_index, struct_type_member in enumerate(struct_type_value[3]):
        debug(f"__get_struct_member__():  struct_type_member: {struct_type_member}")
        if struct_type_member[0] == struct_member:
            # debug(f"__get_struct_member__():  member match: {member}")
            member_type = struct_type_member[1]
            break

    member_value = struct_name_value[3][member_index]

    retv = [member_type, member_value]
    debug(f"__get_struct_member__():  retv: {retv}")

    return retv


def validate_get_struct_member(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for get_struct_member: {node}")

    get_struct_member_, struct_name, struct_member = node

    struct_name_value = eval.get_name_value(struct_name, scope)
    if struct_name_value == []:
        raise Exception(f"Unassigned name: {struct_name}")
#
#


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
    ["set_array_member", "mut", "internal", __set_array_member__],
    ["get_array_member", "mut", "internal", __get_array_member__],
    ["set_struct_member", "mut", "internal", __set_struct_member__],
    ["get_struct_member", "mut", "internal", __get_struct_member__],

    ["ref_member", "mut", "internal", __ref_member__],
    ["ref_array_member", "mut", "internal", __ref_array_member__],

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
scope["step"] = "frontend"
