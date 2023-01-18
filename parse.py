#!/usr/bin/python3


def parse (token_list, root) :

    buf = []
    token_ct = 0

    last_found_rule = None
    lookahead = token_list[token_ct]
    while token_ct < len(token_list):

        # shift
        buf.append(lookahead)
        #print(f"buf {buf}")

        # update lookahead
        if token_ct+1 == len(token_list):
            lookahead = None
        else:
            lookahead = token_list[token_ct+1]
        
        # look for rules and reduce as long as needed
        while True:
            match = _find_match(buf, lookahead)
            #print(f"match {match}")

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
        [ ["ELIF"], [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]] ],
    ]

    match = None

    # iters over buffer slices looking for rule
    for i in range(0, len(buf)):
        buf_slice = buf[i:]
        #print(f"buf_slice {buf_slice}")
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
            if (prec_rule_target == rule) and ((prec_rule_token[0] == lookahead[0]) or (prec_rule_token[0] in [b[0] for b in buf_slice])):
                #print("Bingo!")
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
            [["IF_ELSE_DECL"], ["IF", "SPACE", "NAME", "BLOCK", "ELSE", "BLOCK"]],
            [["IF_ELIF_DECL"], ["IF", "SPACE", "NAME", "BLOCK", "ELIF", "NAME", "BLOCK"]],
        ],
        [
            # expressions
            [["EXPR"], ["INT"]],
            [["EXPR"], ["FLOAT"]],
            [["EXPR"], ["NOP"]],
            [["EXPR"], ["QUOTE", "QVALUE", "QUOTE"]],

            [["EXPR"], ["PAR_GROUP"]],
            
            [["EXPR"], ["FN_DECL"]],
            [["EXPR"], ["CALL_DECL"]],
            [["EXPR"], ["RET_DECL"]],
    
            [["EXPR"], ["SET_DECL"]],
            [["EXPR"], ["MUT_DECL"]],

            [["EXPR"], ["IF_DECL"]],
            [["EXPR"], ["IF_ELSE_DECL"]],
            [["EXPR"], ["WHILE_DECL"]],
            [["EXPR"], ["FOR_DECL"]],
    
            [["EXPR"], ["STRUCT_DECL"]],
            [["EXPR"], ["RES_STRUCT_DECL"]],

            [["EXPR"], ["INCL_DECL"]],


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

            [["RET_DECL"], ["RET", "SPACE", "NAME"]],
    
            # variables and constants
            # set
            [["SET_DECL"], ["SET", "SPACE", "NAMEPAIR", "SPACE", "EXPR"]],
            # mut
            [["MUT_DECL"], ["MUT", "SPACE", "NAMEPAIR", "SPACE", "EXPR"]],

            # control flux
            # if
            [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]],
            # while
            [["WHILE_DECL"], ["WHILE", "SPACE", "NAME", "BLOCK"]],
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
    
            if all(matches) and len(matches) == len(r[1]):
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

    if largest != None:
        #print(f"buf_slice: {buf_slice}\nlargest: {largest}\n")
        return largest

    return None
