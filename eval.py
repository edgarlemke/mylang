import eval_types


def eval(li):
    print(f"eval {li}")

    new_li = None
    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            new_li, found_macro = expand_macro(new_li)
            # print(f"expand new_li: {new_li}")
            expand = found_macro

        # print(f"over new_li: {new_li}")

        li = new_li

    if len(li) == 0:
        return li

    if li[0] == "data":
        return li

    is_macro = li[0] == "macro"

    found_list_at_0 = False
    for index, item in enumerate(li):
        if isinstance(item, list):
            if index == 0:
                found_list_at_0 = True

            if not is_macro:
                li[index] = eval(item)

    if not found_list_at_0:
        funcs = [v for v in variables if v[1] == "fn"]
        # print(f"funcs: {funcs}")
        for fn in funcs:
            fn_name, fn_type, fn_bgfn = fn

            # if function name matches first item of list
            if li[0] == fn_name:
                # call background function
                li = fn_bgfn(li)
                break

    return li


def expand_macro(li):
    print(f"expand_macro: {li}")

    new_li = li.copy()
    found_macro = False
    # for each macro
    for m in macros:
        print(f"m: {m}")
        alias, syntax, expanded = m

        shift = False
        start = None
        end = None
        matching = []
        bindings = []
        # for each item in li
        for index, item in enumerate(li):

            # iters only over the rest of syntax if has some matching
            rest = syntax[len(matching):]
            print(f"index: {index} item: {item} rest: {rest}")
            for syn in rest:
                print(f"alias: {alias} syn \"{syn}\" item \"{item}\"")

                # match quoted syntax pieces with anything
                quote = syn[0] == "'"
                if quote:
                    # set start if not set
                    if start is None:
                        start = index

                    # add item to matching
                    # print(f"matchin {item} with {syn}")
                    matching.append(item)

                    # add pair to bindings
                    bindings.append([syn, item])

                    break

                # other, unquoted pieces of syntax
                else:
                    # if syntax piece doesn't match item, shift to next macro
                    if syn != item:
                        print(f"syntax piece doesn't match item: {syn} != {item}")
                        # shift = True
                        matching = []
                        bindings = []
                        start = None
                        end = None
                        break

                    # syntax piece is matching item
                    # set start if not set
                    if start is None:
                        start = index

                    # add item to matching
                    # print(f"matchin {item} with {syn}")
                    matching.append(item)
                    break

            if len(matching) == len(syntax):
                # print(f"len matchings = len syntax - matching: {matching} syntax {syntax}")
                found_macro = True
                end = index
                break

#                # if syntax's first char is ', it matches with any li item
#                if syn[0] == "'":
#                    matching.append(item)
#                    print(f"Q matching {syn} with {item}")
#                    bindings.append([syn, item])
#                    if start == None:
#                        print(f"setting start as {index}")
#                        start = index
#                    break
#
#                # if syntax item doesn't match with the current li item, shift to next li macro
#                if syn != item:
#                    shift = True
#                    matching = []
#                    print(f"sym != item")
#                    break
#                else:
#                    matching.append(item)
#                    print(f"N matching {syn} with {item}")
#                    print(f"matching: {matching}  index: {index}  syntax {syntax}")
#
#                    # if no start is set, set it
#                    if start == None:
#                        print(f"setting start as {index}")
#                        start = index
#
#                print(f"-- matching: {matching} len-s: {len(syntax)}")
#
#                # if we're here and on the last item of syntax and all matched, found macro
#                if len(matching) == len(syntax):
#                    print(f"ended syntax and all matched!")
#                    found_macro = True
#                    shift = True
#                    matching = []
#                    end = index
#                    break

            if shift:
                break

        # print(f"before found macro start: {start} end: {end}")

        if found_macro:
            print(f"found_macro! {m} {expanded}")
            # print(f"start: {start} end: {end}")

            # print(f"old new_li: {new_li}")
            for i in reversed(range(start, end + 1)):
                new_li.pop(i)

            # print(f"bindings: {bindings}")
            for exp in reversed(expanded):
                inplace = None
                for b in bindings:
                    name, value = b
                    # print(f"BINGDING: {b}\n")

#                    print(f"binding exp: {exp} name: {name}")
#                    if type(exp) == list:
#                        print("LIST!")
#
#                    if exp == name:
#                        inplace = value
#                        print(f"found binding: {name}")
#                        break
                    def inplace_exp(lvl, lix):
                        lixc = lix.copy()
                        # print(f"\nlvl: {lvl} lix: {lix}")

                        found = True
                        while found:
                            found = False

                            for i2, item2 in enumerate(lixc):
                                # print(f"item2: {item2}")
                                if isinstance(item2, list):
                                    # print(f"calling listfier again")
                                    # print(f"LIST lixc old: {lixc}")
                                    lixc[i2] = inplace_exp(lvl + 1, item2)
                                    # print(f"LIST lixc new: {lixc}")
                                else:
                                    # print(f"OwO  {item2} {name}")
                                    if item2 == name:
                                        # print(f"setting {item2} {name} <<")
                                        # print(f"MATCH lixc old: {lixc}")
                                        lixc[i2] = value
                                        # print(f"MATCH lixc new: {lixc}")
                                        found = True

                        # print(f"final lixc: {lixc} lvl {lvl}")
                        return lixc

                    if isinstance(exp, list):
                        # print("LIST!")
                        xyz = inplace_exp(0, exp)
                        # print(f"end of inplace {xyz}")
                        exp = xyz
                        inplace = xyz

                    elif exp == name:
                        inplace = value
                        break

                if inplace is None:
                    inplace = exp

                new_li.insert(start, inplace)

            # print(f"new new_li: {new_li}")
            break

    return [new_li, found_macro]


def __set__(node):
    """
    Set a variable in the current variables namespace.
    """

    print(f"calling __set__ {node}")

    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for set: {node}")

    name = node[1]
    data = node[2]
    type_, value = data[1]

    valid_value = None
    for T in eval_types.types:
        if T[0] == type_:
            valid_value = T[1](value)

    # remove old value from variables
    for index, v in enumerate(variables):
        if v[0] == name:
            variables.remove(v)
        break

    # insert new value into variables
    variables.append([name, type_, valid_value])
    print(f"variables after set: {variables}")

    retv = ["data", ["set", name, type_, value]]
    print(f"returning {retv}")
    return retv


def __macro__(node):
    """
    Set a new macro in the current macros namespace.
    """

    print(f"calling __macro__ {node}")

    alias = node[1]
    # print(f"alias: {alias}")

    syntax = node[2]
    # print(f"syntax: {syntax}")

    expanded = node[3]
    # print(f"expanded: {expanded}")

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

    macros.append([alias, new_syntax, new_expanded])

    return []


variables = [
    ["set", "fn", __set__],
    ["macro", "fn", __macro__]
]

macros = [
]
