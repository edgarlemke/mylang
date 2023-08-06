import re


# default scope is given for creating copies
default_scope = [
    [],    # names
    [],    # macros
    None,  # parent scope
    [],    # children scopes
    True,  # is safe scope
    None,  # forced handler
    None,  # eval returns calls
    False,  # backend scope
]


def eval(li, scope, forced_handler_desc=None):
    is_backend_scope = scope[7] == True
    end_str = "backend" if is_backend_scope else "frontend"
    # print(f"""\neval {end_str} - li: {li}""")
    # print(f"\neval {li} {scope}")

    old_li = li

    # expand macros until there are no more macros to expand
    new_li = None
    macros = scope[1]
    # print(f"macros: {macros}")
    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            # print(f"will try to expand macros in {new_li}")
            new_li, found_macro = _expand_macro(new_li, scope)
            # print(f"expand new_li: {new_li}")
            expand = found_macro

        # print(f"over new_li: {new_li}")

        li = new_li

    # print(f"macro expanded li: {li}")

    # if the list is empty, return it
    if len(li) == 0:
        # print(f"exiting eval {li}")
        return li

    # if there's a forced handler descriptor
    if forced_handler_desc is not None:
        # print(f"forced_handler_desc: {forced_handler_desc}")
        # if there's a forced handler set in scope but no handler
        if scope[5] is not None and li[0] != forced_handler_desc[0]:
            # panic
            raise Exception("Forced handler set but no handler")

    is_list = isinstance(li[0], list)
    if is_list:
        # print(f"li: {li}")
        evaled_li = []
        for key, item in enumerate(li):
            # li[key] = eval(item, scope)
            e = eval(item, scope, forced_handler_desc)
            if len(e) > 0:
                evaled_li.append(e)

        li = evaled_li
        # print(f"evaled_li: {evaled_li}")

        # check if li has evaled with forced handler in scope but no handler
        if forced_handler_desc is not None and scope[5] is not None:
            # panic
            raise Exception(f"Forced handler set in scope but no handler - forced handler: {scope[5]} - li: {li}")

    else:
        # get all names matching list's first value
        # name_matches = [n for n in scope[0] if n[0] == li[0]]
        name_match = _get_name_value(li[0], scope)
        # print(f"name_match: {name_match}")

        # check name_matches size
        if name_match == []:
            raise Exception(f"Unassigned name: {li[0]}")
        # elif len(name_matches) > 1:
        #    raise Exception(f"More than one name set, it's a bug! {li[0]}")

        if name_match[2] in ["fn", "internal"]:
            # print(f"fn/internal")
            # len == 1, so it's a reference
            if len(li) == 1:
                # print(f"fn ref {li}")
                li = name_match

            # len > 1, so it's a function call
            else:
                if name_match[2] == "fn":
                    # print("fn")
                    retv = _call_fn(li, name_match, scope)
                    # print(f"retv: {retv}")
                    if len(retv) == 2 and isinstance(retv[0], list) and isinstance(retv[1], list):
                        scope[5] = retv[1]
                        retv = retv[0]
                    li = retv
                elif name_match[2] == "internal":
                    # print(f"!!! internal")
                    x = name_match[3](li, scope)
                    li = x
                # print(f"li: {li}")

        # not function nor internal
        else:
            # if is list of single item
            if len(li) == 1:
                name_match_value = name_match[3]

                # if name match value is list
                if isinstance(name_match_value, list):

                    # evaluate the list
                    # print(f"evaling {name_match[3]}")
                    evaled_name_match_value = eval(name_match_value, scope, forced_handler_desc)
                    method_type = evaled_name_match_value[0]

                    # if return_calls is set, get correct method type
                    return_calls = scope[6] is not None
                    if return_calls:
                        evaled_fn = _get_name_value(evaled_name_match_value[0], scope)
                        method, solved_args = find_fn_method(evaled_name_match_value, evaled_fn, scope)
                        method_type = method[1]

                    # if type of name match and type of list result are different
                    if name_match[2] != method_type:
                        raise Exception(f"Name and evaluated value types are different - name_match type: {name_match[2]}   -   method_type: {method_type}")

                    if return_calls:
                        # get type
                        type_return_call = "i64"

                        # get var name
                        name_return_call = "%result"

                        li = [f"ret {type_return_call} {name_return_call}"]

                    else:
                        li = evaled_name_match_value

                else:
                    li = name_match[2:]
            else:
                # print(f"struct member? li: {li}")
                li = _get_struct_member(li, scope)

    # print(f"exiting eval {end_str}: {old_li}  ->  {li}")
    return li


def _call_fn(li, fn, scope):
    # print(f"_call_fn - li: {li} fn: {fn}")

    name = fn[0]
    methods = fn[3]
    candidates = []

    the_method, solved_args = find_fn_method(li, fn, scope)
    # print(f"the_method: {the_method} - solved_args: {solved_args}")

    # set new scope
    fn_scope = default_scope.copy()
    fn_scope[2] = scope  # parent scope
    fn_scope[4] = scope[4]  # handler descriptor
    fn_scope[7] = scope[7]  # backend scope

    # print(f"solved_args: {solved_args}")

    # populate new scope's names with function call arguments
    if li[1:] != [[]]:

        # for arg_i, arg in enumerate(li[1:]):
        for arg_i, arg in enumerate(solved_args):
            # print(f"the_method[0]: {the_method[0]} arg_i: {arg_i} arg: {arg}")
            method_arg = the_method[0][arg_i]
            fn_scope[0].append([method_arg[0], "const", method_arg[1], arg[1]])

    # print(f"fn_scope: {fn_scope}")
    return_calls = scope[6] is not None
    # print(f"return_calls: {return_calls}")

    if len(the_method) == 2:
        if return_calls:
            # print(f"the method len 2 return_calls {li}")
            # return " ".join(li)
            return scope[6](li, scope)
        else:
            # print(f"not return_calls []")
            return []

    return_value = eval(the_method[2], fn_scope)

    # return calls if we need the call output
    if return_calls:
        # print(f"returning call _call_fn {li}")
        return_value = li

    else:
        # if returned value isn't empty list
        if len(return_value) > 0:
            return_value = return_value[0]

            # if returned value type is different from called function type
            if (not isinstance(return_value[0], list) and return_value[0] != the_method[1]):
                raise Exception(f"""Returned value type of function is different from called function type:
    return_value: {return_value}

    the_method[1]: {the_method[1]}

    return_value[0]: {return_value[0]}""")

        # print(f"exiting _call_fn {li} -> {return_value}")
        # return return_value

    return return_value


def find_fn_method(li, fn, scope):
    """
    li    - the list calling the function
    fn    - the function name
    scope - scope list
    """
    # print(f"\nfind_fn_method - li: {li} fn: {fn}\n")

    name = fn[0]
    methods = fn[3]
    candidates = []

    # print(f"methods: {methods}")
    solved_args = []

    for m in methods:
        # print(f"method: {m}")

        # clean solved_args from previous functions
        solved_args = []

        # match types
        match = True
        for arg_i, arg in enumerate(li[1:]):
            # print(f"argument: {arg_i} {arg}")

            # break in methods without the arguments
            if len(m[0]) < arg_i + 1 and not (len(m[0]) == 0 and len(li[1:]) == 1 and li[1] == []):
                # print(f"not matching - len(m[0]) < arg_i + 1")
                match = False
                break

            # if an argument name starts with ', consider anything a match
            # print(f"m0: {m[0][arg_i]}")
            # if m[0][arg_i][0][0][0] == "'":
            #    continue

            # solve argument
            #
            solved_arg = None

            # check if argument is a list
            is_list = isinstance(arg, list)

            # if it's a list
            if is_list:
                # eval it
                # print(f"!! is_list: {is_list} {arg}")
                solved_arg = eval(arg, scope)
                # print(f"!! solved_arg: {solved_arg}")

            # if it's not a list
            else:
                # get name value
                name_value = _get_name_value(arg, scope)
                found_value = list(name_value[2:]) != []

                # if found value, set solved_arg with the value
                if found_value:
                    solved_arg = name_value[2:]

                # if value not found, try to infer type of argument
                else:
                    solved_arg = _infer_type(arg)
            #
            #

            if solved_arg is None:
                # print(f"not matching - solved_arg is None")
                match = False
                break

            solved_args.append(solved_arg)

            if len(solved_arg) == 0:
                # print("len(sorved_arg) == 0")
                pass

            else:
                # print(f"solved_arg: {solved_arg}")
                # print(f"m: {m}")
                # print(f"m[0]: {m[0][0][arg_i]} {arg_i}")
                method_arg_type = m[0][0][arg_i][1]
                # print(f"method_arg_type: {method_arg_type}")

                if solved_arg[0] != method_arg_type:
                    # print(f"not matching - solved_arg[0] != method_arg_type[0] - {solved_arg[0]} != {method_arg_type[0]}")
                    match = False
                    break

        if match:
            candidates.append(m)

    if len(candidates) == 0:
        fns = [n for n in scope[0] if n[2] == "fn"]
        raise Exception(f"No candidate function found - name: {name}  -  fns: {fns}")
    if len(candidates) > 1:
        raise Exception(f"Method candidates mismatch: {name} {candidates}")

    # print(f"candidates: {candidates}")

    the_method = candidates[0][0]
    # print(f"the_method: {the_method}")

    return (the_method, solved_args)


def _get_name_value(name, scope):
    # print(f"name: {name}")
    def iterup(scope):
        # print(f"interup {scope}")
        for n in scope[0]:
            # print(f"n: {n}")
            if n[0] == name:
                return n  # list(n[2:])

        # didn't return found value...

        # if has parent scope, iterup
        if scope[2] is not None:
            return iterup(scope[2])
        # else, return empty list
        else:
            return []

    return iterup(scope)


def _infer_type(arg):
    # print(f"_infer_type - arg: {arg}")

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
        for macro in scope[1]:
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
    def myfn(n, index):
        new_li = n[3][index]

        if len(li) > 2:
            return _get_struct_member([new_li] + li[2:], scope)
        else:
            # print(f"n: {n}")
            # print(f"new_li: {new_li}")
            matches = [name for name in scope[0] if name[0] == n[2] and name[2] == "struct"]
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

    # check if member access "goes deeper"
    # if len(li) > 2:
    #    # print(f"len(li) > 2: {li} {new_li}")
    #    return _get_struct_member([new_li] + li[2:], scope)
    # else:
    #    return new_li
