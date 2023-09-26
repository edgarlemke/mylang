import re


# default scope is given for creating copies
default_scope = [
    [],    # 0 names
    [],    # 1 macros
    None,  # 2 parent scope
    [],    # 3 children scopes
    True,  # 4 is safe scope
    None,  # 5 forced handler
    None,  # 6 eval returns calls
    False,  # 7 backend scope
]


def eval(li, scope, forced_handler_desc=None):
    DEBUG = False
    # DEBUG = True

    is_backend_scope = scope[7] == True
    end_str = "backend" if is_backend_scope else "frontend"

    if DEBUG:
        print(f"""\neval():  {end_str} - li: {li}""")
    # print(f"\neval {li} {scope}")

    old_li = li

    # expand macros until there are no more macros to expand
    new_li = None
    macros = scope[1]

    if DEBUG:
        print(f"eval():  macros: {macros} {scope[5]}")

    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            if DEBUG:
                print(f"eval():  will try to expand macros in {new_li}")

            new_li, found_macro = _expand_macro(new_li, scope)

            if DEBUG:
                print(f"eval():  new_li: {new_li} found_macro: {found_macro}")

            expand = found_macro

        if DEBUG:
            print(f"eval():  expansion ended - new_li: {new_li}")

        li = new_li

    if DEBUG:
        print(f"eval():  macro expanded li: {li}")

    # if the list is empty, return it
    if len(li) == 0:
        if DEBUG:
            print(f"eval():  exiting eval {li}")

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
        if DEBUG:
            print(f"eval():  is_list - li: {li}")
        evaled_li = []
        for key, item in enumerate(li):
            if DEBUG:
                print(f"eval():  li item: {item}")

            evaluated_list_ = eval(item, scope, forced_handler_desc)
            if len(evaluated_list_) > 0:
                evaled_li.append(evaluated_list_)

        li = evaled_li
        if DEBUG:
            print(f"evaled_li: {evaled_li}")

        # check if li has evaled with forced handler in scope but no handler
        if forced_handler_desc is not None and scope[5] is not None:
            # panic
            raise Exception(f"Forced handler set in scope but no handler - forced handler: {scope[5]} - li: {li}")

    else:
        # get name value from scope
        name_match = get_name_value(li[0], scope)

        # check name_matches size
        if name_match == []:
            raise Exception(f"Unassigned name: {li[0]}")
        # elif len(name_matches) > 1:
        #    raise Exception(f"More than one name set, it's a bug! {li[0]}")

        if name_match[2] in ["fn", "internal"]:
            if DEBUG:
                print(f"eval():  li calls fn/internal - name_match: {name_match}")

            # len == 1, so it's a reference
            if len(li) == 1:
                # print(f"fn ref {li}")
                li = name_match

            # len > 1, so it's a function call
            else:
                if name_match[2] == "fn":
                    if DEBUG:
                        print(f"eval():  name_match is function - name_match: {name_match}")

                    retv = _call_fn(li, name_match, scope)

                    if DEBUG:
                        print(f"eval():  retv: {retv}")

                    if len(retv) == 2 and isinstance(retv[0], list) and isinstance(retv[1], list):
                        scope[5] = retv[1]
                        retv = retv[0]

                    li = retv

                elif name_match[2] == "internal":
                    if DEBUG:
                        print(f"eval():  name_match is internal - name_match: {name_match}")

                    li = name_match[3](li, scope)

                if DEBUG:
                    print(f"eval():  internal result li: {li}")

        # not function nor internal
        else:
            if DEBUG:
                print(f"eval():  not function nor internal: {li}")

            # if is list of single item
            if len(li) == 1:
                name_match_value = name_match[3]

                # if name match value is list
                if isinstance(name_match_value, list):

                    # evaluate the list
                    if DEBUG:
                        print(f"eval():  evaluating list: {name_match[3]}")
                    evaled_name_match_value = eval(name_match_value, scope, forced_handler_desc)
                    method_type = evaled_name_match_value[0]

                    # if return_calls is set, get correct method type
                    return_calls = scope[6] is not None
                    if return_calls:
                        evaled_fn = get_name_value(evaled_name_match_value[0], scope)
                        method, solved_arguments = find_function_method(evaled_name_match_value, evaled_fn, scope)
                        method_type = method[1]

                    # if type of name match and type of list result are different
                    if name_match[2] != method_type:
                        raise Exception(f"Name and evaluated value types are different - name_match type: {name_match[2]}   -   method_type: {method_type}")

                    if return_calls:
                        # get type
                        type_return_call = "i64"

                        # get var name
                        name_return_call = "%result_0"

                        li = [f"ret {type_return_call} {name_return_call}"]

                    else:
                        li = evaled_name_match_value

                else:
                    li = name_match[2:]
            else:
                if DEBUG:
                    print(f"eval():  struct member li: {li}")

                li = _get_struct_member(li, scope)

    if DEBUG:
        print(f"eval():  exiting {end_str}: {old_li}  ->  {li}")

    return li


def _call_fn(li, fn, scope):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_call_fn():  li: {li} fn: {fn}")

    name = fn[0]
    methods = fn[3]
    candidates = []

    found_method, solved_arguments = find_function_method(li, fn, scope)
    # print(f"found_method: {found_method} - solved_arguments: {solved_arguments}")

    # set new scope
    fn_scope = default_scope.copy()
    fn_scope[2] = scope  # parent scope
    fn_scope[4] = scope[4]  # handler descriptor
    fn_scope[7] = scope[7]  # backend scope

    # print(f"solved_arguments: {solved_arguments}")

    # populate new scope's names with function call arguments
    if li[1:] != [[]]:

        # for arg_i, arg in enumerate(li[1:]):
        for arg_i, arg in enumerate(solved_arguments):
            # print(f"found_method[0]: {found_method[0]} arg_i: {arg_i} arg: {arg}")
            method_arg = found_method[0][arg_i]
            fn_scope[0].append([method_arg[0], "const", method_arg[1], arg[1]])

    # print(f"fn_scope: {fn_scope}")
    return_calls = scope[6] is not None
    # print(f"return_calls: {return_calls}")

    # check for functions without return value
    if len(found_method) == 2:
        if return_calls:
            return_call_function = scope[6]

            if DEBUG:
                print(f"_call_fn():  CALLING return_call() - li: {li}")

            value, stack = return_call_function(li, scope)
            value = f"\t\t{value}"

            if DEBUG:
                print(f"_call_fn():  value: {value}  stack: {stack}")

            # stack.append(value)
            # return stack
            return value
        else:
            # print(f"not return_calls []")
            return []

    return_value = eval(found_method[2], fn_scope)

    # return calls if we need the call output
    if return_calls:
        if DEBUG:
            print(f"returning call _call_fn {li}")
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

    if DEBUG:
        print(f"_call_fn:  exiting {li} -> {return_value}")

    return return_value


def find_function_method(li, fn, scope):
    """
    li    - the list calling the function
    fn    - the function name
    scope - scope list
    """

    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"\nfind_function_method - li: {li} fn: {fn}\n")

    name = fn[0]
    methods = fn[3]
    candidates = []

    if DEBUG:
        print(f"methods: {methods}")

    solved_arguments = []

    for method in methods:
        if DEBUG:
            print(f"\nmethod: {method}")

        # clean solved_arguments from previous functions
        solved_arguments = []

        # match types
        match = True
        for arg_i, arg in enumerate(li[1:]):
            if DEBUG:
                print(f"\nargument - arg_i: {arg_i} arg: {arg}")

            # break in methods without the arguments
            if len(method[0][0]) < arg_i + 1 and not (len(method[0][0]) == 0 and len(li[1:]) == 1 and li[1] == []):
                if DEBUG:
                    print(f"not matching - len(method[0]) < arg_i + 1")

                match = False
                break

            # solve argument
            #
            solved_argument = None

            # check if argument is a list
            is_list = isinstance(arg, list)

            # if it's a list
            if is_list:
                if DEBUG:
                    print(f"is_list: {is_list} arg: {arg} method[0][0]: {method[0][0]}")
                    print(f"is backend scope: {scope[7]}")

                # if it's calling a function without arguments with a single empty list as argument
                if len(arg) == 0 and len(method[0][0]) == 0:
                    continue

                # if it's a backend scope
                if scope[7] == True:
                    # get function
                    list_function = get_name_value(arg[0], scope)
                    if DEBUG:
                        print(f"list_function: {list_function}")

                    # if found function
                    if len(list_function) > 0:
                        # find function method for argument
                        argument_method, argument_solved_arguments = find_function_method(arg, list_function, scope)
                        if DEBUG:
                            print(f"argument_method: {argument_method} argument_solved_arguments: {argument_solved_arguments}")

                        # set a dummy solved_argument just with the correct type
                        solved_argument = [argument_method[1], '?']

                # if it's a frontend scope, eval argument
                else:
                    # eval it
                    if DEBUG:
                        print(f"calling eval() to solve argument {arg}")

                    solved_argument = eval(arg, scope)

                if DEBUG:
                    print(f"list solved_argument: {solved_argument}")

            # if it's not a list
            else:
                if DEBUG:
                    print(f"find_function_method():  argument {arg} isn't a list")

                # get name value
                name_value = get_name_value(arg, scope)
                if DEBUG:
                    print(f"find_function_method():  name_value: {name_value} arg: {arg}")
                    print(f"find_function_method():  names: {[i[0] for i in scope[0]]}")
                    print(f"find_function_method():  scope[0]: {scope[0]}")

                found_value = list(name_value[2:]) != []

                if DEBUG:
                    print(f"find_function_method():  found_value: {found_value}")

                # if found value, set solved_argument with the value
                if found_value:
                    solved_argument = name_value[2:]

                # if value not found, try to infer type of argument
                else:
                    solved_argument = _infer_type(arg)

                    if solved_argument is None:
                        raise Exception(f"Unassigned name: {arg}")
            #
            #

            if solved_argument is None:
                if DEBUG:
                    print(f"not matching - solved_argument is None")

                match = False
                break

            solved_arguments.append(solved_argument)

            if len(solved_argument) == 0:
                if DEBUG:
                    print("len(sorved_arg) == 0")
                pass

            else:
                if DEBUG:
                    print(f"solved_argument: {solved_argument}")
                    print(f"method: {method}")
                    print(f"method[0]: {method[0][0][arg_i]} - arg_i: {arg_i}")

                # get the type of the method argument
                method_argument_type = method[0][0][arg_i][1]

                if DEBUG:
                    print(f"method_argument_type: {method_argument_type}")

                # if the type of the solved argument is different from the type of the method argument, don't match
                if solved_argument[0] != method_argument_type:
                    if DEBUG:
                        print(f"not matching - solved_argument[0] != method_argument_type - {solved_argument[0]} != {method_argument_type}")

                    match = False
                    break

        if match:
            if DEBUG:
                print(f"matching - appending to candidates: {method}")
            candidates.append(method)

    if len(candidates) == 0:
        functions = [n for n in scope[0] if n[2] == "fn"]
        raise Exception(f"No candidate function found - name: {name}  -  functions: {functions}  - li: {li} - solved_arguments: {solved_arguments}")
    if len(candidates) > 1:
        raise Exception(f"Method candidates mismatch: {name} {candidates}")

    if DEBUG:
        print(f"candidates: {candidates}")

    found_method = candidates[0][0]

    if DEBUG:
        print(f"exiting find_function_method - li: {li} -> found_method: {found_method} solved_arguments: {solved_arguments}\n")

    return (found_method, solved_arguments)


def get_name_value(name, scope):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"get_name_value()  - name: {get_name_value}")

    def iterup(scope):
        for each_name in scope[0]:
            if DEBUG:
                print(f"get_name_value()  - each_name: {each_name}")

            if each_name[0] == name:
                return each_name  # list(n[2:])

        # didn't return found value...

        # if has parent scope, iterup
        if scope[2] is not None:
            return iterup(scope[2])
        # else, return empty list
        else:
            return []

    return iterup(scope)


def _infer_type(arg):
    # DEBUG = False
    # DEBUG = True

    # if DEBUG:
    #    print(f"_infer_type():  arg: {arg}")

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
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_get_struct_member:  li: {li}")

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
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_seek_struct_ref():  li: {li} fn: {fn}")

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


def _seek_array_ref(li, scope, fn):
    DEBUG = False
    # DEBUG = True

    # seeks names matching with li[0]
    name_matches = [n for n in scope[0] if n[0] == li[0]]
    n = name_matches[0]

    # get possible array_type
    array_type = n[2]

    # check if there's some struct set with this name
    candidates = [s for s in scope[0] if s[2] == array_type]  # type(s[2]) == list and s[2][0] == "Array" ] #and s[0] == struct_name]
    if DEBUG:
        print(f"candidates: {candidates}")

    # get the candidate struct
    candidate = candidates[0]

    if DEBUG:
        print(f"_seek_array_ref():  candidate: {candidate}")

    index = int(li[1])

    return fn(n, index)
