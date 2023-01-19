#!/usr/bin/python3


def parse (token_list, root) :

    buf = []
    token_ct = 0

    last_found_rule = None
    lookahead = token_list[token_ct]
    while token_ct < len(token_list):

        # shift
        buf.append(lookahead)

        # update lookahead
        if token_ct+1 == len(token_list):
            lookahead = None
        else:
            lookahead = token_list[token_ct+1]
        
        # look for rules and reduce as long as needed
        while True:
            match = _find_match(buf, lookahead)

            if match != None:
                start, rule = match

                # reduce
                #
                # pop matching slice from buffer
                popped = []
                for j in range(start, start+len(rule[1])):
                    popped.append( buf.pop(start) )
                #
                # substitute the slice with target
                inplace = rule[0].copy()
                inplace.append(popped)
                buf.insert(start, inplace)
                #

                last_found_rule = inplace

            else:
                # if not all tokens have been buffered, get out of while loop and shift
                all_tokens_buffered = token_ct + 1 == len(token_list)
                if not all_tokens_buffered:
                    break

                # ... all tokens have been buffered

                # if buffer length isn't 1 and buffer root variable isn't "root", we have a syntax error
                buff_len_one = len(buf) == 1
                buff_expr = buf[0][0] == root
                if not (buff_len_one and buff_expr):
                    raise Exception(f"Invalid syntax!\nlast_found_rule: {last_found_rule}\n\nbuf: {buf}")

                break

        token_ct += 1

    parsetree = buf
    return parsetree


def _find_match (buf, lookahead):
    token_rule_prec = [
        [ ["ELSE"], [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]] ],
        [ ["ELSE"], [["EXPR"], ["IF_DECL"]] ],
        [ ["ELSE"], [["IF_ELIF_DECL"], ["IF_DECL", "ELIF_DECL"]] ],
        [ ["ELSE"], [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]] ],

        [ ["ELIF"], [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]] ],
        [ ["ELIF"], [["IF_ELIF_DECL"], ["IF_DECL", "ELIF_DECL"]] ],
        [ ["ELIF"], [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]] ],

        [ ["ELIF_DECL"], [["IF_ELIF_GROUP_DECL"], ["IF_DECL", "ELIF_GROUP"]] ],

        [ ["SPACE"], [["CALL_DECL"], ["CALL", "SPACE", "NAME"]] ],
        [ ["SPACE"], [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAME"]] ],
        [ ["SPACE"], [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR"]] ],
        [ ["SPACE"], [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR", "SPACE", "NAME"]] ],
        [ ["SPACE"], [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP"]] ],
        [ ["SPACE"], [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP", "SPACE", "NAME"]] ],

        [ ["SPACE"], [["EXPR"], ["CALL_DECL"]] ],
    ]

    match = None

    # iters over buffer slices looking for rule
    for i in range(0, len(buf)):
        buf_slice = buf[i:]
        rule = _match(buf_slice)

        # if didn't find matching rule, skip
        if rule == None:
            continue

        # find token-rule precedence
        force_prec_shift = False
        for prec_rule in token_rule_prec:
            prec_rule_token, prec_rule_target = prec_rule

            #print(f"prec_rule_target: {prec_rule_target}  rule: {rule}    {prec_rule_target == rule}")
            #print(f"prec_rule_token: {prec_rule_token} lookahead: {lookahead}     {prec_rule_token[0] == lookahead[0]}")
            target_match = (prec_rule_target == rule) 
            token_in_lookahead = (lookahead != None and prec_rule_token[0] == lookahead[0])
            token_in_buffer = (prec_rule_token[0] in [b[0] for b in buf_slice[ len(prec_rule_target[1]): ]])
            if target_match and (token_in_lookahead or token_in_buffer):
                #print(f"    force_prec_shift {prec_rule_target} {prec_rule_token}")
                force_prec_shift = True
                break

        if force_prec_shift:
            continue

        match = [i, rule]

        break

    return match


def _match (buf_slice):
    rules = [
        [
            # expressions
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
    
            [["EXPR"], ["STRUCT_DECL"]],
            [["EXPR"], ["RES_STRUCT_DECL"]],

            [["EXPR"], ["INCL_DECL"]],
            [["EXPR"], ["PKG_DECL"]],


            [["PAR_GROUP"], ["PAR_OPEN", "PAR_CLOSE"]],
            [["PAR_GROUP"], ["PAR_OPEN", "EXPR", "PAR_CLOSE"]],
            [["PAR_GROUP"], ["PAR_OPEN", "EXPR_GROUP", "PAR_CLOSE"]],
    
            #[["EXPR_GROUP"], ["EXPR", "SPACE", "EXPR"]],
            #[["EXPR_GROUP"], ["EXPR_GROUP", "SPACE", "EXPR"]],
    
            #[["EXPR_GROUP"], ["EXPR", "EXPR_SEP", "EXPR"]],
            #[["EXPR_GROUP"], ["EXPR_GROUP", "EXPR_SEP", "EXPR"]],
    
            [["EXPR_GROUP"], ["EXPR", "EXPR"]],
            [["EXPR_GROUP"], ["EXPR_GROUP", "EXPR"]],
    
            # blocks
            [["BLOCK"], ["BLOCK_START", "EXPR", "BLOCK_END"]],
            [["BLOCK"], ["BLOCK_START", "EXPR_GROUP", "BLOCK_END"]],

    
            # functions
            [["NAMEPAIR"], ["NAME", "SPACE", "NAME"]],
            [["NAMEPAIR_GROUP"], ["NAMEPAIR", "SPACE", "NAMEPAIR"]],
            [["NAMEPAIR_GROUP"], ["NAMEPAIR_GROUP", "SPACE", "NAMEPAIR"]],
    
            [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR", "SPACE", "SPACE", "NAME", "BLOCK"]],
            [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP", "SPACE", "SPACE", "NAME", "BLOCK"]],

            [["CALL_DECL"], ["CALL", "SPACE", "NAME"]],
            [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAME"]],
            [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR"]],
            [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR", "SPACE", "NAME"]],
            [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP"]],
            [["CALL_DECL"], ["CALL", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP", "SPACE", "NAME"]],

            [["RET_DECL"], ["RET", "SPACE", "NAME"]],
            [["RET_DECL"], ["RET", "SPACE", "EXPR"]],
    
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
            [["FOR_DECL"], ["FOR", "SPACE", "NAMEPAIR", "SPACE", "SPACE", "NAME", "BLOCK"]],

            # structs
            [["STRUCT_DECL"], ["STRUCT", "SPACE", "NAME", "STRUCT_BLOCK"]],
            [["RES_STRUCT_DECL"], ["RES", "SPACE", "STRUCT", "SPACE", "NAME", "STRUCT_BLOCK"]],

            [["STRUCT_BLOCK"], ["BLOCK_START", "NAMEPAIR", "BLOCK_END"]],
            [["STRUCT_BLOCK"], ["BLOCK_START", "STRUCT_DEF_GROUP", "BLOCK_END"]],

            [["STRUCT_DEF_GROUP"], ["NAMEPAIR", "NAMEPAIR"]],
            [["STRUCT_DEF_GROUP"], ["STRUCT_DEF_GROUP", "NAMEPAIR"]],

            # packages
            [["INCL_DECL"], ["INCL", "SPACE", "NAME"]],
            [["INCL_DECL"], ["INCL", "SPACE", "EXPR"]],
            [["PKG_DECL"], ["PKG", "SPACE", "NAME", "BLOCK"]],
        ],
    ]

    all_matches = []
    for order, ruleorder in enumerate(rules):
        all_matches.append( [] )

        for r in ruleorder:
            matches = []

            for i, item in enumerate(buf_slice):
                if i > len(r[1])-1:
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
            if largest == None:
                largest = m
                continue
    
            if len(largest[1]) < len(m[1]):
                largest = m
                continue
    
            if len(largest[1]) == len(m[1]):
                raise Exception(f"Rule mismatch: {largest} {m}")

        # stop at the first order which found some rule
        if largest != None:
            break

    if largest != None:
        #print(f"buf_slice: {buf_slice}\nlargest: {largest}\n")
        return largest

    return None
