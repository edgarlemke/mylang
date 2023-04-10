#!/usr/bin/python3


def parse(token_list, root):

    result = _parse(token_list, root)
    status, parsetree, last_found_buf = result

    if status == "NOTR":
        raise Exception(
            f"Invalid syntax!\n\nlast_found_buf: {last_found_buf}\n\nparsetree: {parsetree}")

    return parsetree


def _parse(token_list, root):

    buf = []
    token_ct = 0

    last_found_rule = None
    last_buf = None
    lookahead = token_list[token_ct]
    while token_ct < len(token_list):

        # shift
        buf.append(lookahead)

        # update lookahead
        if token_ct + 1 == len(token_list):
            lookahead = None
        else:
            lookahead = token_list[token_ct + 1]

        # look for rules and reduce as long as needed
        while True:
            # print(f"loop start buf: {buf}")
            match = _find_match(buf, lookahead)

            if match is not None:
                start, rule = match
                # print(f"start: {start}")
                # print(f"rule: {rule}")

                # reduce
                #
                # pop matching slice from buffer
                popped = []
                for j in range(start, start + len(rule[1])):
                    popped.append(buf.pop(start))
                #
                # substitute the slice with target
                inplace = rule[0].copy()
                inplace.append(popped)
                buf.insert(start, inplace)
                #

                last_found_rule = inplace
                last_buf = buf.copy()

            else:
                # if not all tokens have been buffered, get out of while loop
                # and shift
                all_tokens_buffered = token_ct + 1 == len(token_list)
                if not all_tokens_buffered:
                    break

                # ... all tokens have been buffered

                # if buffer length isn't 1 and buffer root variable isn't
                # "root", we have a syntax error
                buff_len_one = len(buf) == 1
                buff_expr = buf[0][0] == root
                if not (buff_len_one and buff_expr):
                    # raise Exception(f"Invalid syntax!\nlast_found_rule: {last_found_rule}\n\nbuf:{buf}")
                    return ("NOTR", buf, last_buf)

                break

        token_ct += 1

    return ("OK", buf, last_buf)


def _find_match(buf, lookahead):
    token_rule_prec = [
        [["ELSE"], [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]]],
        [["ELSE"], [["EXPR"], ["IF_DECL"]]],
        [["ELSE"], [["IF_ELIF_DECL"], ["IF_DECL", "ELIF_DECL"]]],
        [["ELSE"], [["EXPR"], ["IF_ELIF_DECL"]]],
        [["ELSE"], [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]]],
        [["ELSE"], [["EXPR"], ["IF_ELIF_GROUP_DECL"]]],

        [["ELIF"], [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]]],
        [["ELIF"], [["EXPR"], ["IF_DECL"]]],
        [["ELIF"], [["IF_ELIF_DECL"], ["IF_DECL", "ELIF_DECL"]]],
        [["ELIF"], [["EXPR"], ["IF_ELIF_DECL"]]],
        [["ELIF"], [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]]],
        [["ELIF"], [["EXPR"], ["IF_ELIF_GROUP_DECL"]]],

        [["ELIF_DECL"], [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]]],

        [["BLOCK_START"], [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAME"]]],
        [["BLOCK_START"], [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "PAR_GROUP"]]],
        [["BLOCK_START"], [["EXPR"], ["PAR_GROUP"]]],

        [["SPACE"], [["EXPR"], ["PAR_GROUP"]]],
        [["SPACE"], [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "PAR_GROUP"]]],
        [["SPACE"], [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAME"]]],
        [["SPACE"], [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAMEPAIR"]]],
        [["SPACE"], [["CALL_DECL"], ["NAME", "SPACE",
                                     "SPACE", "NAMEPAIR", "SPACE", "NAME"]]],
        [["SPACE"], [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP"]]],
        [["SPACE"], [["CALL_DECL"], ["NAME", "SPACE",
                                     "SPACE", "NAMEPAIR_GROUP", "SPACE", "NAME"]]],

        [["SPACE"], [["USE_DECL"], ["USE", "SPACE", "NAME"]]],
        # [ ["SPACE"], [["USE_DECL"], ["USE", "SPACE", "SPACE", "NAMEPAIR"]] ],
        [["SPACE"], [["EXPR"], ["USE_DECL"]]],

        [["SPACE"], [["RET_DECL"], ["RET"]]],
    ]

    match = None

    # iters over buffer slices looking for rule
    for i in range(0, len(buf)):
        buf_slice = buf[i:]
        rule = _match(buf_slice)

        # if didn't find matching rule, skip
        if rule is None:
            continue

        # find token-rule precedence
        force_prec_shift = False
        for prec_rule in token_rule_prec:
            prec_rule_token, prec_rule_target = prec_rule

            # print(f"prec_rule_target: {prec_rule_target}  rule: {rule}    {prec_rule_target == rule}")
            # print(f"prec_rule_token: {prec_rule_token} lookahead: {lookahead}     {prec_rule_token[0] == lookahead[0]}")
            target_match = (prec_rule_target == rule)
            token_in_lookahead = (
                lookahead is not None and prec_rule_token[0] == lookahead[0])
            token_in_buffer = (prec_rule_token[0] in [
                               b[0] for b in buf_slice[len(prec_rule_target[1]):]])
            if target_match and (token_in_lookahead or token_in_buffer):
                # print(f"    force_prec_shift {prec_rule_target} {prec_rule_token}")
                force_prec_shift = True
                break

        if force_prec_shift:
            continue

        match = [i, rule]

        break

    return match


def _match(buf_slice):
    rules = [
        [
            # expressions
            [["EXPR"], ["EXPR", "EXPR"]],

            [["EXPR"], ["INT"]],
            [["EXPR"], ["FLOAT"]],
            [["EXPR"], ["QUOTE", "QVALUE", "QUOTE"]],
            [["EXPR"], ["BOOL"]],

            [["EXPR"], ["NOP"]],

            [["EXPR"], ["PAR_GROUP"]],

            [["EXPR"], ["FN_DECL"]],
            [["EXPR"], ["CALL_DECL"]],
            [["EXPR"], ["RET_DECL"]],

            [["EXPR"], ["SET_DECL"]],
            [["EXPR"], ["MUT_DECL"]],

            [["EXPR"], ["IF_DECL"]],
            [["EXPR"], ["IF_ELSE_DECL"]],
            [["EXPR"], ["IF_ELIF_DECL"]],
            [["EXPR"], ["IF_ELIF_GROUP_DECL"]],
            [["EXPR"], ["IF_ELIF_ELSE_DECL"]],
            [["EXPR"], ["IF_ELIF_GROUP_ELSE_DECL"]],

            [["EXPR"], ["WHILE_DECL"]],
            [["EXPR"], ["FOR_DECL"]],

            [["EXPR"], ["TYPEDEF_DECL"]],

            [["EXPR"], ["STRUCT_DECL"]],
            [["EXPR"], ["RES_STRUCT_DECL"]],

            [["EXPR"], ["USE_DECL"]],
            [["EXPR"], ["PKG_DECL"]],

            # parenthesis groups
            [["PAR_GROUP"], ["PAR_OPEN", "PAR_CLOSE"]],
            [["PAR_GROUP"], ["PAR_OPEN", "EXPR", "PAR_CLOSE"]],

            [["PAR_GROUP"], ["PAR_OPEN", "NAME", "PAR_CLOSE"]],

            # blocks
            [["BLOCK"], ["BLOCK_START", "EXPR", "BLOCK_END"]],

            # function related
            # function arguments
            [["NAMEPAIR"], ["NAME", "SPACE", "NAME"]],
            [["NAMEPAIR_GROUP"], ["NAMEPAIR", "SPACE", "SPACE", "NAMEPAIR"]],
            [["NAMEPAIR_GROUP"], ["NAMEPAIR", "SPACE", "NAMEPAIR"]],
            [["NAMEPAIR_GROUP"], ["NAMEPAIR_GROUP", "SPACE", "SPACE", "NAMEPAIR"]],
            [["NAMEPAIR_GROUP"], ["NAMEPAIR_GROUP", "SPACE", "NAMEPAIR"]],

            [["ARG_PAR_GROUP"], ["PAR_OPEN", "NAMEPAIR", "PAR_CLOSE"]],
            [["ARG_PAR_GROUP"], ["PAR_OPEN", "NAMEPAIR", "SPACE", "NAME", "PAR_CLOSE"]],
            [["ARG_PAR_GROUP"], ["PAR_OPEN", "NAMEPAIR_GROUP", "PAR_CLOSE"]],
            [["ARG_PAR_GROUP"], ["PAR_OPEN", "NAMEPAIR_GROUP",
                                 "SPACE", "NAME", "PAR_CLOSE"]],

            # function declarations
            #   functions without argument and without return type
            [["FN_DECL"], ["FN", "SPACE", "NAME", "BLOCK"]],
            #   functions with arguments and without return type
            [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE",
                           "SPACE", "ARG_PAR_GROUP", "BLOCK"]],
            #   functions with or without arguments and with return type
            [["FN_DECL"], ["FN", "SPACE", "NAME",
                           "SPACE", "SPACE", "PAR_GROUP", "BLOCK"]],
            [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE", "SPACE",
                           "PAR_GROUP", "SPACE", "SPACE", "NAME", "BLOCK"]],
            [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE", "SPACE",
                           "ARG_PAR_GROUP", "SPACE", "SPACE", "NAME", "BLOCK"]],

            # function calls
            [["CALL_DECL"], ["NAME", "PAR_GROUP"]],  # for empty par_group
            [["CALL_DECL"], ["NAME", "ARG_PAR_GROUP"]],

            [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "PAR_GROUP"]],
            [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAME"]],
            [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAMEPAIR"]],
            [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAMEPAIR", "SPACE", "NAME"]],
            [["CALL_DECL"], ["NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP"]],
            [["CALL_DECL"], ["NAME", "SPACE", "SPACE",
                             "NAMEPAIR_GROUP", "SPACE", "NAME"]],

            # function return
            [["RET_DECL"], ["RET"]],
            [["RET_DECL"], ["RET", "SPACE", "NAME"]],
            [["RET_DECL"], ["RET", "SPACE", "EXPR"]],
            #

            # variables and constants
            # set
            [["SET_DECL"], ["SET", "SPACE", "NAMEPAIR", "SPACE", "EXPR"]],
            # mut
            [["MUT_DECL"], ["MUT", "SPACE", "NAMEPAIR", "SPACE", "EXPR"]],

            # control flux
            # if
            [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]],
            [["IF_DECL"], ["IF", "SPACE", "EXPR", "BLOCK"]],
            # if-else
            [["ELSE_DECL"], ["ELSE", "BLOCK"]],
            [["IF_ELSE_DECL"], ["IF_DECL", "ELSE_DECL"]],
            # if-elif
            [["ELIF_DECL"], ["ELIF", "SPACE", "NAME", "BLOCK"]],
            [["ELIF_DECL"], ["ELIF", "SPACE", "EXPR", "BLOCK"]],
            [["IF_ELIF_DECL"], ["IF_DECL", "ELIF_DECL"]],
            [["ELIF_GROUP"], ["ELIF_DECL", "ELIF_DECL"]],
            [["ELIF_GROUP"], ["ELIF_GROUP", "ELIF_DECL"]],
            [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]],
            # if-elif-else
            [["IF_ELIF_ELSE_DECL"], ["IF_DECL", "ELIF_DECL", "ELSE_DECL"]],
            [["IF_ELIF_GROUP_ELSE_DECL"], ["IF_DECL", "ELIF_GROUP", "ELSE_DECL"]],

            # while
            [["WHILE_DECL"], ["WHILE", "SPACE", "NAME", "BLOCK"]],
            [["WHILE_DECL"], ["WHILE", "SPACE", "EXPR", "BLOCK"]],
            # for
            [["FOR_DECL"], ["FOR", "SPACE", "NAME", "SPACE", "SPACE", "NAME", "BLOCK"]],
            [["FOR_DECL"], ["FOR", "SPACE", "NAMEPAIR",
                            "SPACE", "SPACE", "NAME", "BLOCK"]],

            # typedef
            [["TYPEDEF_DECL"], ["TYPEDEF", "SPACE", "NAME", "SPACE", "EXPR"]],

            # structs
            [["STRUCT_DECL"], ["STRUCT", "SPACE", "NAME", "STRUCT_BLOCK"]],
            [["RES_STRUCT_DECL"], ["RES", "SPACE",
                                   "STRUCT", "SPACE", "NAME", "STRUCT_BLOCK"]],

            [["STRUCT_BLOCK"], ["BLOCK_START", "NAMEPAIR", "BLOCK_END"]],
            [["STRUCT_BLOCK"], ["BLOCK_START", "STRUCT_DEF_GROUP", "BLOCK_END"]],

            [["STRUCT_DEF_GROUP"], ["NAMEPAIR", "NAMEPAIR"]],
            [["STRUCT_DEF_GROUP"], ["STRUCT_DEF_GROUP", "NAMEPAIR"]],

            # packages
            # [["USE_DECL"], ["USE", "SPACE", "EXPR"]],
            [["USE_DECL"], ["USE", "SPACE", "NAME"]],
            # [["USE_DECL"], ["USE", "SPACE", "NAME", "SPACE", "SPACE", "NAME"]],

            [["USE_DECL"], ["USE", "SPACE", "NAMEPAIR"]],
            # [["USE_DECL"], ["USE", "SPACE", "NAMEPAIR", "SPACE", "SPACE", "NAME"]],


            # [["PKG_DECL"], ["PKG", "SPACE", "NAME", "BLOCK"]],
        ],
    ]

    all_matches = []
    for order, ruleorder in enumerate(rules):
        all_matches.append([])

        for r in ruleorder:
            matches = []

            for i, item in enumerate(buf_slice):
                if i > len(r[1]) - 1:
                    break

                if item[0] == r[1][i]:
                    matches.append(True)

            some_match = len(matches) > 0
            match_rule_same_size = len(matches) == len(r[1])

            if some_match and all(matches) and match_rule_same_size:
                all_matches[order].append(r)

    largest = None
    for order in all_matches:
        for m in order:
            if largest is None:
                largest = m
                continue

            if len(largest[1]) < len(m[1]):
                largest = m
                continue

            if len(largest[1]) == len(m[1]):
                raise Exception(f"Rule mismatch: {largest} {m}")

        # stop at the first order which found some rule
        if largest is not None:
            break

    if largest is not None:
        # print(f"buf_slice: {buf_slice}\nlargest: {largest}\n")
        return largest

    return None


def abstract(parsetree):

    _clean_nodes(parsetree)
    _clean_token_data(parsetree)
    _merge_groups(parsetree)

    parsetree = _merge_single_children(parsetree)

    return parsetree


def _clean_nodes(list_):
    to_remove = [
        "SPACE",
        "PAR_OPEN", "PAR_CLOSE",
        "BLOCK_START", "BLOCK_END",
        "IF", "ELIF", "ELSE",
        "FOR",
        "WHILE",
        "FN",
        "SET",
        "MUT",
        "RET",
        "PKG",
        "USE",
    ]
    for index, item in enumerate(list_.copy()):
        if not isinstance(item, list):
            continue
        if item[0] in to_remove:
            list_.remove(item)
        else:
            _clean_nodes(item)


def _clean_token_data(list_):
    import lex
    lex_tokens = [i[0] for i in lex.rules_list]

    for index, item in enumerate(list_.copy()):
        if not isinstance(item, list):
            continue

        if len(item) >= 1 and item[0] in lex_tokens:
            if item[0] in ["NAME", "INT", "FLOAT", "BOOL"]:
                limit = 2
            else:
                limit = 3
            for i in range(0, limit):
                item.pop(1)
        else:
            _clean_token_data(item)


group_tokens = ["NAMEPAIR", "NAMEPAIR_GROUP", "EXPR_GROUP", "BLOCK"]


def _merge_groups(list_):
    for i, item in enumerate(list_):
        if not isinstance(item, list):
            continue

        if len(item) >= 1 and item[0] in group_tokens:
            item.pop(0)

        _merge_groups(item)


def _merge_single_children(list_):

    if len(list_) == 1:
        list_ = list_[0]

    for i, item in enumerate(list_):
        if not isinstance(item, list):
            continue

        if len(item) == 1 and isinstance(item[0], list):
            # list_[i].append(item[0])
            # list_[i].pop(0)
            list_[i] = item[0]

        _merge_single_children(item)

    return list_


def serialize_tree(tree):
    s = [["EXPR", None, []]]

    def _follow(li, s, parent):
        new = []

        for i, node in enumerate(li):
            if not isinstance(node, list):
                continue

            to_append = [
                child for child in node if not isinstance(
                    child, list)]
            # print(to_append)

            if len(to_append) > 0:
                to_append += [parent] + [[]]
                s.append(to_append)
                new_parent = len(s) - 1

                s[parent][len(s[parent]) - 1].append(new_parent)

            else:
                new_parent = parent

            _follow(node, s, new_parent)

        s += new

    _follow(tree, s, len(s) - 1)

    return s
