import re

from shared import debug


default_scope = {
    "names": [],
    "macros": [],
    "parent": None,
    "children": [],
    "safe": True,
    "step": None,

    "return_call": None,
    "return_call_common_list": None,
    "return_call_common_not_list": None,

    "is_last": False,
    "function_depth": 0,
}


def eval(li, scope):
    debug(f"""\neval():  {scope["step"]} - li: {li}""")

    new_li = li.copy()

    new_li = _eval_handle_macros(new_li, scope)

    debug(f"eval():  macro expanded li: {new_li}")

    # if the list is empty, return it
    if len(new_li) == 0:
        debug(f"eval():  exiting eval, empty list {new_li}")
        return new_li

    is_list = isinstance(new_li[0], list)
    if is_list:
        new_li = _eval_handle_list(new_li, scope)

    else:
        new_li = _eval_handle_not_list(new_li, scope)

    debug(f"""eval():  exiting {scope["step"]}: {li}  ->  {new_li}""")

    return new_li


def _eval_handle_macros(li, scope):

    if len(scope["macros"]):
        expand = True
        new_li = li.copy()

        # expand macros until there are no more macros to expand
        while expand:
            debug(f"_eval_handle_macros():  will try to expand macros in {new_li}")

            new_li, found_macro = _expand_macro(new_li, scope)

            debug(f"_eval_handle_macros():  new_li: {new_li} found_macro: {found_macro}")

            expand = found_macro

        debug(f"_eval_handle_macros():  expansion ended - new_li: {new_li}")

        return new_li

    else:
        return li


def _eval_handle_list(li, scope):
    debug(f"_eval_handle_list():  li: {li}")
    evaled_li = []

    for key, item in enumerate(li):
        debug(f"_eval_handle_list():  li item: {item}")

        # check for last item in list
        scope["is_last"] = key == (len(li) - 1)

        evaluated_list_ = eval(item, scope)
        if len(evaluated_list_) > 0:
            evaled_li.append(evaluated_list_)

    debug(f"_eval_handle_list():  {li} -> {evaled_li}")

    return evaled_li


def _eval_handle_not_list(li, scope):
    debug(f"_eval_handle_not_list():  li: {li}")

    # get name value from scope
    name_match = get_name_value(li[0], scope)
    if name_match == []:
        raise Exception(f"Unassigned name: {li[0]}")

    # elif len(name_matches) > 1:
    #    raise Exception(f"More than one name set, it's a bug! {li[0]}")
    struct_values = get_type_values("struct", scope)
    debug(f"_eval_handle_not_list():  struct_values: {struct_values}")

    structs = [s[0] for s in struct_values]
    debug(f"_eval_handle_not_list():  structs: {structs}")

    if name_match[2] in ["fn", "internal"]:
        debug(f"_eval_handle_not_list():  li calls fn/internal - name_match: {name_match}")
        li = _eval_handle_fn_internal(li, scope, name_match)

    elif name_match[2] in structs:
        debug(f"_eval_handle_not_list():  struct - name_match: {name_match}")
        li = _eval_handle_structs(li, scope, name_match)

    elif name_match[2][0] == "Array":
        debug(f"_eval_handle_not_list():  Array - name_match: {name_match}")
        li = _eval_handle_arrays(li, scope, name_match)

    else:
        debug(f"_eval_handle_not_list():  not function nor internal: {li}")

        if len(li) == 1:
            li = _eval_handle_common(li, scope, name_match)
        else:
            # li = _eval_handle_struct_members(li, scope, name_match)
            raise Exception("Handle struct members?")

    return li


def _eval_handle_fn_internal(li, scope, name_match):
    # if len == 1 it's a reference
    if len(li) == 1:
        li = name_match

    # if len > 1 it's a function call
    else:
        if name_match[2] == "fn":
            debug(f"eval():  name_match is function - name_match: {name_match}")

            retv = _call_fn(li, name_match, scope)
            debug(f"eval():  retv: {retv}")

            li = retv

        elif name_match[2] == "internal":
            debug(f"eval():  name_match is internal - name_match: {name_match}")

            li = name_match[3](li, scope)

        debug(f"eval():  internal result li: {li}")

    return li


def _eval_handle_structs(li, scope, name_match):
    debug(f"_eval_handle_structs():  li: {li} name_match: {name_match}")

    return name_match[2:]


def _eval_handle_common(li, scope, name_match):
    debug(f"_eval_handle_common():  name_match: {name_match}")

    # if is list of single item
    # if len(li) == 1:
    debug(f"_eval_handle_common():  list of single item")

    name_match_type = name_match[2]
    debug(f"_eval_handle_common():  name_match_type: {name_match_type}")

    name_match_value = name_match[3]
    debug(f"_eval_handle_common():  name_match_value: {name_match_value}")

    # if name match value is list
    if isinstance(name_match_value, list):
        debug(f"_eval_handle_common():  name_match_value is list")

        # evaluate the list
        debug(f"_eval_handle_common():  evaluating list: {name_match[3]}")
        evaled_name_match_value = eval(name_match_value, scope)
        method_type = evaled_name_match_value[0]

        # if return_calls is set, get correct method type
        return_calls = scope["return_call"] is not None
        if return_calls:
            if not callable(scope["return_call_common_list"]):
                raise Exception(f"""return_call_common_list not callable: {scope["return_call_common_list"]}""")

            li = scope["return_call_common_list"](evaled_name_match_value, name_match, scope)

        else:
            if name_match[2] != method_type:
                raise Exception(f"Name and evaluated value types are different - name_match type: {name_match[2]} - method_type: {method_type}")

            li = evaled_name_match_value

    else:
        debug(f"_eval_handle_common():  name_match_value isn't list")

        return_call_common_not_list = scope["return_call_common_not_list"] is not None
        if return_call_common_not_list:
            if not callable(scope["return_call_common_not_list"]):
                raise Exception(f"""return_call_common_not_list not callable: {scope["return_call_common"]}""")

            li = scope["return_call_common_not_list"](name_match, scope)

        else:
            li = name_match[2:]

    # else:
    #    debug(f"_eval_handle_common():  struct member li: {li}")
    #
    #    if li != []:
    #        debug(f"_eval_handle_common():  struct member li not empty: {li}")
    #
    #    # li = _get_struct_member(li, scope)

    return li


def _eval_handle_struct_member(li, scope, name_match):
    debug(f"_eval_handle_struct_member():  li: {li} name_match: {name_match}")
    return ['NYA']


def _eval_handle_arrays(li, scope, name_match):
    debug(f"_eval_handle_arrays():  li: {li}")

    type_, value = name_match[2:]
    debug(f"_eval_handle_arrays():  type_: {type_} value: {value}")

#    new_li = [type_]
#
#    for value_item in value:
#        debug(f"_eval_handle_arrays():  value_item: {value_item}")
#
#        value_name_value = get_name_value(value_item, scope)
#        debug(f"_eval_handle_arrays():  value_name_value: {value_name_value}")
#
#        if value_name_value != []:
#            to_append = [value_name_value[3]][0]
#
#        else:
#            to_append = value_item
#
#        debug(f"_eval_handle_arrays():  to_append: {to_append}")
#
#        new_li.append(to_append)
#
#    debug(f"_eval_handle_arrays(): new_li: {new_li}")

    # iter down arrays solving array references

    def iter(value):
        debug(f"iter():  start - value: {value}")

        retv = []

        # for each item in value
        for abc in value:
            debug(f"iter():  abc: {abc}")

            # if it's a list, iter() over it
            if isinstance(abc, list):
                abc_list_result = iter(abc)
                debug(f"iter():  appending to retv - abc_list_result: {abc_list_result}")

                retv.append(abc_list_result)
                debug(f"iter():  new retv: {retv}")

            # if it's not a list, try to get name value
            else:
                abc_value = get_name_value(abc, scope)
                debug(f"iter():  abc_value: {abc_value}")
                # abc_fixed_value = abc_value[2:]
                # debug(f"iter():  abc_fixed_value: {abc_fixed_value}")

                # if found name value
                if abc_value != []:
                    debug(f"iter():  abc_value found! {abc_value[3][0]}")

                    # if name value is an Array
                    if abc_value[2][0] == "Array":
                        abc_array = iter(abc_value[3])
                        debug(f"iter():  adding to retv - abc_array: {abc_array}")

                        # return abc_array
                        retv.append(abc_array)
                        debug(f"iter():  new retv: {retv}")

                    else:
                        retv.append(abc_value)

                # if didn't found name value
                else:
                    debug(f"iter():  abc_value not found!")
                    # return value
                    retv.append(abc)

        debug(f"iter():  end - retv: {retv}")

        return retv

    return [type_] + iter(value)

#    return new_li


def _call_fn(li, fn, scope):
    debug(f"_call_fn():  li: {li} fn: {fn}")
    name = fn[0]
    methods = fn[3]
    candidates = []

    found_method, solved_arguments = find_function_method(li, fn, scope)

    debug(f"_call_fn():  found_method: {found_method} - solved_arguments: {solved_arguments}")
    # print(f"solved_arguments: {solved_arguments}")

    # set new scope
    import copy
    fn_scope = copy.deepcopy(default_scope)
    fn_scope["parent"] = scope  # parent scope
    fn_scope["safe"] = scope["safe"]  # handler descriptor
    fn_scope["step"] = scope["step"]  # backend scope

    # populate new scope's names with function call arguments
    if li[1:] != [[]]:

        debug(f"_call_fn():  solved_arguments: {solved_arguments}")

        # for arg_i, arg in enumerate(li[1:]):
        for arg_i, arg in enumerate(solved_arguments):
            debug(f"_call_fn():  arg_i: {arg_i} arg: {arg} found_method[0]: {found_method[0]}")

            if scope["step"] == "backend":
                method_arg = found_method[0][0][arg_i]
                arg = arg[0]
            elif scope["step"] == "frontend":
                method_arg = found_method[0][arg_i]

            debug(f"_call_fn():  method_arg: {method_arg}")

            to_append = [method_arg[0], "const", method_arg[1], arg[1]]

            debug(f"_call_fn():  to_append: {to_append}")

            fn_scope["names"].append(to_append)

    #    debug(f"fn_scope: {fn_scope}")

    return_calls = scope["return_call"] is not None

    debug(f"_call_fn():  return_calls: {return_calls}")

    # check for functions without return value
    if len(found_method) == 2:
        if return_calls:
            return_call_function = scope["return_call"]

            debug(f"_call_fn():  calling return_call() - li: {li}")

            value, stack = return_call_function(li, scope)
            value = f"\t\t{value}"

            debug(f"_call_fn():  result return_call() - value: {value}  stack: {stack}")

            # stack.append(value)
            # return stack + [value]
            result = stack + [value]
            # result = value
            return result
        else:
            # print(f"not return_calls []")
            return []

    return_value = eval(found_method[2], fn_scope)

    # return calls if we need the call output
    if return_calls:
        debug(f"returning call _call_fn {li}")
        return_value = li

    else:
        # if returned value isn't empty list
        if len(return_value) > 0:
            return_value = return_value[0]

            # if returned value type is different from called function type
            if (not isinstance(return_value[0], list) and return_value[0] != found_method[1]):
                raise Exception(f"""Returned value type of function is different from called function type:
    return_value: {return_value}

    found_method[1]: {found_method[1]}

    return_value[0]: {return_value[0]}""")

    debug(f"_call_fn:  exiting {li} -> {return_value}")

    return return_value


def find_function_method(li, fn, scope):
    """
    li    - the list calling the function
    fn    - the function name
    scope - scope list
    """

    debug(f"find_function_method():  li: {li} fn: {fn}")

    name = fn[0]
    methods = fn[3]
    candidates = []

    debug(f"find_function_method():  methods: {methods}")

    solved_arguments = []

    for method in methods:
        debug(f"find_function_method():  method: {method}")

        # clean solved_arguments from previous functions
        solved_arguments = []

        # match types
        match = True
        for arg_i, arg in enumerate(li[1:]):
            debug(f"find_function_method():  argument - arg_i: {arg_i} arg: {arg}")

            # break in methods without the arguments
            if scope["step"] == "backend":
                m0 = method[0][0]
            elif scope["step"] == "frontend":
                m0 = method[0]

            if len(m0) < arg_i + 1 and not (len(m0) == 0 and len(li[1:]) == 1 and li[1] == []):
                debug(f"find_function_method():  not matching - len(m0) < arg_i + 1")

                match = False
                break

            # solve argument
            #
            solved_argument = None

            # check if argument is a list
            is_list = isinstance(arg, list)

            # if it's a list
            if is_list:
                debug(f"find_function_method():  is_list: {is_list} arg: {arg} m0: {m0}")
                debug(f"""find_function_method():  is backend scope: {scope["step"] == "backend"}""")

                # if it's calling a function without arguments with a single empty list as argument
                if len(arg) == 0 and len(method[0]) == 0:
                    continue

                # if it's a backend scope
                if scope["step"] == "backend":
                    debug(f"find_function_method():  backend scope")

                    # get name value
                    name_value = get_name_value(arg[0], scope)
                    debug(f"find_function_method():  name_value: {name_value}")

                    # if found name value
                    if len(name_value) > 0:

                        #                        # handle functions
                        #                        if name_value[2] == "fn":
                        debug(f"find_function_method():  handling function")

                        # find function method for argument
                        debug(f"find_function_method():  calling find_function_method() now - arg: {arg}")

                        argument_method, argument_solved_arguments = find_function_method(arg, name_value, scope)
                        debug(f"find_function_method():  argument_method: {argument_method} argument_solved_arguments: {argument_solved_arguments}")

                        # set a dummy solved_argument just with the correct type
                        solved_argument = [argument_method[1], '?']

#                        # DIRTY: handle internals
#                        elif name_value[2] == "internal":
#                            debug(f"find_function_method():  handling internal")
#                            raise Exception(f"aAAA: {name_value}")
#
#                            if name_value[0] in ["get_ptr", "read_ptr", "write_ptr"]:
#                                debug(f"find_function_method():  ptr internals")
#
#                                fake_type = ["ptr"]
#                                target_name_value = get_name_value(arg[1], scope)
#
#                                if target_name_value[2][0] == "Array":
#                                    debug(f"find_function_method():  internal target_name_value is Array")
#
#                                    if len(target_name_value[2]) == 3:
#                                        if target_name_value[1] == "mut":
#                                            fake_type.append(["Array", target_name_value[2][1]])
#
#                                        elif target_name_value[1] == "const":
#                                            fake_type_append(["Array", target_name_value[1]])
#
#                                solved_argument = [fake_type, '?']

                    debug(f"find_function_method():  solved_argument: {solved_argument}")

                # if it's a frontend scope, eval argument
                elif scope["step"] == "frontend":
                    debug(f"find_function_method():  frontend scope")

                    # eval it
                    debug(f"find_function_method():  calling eval() to solve argument {arg}")

                    solved_argument = eval(arg, scope)

                debug(f"find_function_method(): list solved_argument: {solved_argument}")

            # if it's not a list
            else:
                debug(f"find_function_method():  argument {arg} isn't a list")

                # get name value
                name_value = get_name_value(arg, scope)
                debug(f"find_function_method():  name_value: {name_value} arg: {arg}")
                debug(f"""find_function_method():  names: {[i[0] for i in scope["names"]]}""")
                debug(f"""find_function_method():  scope["names"]: {scope["names"]}""")

                found_value = list(name_value[2:]) != []

                debug(f"find_function_method():  found_value: {found_value}")

                # if found value, set solved_argument with the value
                if found_value:
                    tmp_solved_argument = name_value[2:]
                    solved_argument = [tmp_solved_argument[0]] + tmp_solved_argument[1]

                    # handle composite types
                    if isinstance(solved_argument[0], list):
                        if solved_argument[0][0] == "Array" and solved_argument[1] == "unset":
                            solved_argument = [solved_argument[0].copy()]
                            solved_argument[0].pop(2)

                # if value not found, try to infer type of argument
                else:
                    solved_argument = _infer_type(arg)

                    if solved_argument is None:
                        raise Exception(f"Unassigned name: {arg}")
            #
            #

            if solved_argument is None:
                debug(f"find_function_method():  not matching - solved_argument is None")

                match = False
                break

            debug(f"find_function_method():  solved_argument: {solved_argument}")
            solved_arguments.append(solved_argument)

            if len(solved_argument) == 0:
                debug("find_function_method():  len(sorved_arg) == 0")
                pass

            else:
                debug(f"find_function_method():  argument was solved")
                debug(f"find_function_method():  method: {method}")
                debug(f"find_function_method():  m0[arg_i]: {m0[arg_i]} - arg_i: {arg_i}")

                # get the type of the method argument

                if len(m0[arg_i]) == 2:
                    method_argument_type = m0[arg_i][1]
                elif len(m0[arg_i]) == 3 and m0[arg_i][1] == "mut":
                    method_argument_type = m0[arg_i][2]

                debug(f"find_function_method():  method_argument_type: {method_argument_type}")

                # if the type of the solved argument is different from the type of the method argument, don't match
                if solved_argument[0] != method_argument_type:
                    debug(f"find_function_method():  not matching - solved_argument[0] != method_argument_type - {solved_argument[0]} != {method_argument_type}")

                    match = False
                    break

        if match:
            debug(f"find_function_method():  matching - appending to candidates: {method}")
            candidates.append(method)

    if len(candidates) == 0:
        functions = [n for n in scope["names"] if n[2] == "fn"]
        raise Exception(f"No candidate function found - name: {name}  -  functions: {functions}  - li: {li} - solved_arguments: {solved_arguments}")
    if len(candidates) > 1:
        raise Exception(f"Method candidates mismatch: {name} {candidates}")

    debug(f"find_function_method():  candidates: {candidates}")

    found_method = candidates[0]

    debug(f"find_function_method():  exitting - li: {li} -> found_method: {found_method} solved_arguments: {solved_arguments}\n")

    return (found_method, solved_arguments)


def get_name_value(name, scope):
    debug(f"get_name_value()  - name: {name}")

    def iterup(scope):
        for each_name in scope["names"]:
            debug(f"get_name_value()  - each_name: {each_name}")

            if each_name[0] == name:
                return each_name  # list(n[2:])

        # didn't return found value...

        # if has parent scope, iterup
        if scope["parent"] is not None:
            return iterup(scope["parent"])
        # else, return empty list
        else:
            return []

    return iterup(scope)


def get_type_values(type_, scope):
    debug(f"get_type_values():  type_: {type_}")

    type_values = []

    def iterup(scope):
        for each_name in scope["names"]:
            debug(f"get_type_values():  each_name: {each_name}")

            if each_name[2] == type_:
                debug(f"get_type_values():  appending {each_name} to type_values")
                type_values.append(each_name)

        if scope["parent"] is not None:
            iterup(scope["parent"])

    iterup(scope)

    return type_values


def _infer_type(arg):
    #    debug(f"_infer_type():  arg: {arg}")

    candidates = []

    # match base 10 integers
    int_regexp = "[0-9]+"
    m = re.match(int_regexp, arg)
    if m:
        candidates.append([m, "int"])

    # match heaxdecimal integers
    hex_int_regexp = "0x[0-9]+"
    m = re.match(hex_int_regexp, arg)
    if m:
        candidates.append([int(m), "int"])

    # match floating points
    float_regexp = "[0-9]+\\.[0-9]+"
    m = re.match(float_regexp, arg)
    if m:
        candidates.append([m, "float"])

    # match booleans
    bool_regexp = "true|false"
    m = re.match(bool_regexp, arg)
    if m:
        candidates.append([m, "bool"])

    # get biggest match
    biggest = None
    for c in candidates:
        if biggest is None:
            biggest = c
        else:
            if len(c[0].group()) > len(biggest[0].group()):
                biggest = c

            elif len(c[0].group()) == len(biggest[0].group()):
                raise Exception("Two candidates with same size!")

    # return according to biggest match
    if biggest is None:
        return None

    return [biggest[1], arg]


def _expand_macro(li, scope):
    # print(f"_expand_macro: {li}")

    new_li = li.copy()
    found_macro = False

    # for each item in li
    for index, item in enumerate(li):
        # print(f"LI index: {index} item: {item}")

        if isinstance(item, list):
            sub_found_macro = True
            while sub_found_macro:
                sub_new_li, sub_found_macro = _expand_macro(item, scope)
                if sub_found_macro:
                    # print(f"sub_found_macro! {item} -> {sub_new_li}")
                    item = sub_new_li
                    li[index] = sub_new_li

        found_macro = False
        for macro in scope["macros"]:
            # print(f"macro: {macro}")

            found_macro, full_match, bindings = match_macro(li, index, macro)
            # print(f"match_macro > {new_li} {found_macro}")

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

    return_value = [new_li, found_macro]
    # print(f"_expand_macro - return_value: {return_value}")
    return return_value


def match_macro(li, index, macro):
    # print(f"match_macro - li: {li} index: {index} macro: {macro}")

    alias, syntax, extended = macro

    # li_piece = li[index : index+len(syntax)]
    li_piece = li[index:]
    bindings = []

    full_match = False
    for cur_index, cur in enumerate(li_piece):
        # print(f"cur {cur_index} {cur}")

        #        if type(cur) == list:
        #            #print(f"cur is list! {cur}")
        #            result = match_macro(cur, 0, macro)
        #            print(f"result: {result}")

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


# def _get_struct_member(li, scope):
#    debug(f"_get_struct_member:  li: {li}")
#
#    def myfn(n, index):
#        new_li = n[3][index]
#
#        if len(li) > 2:
#            return _get_struct_member([new_li] + li[2:], scope)
#        else:
#            # print(f"n: {n}")
#            # print(f"new_li: {new_li}")
#            matches = [name for name in scope["names"] if name[0] == n[2] and name[2] == "struct"]
#            # print(f"matches: {matches}")
#
#            # member_type = matches[0][3][index][1]
#            member = matches[0][3][index]
#            if len(member) == 3 and member[0] == "mut":
#                member_type = member[2]
#            else:
#                member_type = member[1]
#            # print(f"member_type: {member_type}")
#
#            result = [member_type, new_li]
#            # print(f"result: {result}")
#            return result
#
#    return _seek_struct_ref(li, scope, myfn)
#
#
# def _seek_struct_ref(li, scope, fn):
#    debug(f"_seek_struct_ref():  li: {li} fn: {fn}")
#
#    # seeks names matching with li[0]
#    name_matches = [n for n in scope["names"] if n[0] == li[0]]
#    n = name_matches[0]
#
#    # get possible struct name
#    struct_name = n[2]
#
#    # check if there's some struct set with this name
#    candidates = [s for s in scope["names"] if s[2] == "struct" and s[0] == struct_name]
#    # print(f"candidates: {candidates}")
#
#    # get the candidate struct
#    candidate = candidates[0]
#    # print(f"candidate: {candidate}")
#
#    # check if member name exists
#    member_name = li[1]
#    # print(f"member_name: {member_name}")
#
#    members_matches = []
#    for index, m in enumerate(candidate[3]):
#        if m[0] == "mut":
#            if m[1] == member_name:
#                members_matches.append((index, m))
#        elif m[0] == member_name:
#            members_matches.append((index, m))
#
#    # members_matches = [(index, m) for index, m in enumerate(c[3]) if m[0] == member_name]
#
#    members_match = members_matches[0]
#    # print(f"members_match: {members_match}")
#
#    if len(members_match) == 0:
#        raise Exception(f"Struct {struct_name} has no member {member_name}")
#
#    # get value
#    # print(f"n: {n}")
#    index, m = members_match
#    # new_li = n[3][index]
#    return fn(n, index)
#
#
# def _seek_array_ref(li, scope, fn):
#    # seeks names matching with li[0]
#    name_matches = [n for n in scope["names"] if n[0] == li[0]]
#    n = name_matches[0]
#
#    # get possible array_type
#    array_type = n[2]
#
#    # check if there's some struct set with this name
#    candidates = [s for s in scope["names"] if s[2] == array_type]  # type(s[2]) == list and s[2][0] == "Array" ] #and s[0] == struct_name]
#    debug(f"candidates: {candidates}")
#
#    # get the candidate struct
#    candidate = candidates[0]
#
#    debug(f"_seek_array_ref():  candidate: {candidate}")
#
#    index = int(li[1])
#
#    return fn(n, index)


def get_global_scope(scope):

    def iter(scope):
        if scope["parent"] is None:
            return scope
        else:
            return iter(scope["parent"])

    return iter(scope)


def is_global_name(name, scope):
    global_scope = get_global_scope(scope)

    debug(f"""is_global_name():  name: {name} global_scope["names"]:{global_scope["names"]}""")
    return (name in global_scope["names"])
