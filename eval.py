import re

from shared import debug


# default scope is given for creating copies
# default_scope = [
#    [],    # 0 names
#    [],    # 1 macros
#    None,  # 2 parent scope
#    [],    # 3 children scopes
#    True,  # 4 is safe scope
#    None,  # 5 forced handler
#    None,  # 6 eval returns calls
#    False,  # 7 backend scope
# ]
default_scope = {
    "names": [],
    "macros": [],
    "parent": None,
    "children": [],
    "safe": True,
    "forced_handler": None,
    "return_call": None,
    "backend_scope": False,
    "is_last": False,
    "function_depth": 0
}


def eval(li, scope):
    is_backend_scope = scope["backend_scope"] == True
    end_str = "backend" if is_backend_scope else "frontend"

    debug(f"""\neval():  {end_str} - li: {li}""")
    # print(f"\neval {li} {scope}")

    old_li = li

    # expand macros until there are no more macros to expand
    new_li = None
    macros = scope["macros"]

    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            debug(f"eval():  will try to expand macros in {new_li}")

            new_li, found_macro = _expand_macro(new_li, scope)

            debug(f"eval():  new_li: {new_li} found_macro: {found_macro}")

            expand = found_macro

        debug(f"eval():  expansion ended - new_li: {new_li}")

        li = new_li

    debug(f"eval():  macro expanded li: {li}")

    # if the list is empty, return it
    if len(li) == 0:
        debug(f"eval():  exiting eval {li}")

        return li

    is_list = isinstance(li[0], list)
    if is_list:
        debug(f"eval():  is_list - li: {li}")
        evaled_li = []
        for key, item in enumerate(li):
            debug(f"eval():  li item: {item}")

            # check for last item in list
            scope["is_last"] = key == (len(li) - 1)

            evaluated_list_ = eval(item, scope)
            if len(evaluated_list_) > 0:
                evaled_li.append(evaluated_list_)

        li = evaled_li
        debug(f"evaled_li: {evaled_li}")

    else:
        # get name value from scope
        name_match = get_name_value(li[0], scope)

        # check name_matches size
        if name_match == []:
            raise Exception(f"Unassigned name: {li[0]}")

        # elif len(name_matches) > 1:
        #    raise Exception(f"More than one name set, it's a bug! {li[0]}")

        if name_match[2] in ["fn", "internal"]:
            debug(f"eval():  li calls fn/internal - name_match: {name_match}")

            # len == 1, so it's a reference
            if len(li) == 1:
                # print(f"fn ref {li}")
                li = name_match

            # len > 1, so it's a function call
            else:
                if name_match[2] == "fn":
                    debug(f"eval():  name_match is function - name_match: {name_match}")

                    retv = _call_fn(li, name_match, scope)

                    debug(f"eval():  retv: {retv}")

                    # if len(retv) == 2 and isinstance(retv[0], list) and isinstance(retv[1], list):
                    #    scope["forced_handler"] = retv[1]
                    #    retv = retv[0]

                    li = retv

                elif name_match[2] == "internal":
                    debug(f"eval():  name_match is internal - name_match: {name_match}")

                    li = name_match[3](li, scope)

                debug(f"eval():  internal result li: {li}")

        # not function nor internal
        else:
            debug(f"eval():  not function nor internal: {li}")

            # if is list of single item
            if len(li) == 1:
                debug(f"eval():  list of single item")
                name_match_value = name_match[3]
                debug(f"eval():  name_match_value: {name_match_value}")

                # if name match value is list
                if isinstance(name_match_value, list):
                    debug(f"eval():  name_match_value is list")

                    # evaluate the list
                    debug(f"eval():  evaluating list: {name_match[3]}")
                    evaled_name_match_value = eval(name_match_value, scope)
                    method_type = evaled_name_match_value[0]

                    # if return_calls is set, get correct method type
                    return_calls = scope["return_call"] is not None
                    if return_calls:
                        evaled_fn = get_name_value(evaled_name_match_value[0], scope)
                        method, solved_arguments = find_function_method(evaled_name_match_value, evaled_fn, scope)
                        method_type = method[1]

                    # if type of name match and type of list result are different
                    if name_match[2] != method_type:
                        raise Exception(f"Name and evaluated value types are different - name_match type: {name_match[2]} - method_type: {method_type}")

                    if return_calls:
                        # TODO: get correct return type and result name

                        # get type
                        type_return_call = "i64"

                        # get var name
                        name_return_call = "%result"

                        li = [f"\tret {type_return_call} {name_return_call}"]

                    else:
                        li = evaled_name_match_value

                else:
                    debug(f"eval():  name_match_value isn't list")

                    if scope["backend_scope"]:
                        debug(f"""eval():  backend scope - function_depth: {scope["function_depth"]} - is_last: {scope["is_last"]} - li: {li}""")

                        if scope["is_last"] and scope["function_depth"] == 1:
                            import backend.scope as bes
                            converted_type = bes._convert_type(name_match[2])
                            li = [f"\t\tret {converted_type} %{name_match[0]}"]

                        else:
                            li = ["\t\t; NOT IMPLEMENTED"]
                    else:
                        li = name_match[2:]

            else:
                debug(f"eval():  struct member li: {li}")
                li = _get_struct_member(li, scope)

    debug(f"eval():  exiting {end_str}: {old_li}  ->  {li}")

    return li


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
    fn_scope["backend_scope"] = scope["backend_scope"]  # backend scope

    # populate new scope's names with function call arguments
    if li[1:] != [[]]:

        debug(f"_call_fn():  solved_arguments: {solved_arguments}")

        # for arg_i, arg in enumerate(li[1:]):
        for arg_i, arg in enumerate(solved_arguments):
            debug(f"_call_fn():  arg_i: {arg_i} arg: {arg} found_method[0]: {found_method[0]}")

            if scope["backend_scope"]:
                method_arg = found_method[0][0][arg_i]
                arg = arg[0]
            else:
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
            if scope["backend_scope"]:
                m0 = method[0][0]
            else:
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
                debug(f"""find_function_method():  is backend scope: {scope["backend_scope"]}""")

                # if it's calling a function without arguments with a single empty list as argument
                if len(arg) == 0 and len(method[0]) == 0:
                    continue

                # if it's a backend scope
                if scope["backend_scope"] == True:
                    debug(f"find_function_method():  backend scope")

                    # get name value
                    name_value = get_name_value(arg[0], scope)
                    debug(f"find_function_method():  name_value: {name_value}")

                    # if found name value
                    if len(name_value) > 0:

                        # handle functions
                        if name_value[2] == "fn":
                            debug(f"find_function_method():  handling function")

                            # find function method for argument
                            debug(f"find_function_method():  calling find_function_method() now - arg: {arg}")

                            argument_method, argument_solved_arguments = find_function_method(arg, name_value, scope)
                            debug(f"find_function_method():  argument_method: {argument_method} argument_solved_arguments: {argument_solved_arguments}")

                            # set a dummy solved_argument just with the correct type
                            solved_argument = [argument_method[1], '?']

                        # handle internals
                        elif name_value[2] == "internal":
                            debug(f"find_function_method():  handling internal")

                            if name_value[0] in ["get_ptr", "read_ptr", "write_ptr"]:
                                debug(f"find_function_method():  ptr internals")

                                fake_type = ["ptr"]
                                target_name_value = get_name_value(arg[1], scope)

                                if target_name_value[2][0] == "Array":
                                    debug(f"find_function_method():  internal target_name_value is Array")

                                    if len(target_name_value[2]) == 3:
                                        if target_name_value[1] == "mut":
                                            fake_type.append(["Array", target_name_value[2][1]])

                                        elif target_name_value[1] == "const":
                                            fake_type_append(["Array", target_name_value[1]])

                                solved_argument = [fake_type, '?']

                        debug(f"find_function_method():  fn/internal solved_argument: {solved_argument}")

                # if it's a frontend scope, eval argument
                else:
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
                    solved_argument = name_value[2:]

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


def _get_struct_member(li, scope):
    debug(f"_get_struct_member:  li: {li}")

    def myfn(n, index):
        new_li = n[3][index]

        if len(li) > 2:
            return _get_struct_member([new_li] + li[2:], scope)
        else:
            # print(f"n: {n}")
            # print(f"new_li: {new_li}")
            matches = [name for name in scope["names"] if name[0] == n[2] and name[2] == "struct"]
            # print(f"matches: {matches}")

            # member_type = matches[0][3][index][1]
            member = matches[0][3][index]
            if len(member) == 3 and member[0] == "mut":
                member_type = member[2]
            else:
                member_type = member[1]
            # print(f"member_type: {member_type}")

            result = [member_type, new_li]
            # print(f"result: {result}")
            return result

    return _seek_struct_ref(li, scope, myfn)


def _seek_struct_ref(li, scope, fn):
    debug(f"_seek_struct_ref():  li: {li} fn: {fn}")

    # seeks names matching with li[0]
    name_matches = [n for n in scope["names"] if n[0] == li[0]]
    n = name_matches[0]

    # get possible struct name
    struct_name = n[2]

    # check if there's some struct set with this name
    candidates = [s for s in scope["names"] if s[2] == "struct" and s[0] == struct_name]
    # print(f"candidates: {candidates}")

    # get the candidate struct
    candidate = candidates[0]
    # print(f"candidate: {candidate}")

    # check if member name exists
    member_name = li[1]
    # print(f"member_name: {member_name}")

    members_matches = []
    for index, m in enumerate(candidate[3]):
        if m[0] == "mut":
            if m[1] == member_name:
                members_matches.append((index, m))
        elif m[0] == member_name:
            members_matches.append((index, m))

    # members_matches = [(index, m) for index, m in enumerate(c[3]) if m[0] == member_name]

    members_match = members_matches[0]
    # print(f"members_match: {members_match}")

    if len(members_match) == 0:
        raise Exception(f"Struct {struct_name} has no member {member_name}")

    # get value
    # print(f"n: {n}")
    index, m = members_match
    # new_li = n[3][index]
    return fn(n, index)


def _seek_array_ref(li, scope, fn):
    # seeks names matching with li[0]
    name_matches = [n for n in scope["names"] if n[0] == li[0]]
    n = name_matches[0]

    # get possible array_type
    array_type = n[2]

    # check if there's some struct set with this name
    candidates = [s for s in scope["names"] if s[2] == array_type]  # type(s[2]) == list and s[2][0] == "Array" ] #and s[0] == struct_name]
    debug(f"candidates: {candidates}")

    # get the candidate struct
    candidate = candidates[0]

    debug(f"_seek_array_ref():  candidate: {candidate}")

    index = int(li[1])

    return fn(n, index)


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
