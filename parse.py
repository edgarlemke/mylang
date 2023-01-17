#!/usr/bin/python3


def parse (token_list, root) :

    token_rule_prec = [
            [ ["ELSE"], [["IF_DECL"],["IF", "SPACE", "NAME", "BLOCK"]] ],
            ]

    buf = []
    token_ct = 0

    last_found_rule = None
    lookahead = token_list[token_ct]
    while token_ct < len(token_list):

        # shift
        buf.append(lookahead)
        print(f"buf {buf}")

        # update lookahead
        if token_ct+1 == len(token_list):
            lookahead = None
        else:
            lookahead = token_list[token_ct+1]
        
        force_prec_shift = False

        # look for rule
        while True:
            found_rule = False

            # iters over buffer slices looking for rule
            for i in range(0, len(buf)):
                buf_slice = buf[i:]
                rule = _match(buf_slice)

                # if didn't find matching rule, skip
                if rule == False:
                    continue

                # ... found matching rule
                found_rule = True
                #print(f"match - rule {rule} buf_slice {buf_slice}")

                # find token rule prec
                for precrule in token_rule_prec:
                    precrule_token, precrule_target = precrule

                    #print(f"precrule_target: {precrule_target}  rule: {rule}    {precrule_target == rule}")
                    #print(f"precrule_token: {precrule_token} lookahead: {lookahead}     {precrule_token[0] == lookahead[0]}")
                    if (precrule_target == rule) and (precrule_token[0] == lookahead[0]):
                        #print("Bingo!")
                        force_prec_shift = True
                        found_rule = False
                        #print()
                        break
                    #print()

                if force_prec_shift:
                    #print("break 1")
                    break

                # reduce
                #
                # pop matching slice from buffer
                popped = []
                for j in range(i, i+len(rule[1])):
                    #print(f"f {j} buf {buf}")
                    popped.append( buf.pop(i) )
                #
                # substitute the slice with target
                inplace = rule[0].copy()
                inplace.append(popped)
                buf.insert(i, inplace)
                #

                break

            if force_prec_shift:
                #print("break 2")
                break

            # if found no rule in buffer slices break out of while loop that looks for rules
            if not found_rule:

                all_tokens_buffered = token_ct + 1 == len(token_list)
                if not all_tokens_buffered:
                    break

                # ... all tokens have been buffered

                buff_len_one = len(buf) == 1
                buff_expr = buf[0][0] == root
                if not (buff_len_one and buff_expr):
                    raise Exception(f"Invalid syntax!\nlast_found_rule: {last_found_rule}\n\nbuf: {buf}")


                break
            
            else:
                last_found_rule = inplace

        token_ct += 1

    parsetree = buf
    return parsetree


def _match (buf_slice):
    rules = [
            [
        [["IF_ELSE_DECL"], ["IF", "SPACE", "NAME", "BLOCK", "ELSE", "BLOCK"]],
            ],
            [
        [["EXPR"], ["INT"]],
        [["EXPR"], ["NOP"]],
        [["EXPR"], ["QUOTE", "QVALUE", "QUOTE"]],
        [["EXPR"], ["PAR_GROUP"]],
        [["EXPR"], ["FN_DECL"]],

        [["EXPR"], ["IF_DECL"]],
        [["EXPR"], ["IF_ELSE_DECL"]],

        [["PAR_GROUP"], ["PAR_OPEN", "PAR_CLOSE"]],
        [["PAR_GROUP"], ["PAR_OPEN", "EXPR", "PAR_CLOSE"]],
        [["PAR_GROUP"], ["PAR_OPEN", "EXPR_GROUP", "PAR_CLOSE"]],

        #[["EXPR_GROUP"], ["EXPR", "SPACE", "EXPR"]],
        #[["EXPR_GROUP"], ["EXPR_GROUP", "SPACE", "EXPR"]],

        #[["EXPR_GROUP"], ["EXPR", "EXPR_SEP", "EXPR"]],
        #[["EXPR_GROUP"], ["EXPR_GROUP", "EXPR_SEP", "EXPR"]],

        [["EXPR_GROUP"], ["EXPR", "EXPR"]],
        [["EXPR_GROUP"], ["EXPR_GROUP", "EXPR"]],

        # block related
        [["BLOCK"], ["BLOCK_START", "EXPR", "BLOCK_END"]],
        [["BLOCK"], ["BLOCK_START", "EXPR_GROUP", "BLOCK_END"]],

        # fn related
        [["NAMEPAIR"], ["NAME", "SPACE", "NAME"]],
        [["NAMEPAIR_GROUP"], ["NAMEPAIR", "SPACE", "NAMEPAIR"]],
        [["NAMEPAIR_GROUP"], ["NAMEPAIR_GROUP", "SPACE", "NAMEPAIR"]],

        [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR", "SPACE", "SPACE", "NAME", "BLOCK"]],
        [["FN_DECL"], ["FN", "SPACE", "NAME", "SPACE", "SPACE", "NAMEPAIR_GROUP", "SPACE", "SPACE", "NAME", "BLOCK"]],

        # if
        [["IF_DECL"], ["IF", "SPACE", "NAME", "BLOCK"]],
        ],
    ]

    all_matches = []
    for order, ruleoder in enumerate(rules):
        for r in ruleorder:
            matches = []
    
            for i, item in enumerate(buf_slice):
                if i > len(r[1])-1:
                    break
    
                if item[0] == r[1][i]:
                    matches.append(True)
    
            if all(matches) and len(matches) == len(r[1]):
                all_matches.append(r)
    
    #if len(all_matches):
    #    print(f"all_matches: {all_matches}")


    largest = None
    for m in all_matches:
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

    return False
