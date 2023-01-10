#!/usr/bin/python3


def parse (token_list) :

#    parsetree = _get_bottom_up_order(token_list)
#    #print(parsetree)
#
#    #parsetree = _parse_lit_tokens(parsetree)
#    treecp = parsetree.copy()[1:]
#    print(treecp)
#    print(len(treecp))
#
#    for oi, order_list in enumerate(treecp):
#        for i, li in enumerate(order_list):
#            rule = _match(li)
#
#            new = rule[0]
#            new.append(li)
#
#            treecp[oi][i] = new
#
#            #print(oi+1)
#            #treecp[oi+1]
#
#    print(treecp)


    buf = []
    token_ct = 0
    while True:
        # check token_ct
        if token_ct == len(token_list):
            break

        # shift
        buf.append(token_list[token_ct])

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

                # reduce
                #
                # pop matching slice from buffer
                popped = []
                for j in range(i, i+len(rule[1])):
                    #print(f"f {j} buf {buf}")
                    popped.append( buf.pop(i) )
                #
                # substitute the slice with target
                inplace = rule[0]
                inplace.append(popped)
                buf.insert(i, inplace)
                #

                break

            # if found no rule in buffer slices break out of while loop that looks for rules
            if not found_rule:
                break

        token_ct += 1

    parsetree = buf
    return parsetree


def _get_bottom_up_order (token_list) :
    bottom_up_order = {}

    def _follow(li, depth):

        if depth not in bottom_up_order.keys():
            bottom_up_order[depth] = []

        bottom_up_order[depth].append(li)

        for l in li:
            if type(l) != list:
                continue

            _follow(l, depth+1)

    _follow(token_list, 0)

    # reverse
    rev_bottom_up_order = []
    rev = list(bottom_up_order.keys())
    rev.reverse()

    for i, key in enumerate(rev):
        rev_bottom_up_order.append( bottom_up_order[key] )
    bottom_up_order = rev_bottom_up_order

    return bottom_up_order



#def _parse_lit_tokens (parsetree) :
#    lit_tokens = ["PAR_OPEN", "PAR_CLOSE", "SPACE", "QUOTE", "VALUE"]
#
#    for order in parsetree.keys():
#        order_li = parsetree[order]
#
#        for li in order_li:
#            if li[0] in lit_tokens:
#                lit_li = ["LIT", li]
#
#                for ho_li_index, ho_li in enumerate( parsetree[order+1].copy() ):
#                    for ho_li_ch_index, ho_li_ch in enumerate(ho_li):
#                        if ho_li_ch == li:
#                            parsetree[order+1][ho_li_index][ho_li_ch_index] = lit_li
#
#    return parsetree


def _match (buf_slice):
    #print(f"buf_slice: {buf_slice}")
    rules = [
        [["EXPR"],["QUOTE", "VALUE", "QUOTE"]],
    ]

    for r in rules:
        matches = []

        for i, item in enumerate(buf_slice):
            if item[0] == r[1][i]:
                matches.append(True)

        if all(matches) and len(matches) == len(r[1]):
            return r

    #raise Exception(f"No parser rule found for list: {buf_slice}")
    return False
