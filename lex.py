#!/usr/bin/python3
# coding: utf-8

import argparse
import re

import list as list_



# rules list
# structure of rules is a list: ["TOKEN_CAT", "REGEXP"]
# TOKEN_CAT is the token category keyword
# REGEXP is the regular expression for matching tokens
rules_list = [
    ["PAR_OPEN", "\("],
    ["PAR_CLOSE", "\)"],
    ["SPACE", " "],
    ["BREAKLINE", "\n"],
    ["TAB", "\t"],
    ["QUOTE", "\""],

    ["NAME", "\w+"],

    ["INT", "[0-9]+"],
    ["FLOAT", "[0-9]+\.[0-9]+"],
    ["BOOL", "true|false"],
    ["STRUCT", "struct"],

    ["NOP", "nop"],

    #["PKG", "pkg"],
    ["INCL", "incl"],

    ["FN", "fn"],
    ["CALL", "call"],
    ["RET", "ret"],

    ["SET", "set"],
    ["MUT", "mut"],

    ["RES", "res"],

    ["IF", "if"],
    ["ELSE", "else"],
    ["ELIF", "elif"],

    ["WHILE", "while"],

    ["FOR", "for"],

    ["TYPEDEF", "typedef"],
]


def tokenize (code):
    """
    Tokenize code according to rules.

    Returns a list
    """

    token_list = _match_tokens(code)
    
    if len(token_list) == 0:
        raise Exception("No token match!")


    token_list = _match_value_tokens(token_list, code)
    token_list = _decide_dup_tokens(token_list)

    # sort token_list list by start position of the token
    token_list.sort(key=lambda x: x[1]) 

    # check for non-tokenized ranges
    _check_nontokenized(token_list, code)

    _sort_identation(token_list)


    return token_list


def _match_tokens (code) :
    token_list = []


    # iter over rules list matching tokens
    for rule in rules_list:
        # shortcut variables
        token_cat = rule[0]
        regexp = rule[1]

        # find all matches for regexp in code
        matches = re.finditer(regexp, code, flags= re.UNICODE)
        # iter over matches
        for match in matches:
            # extract start, end and value
            start = match.span()[0]
            end = match.span()[1]
            value = match.group()

            # register the info as a found token
            token = [token_cat, start, end, value]
            #print(token)
            token_list.append(token)

    return token_list


def _match_value_tokens (token_list, code) :
    # match VALUE tokens
    quotes = []
    for token in token_list:
        # skip all non-QUOTE tokens
        if token[0] != "QUOTE":
            continue

        # skip escaped QUOTE tokens, convert them to VALUE tokens
        # keeping escaped \ char as VALUE
        if code[ token[1]-1 ] == "\\" and code[ token[1]-2 ] != "\\":
            #token[0] = "VALUE"
            continue

        quotes.append(token)

    # iter over every two quotes
    i = 0
    while i < len(quotes):
        quote = quotes[i]

        # get initial value start and end
        value_start = quote[2]
        value_end = len(code)

        # if there's a next QUOTE, get a new value end
        if len(quotes) > (i+1):
            end_quote = quotes[i+1]
            value_end = end_quote[1]

        # if start is different from end, add QVALUE token to list
        if value_start != value_end:
            value = code[value_start : value_end]
            token = ["QVALUE", value_start, value_end, value]
            token_list.append(token)

        i += 2

    return token_list


def _decide_dup_tokens (token_list) :
    token_list_iter = token_list.copy()
    removed = []
    for token in token_list_iter:
        for token2 in token_list_iter:
            # skip already removed tokens
            if token in removed or token2 in removed:
                continue

            # change only different tokens
            if id(token) == id(token2):
                continue

            def rem (t):
                token_list.remove(t)
                removed.append(t)


            if (token[1] <= token2[1]) and (token[2] >= token2[2]):

                if token[0] == "QVALUE":
                    if token2[0] in ["PAR_OPEN", "PAR_CLOSE", "SPACE"]:
                        rem(token2)

                if token2[0] == "NAME":
                    rem(token2)

                if (token[1] == token2[1] and token[2] > token2[2]) or (token[1] < token2[1] and token[2] == token2[2]):
                    rem(token2)



    return token_list



def _check_nontokenized (token_list, code) :
    last_t = None
    for t in token_list:
        t_start = int(t[1])

        # check for the start
        if last_t == None:
            if t_start > 0:
                ntrange = code[0:t_start]
                raise Exception(f"Non-tokenized range at start: 0 {t_start}  \"{ntrange}\"\ntoken_list: {token_list}")
        
        # check for the middle
        else:
            last_t_end = int(last_t[2])

            if t_start > last_t_end:
                ntrange = code[last_t_end:t_start]
                raise Exception(f"Non-tokenized range at middle: {last_t_end} {t_start}  \"{ntrange}\"\ntoken_list: {token_list}")

        last_t = t

    # check for the end
    t_end = int(t[2])
    code_end = len(code)
    if t_end < code_end:
        ntrange = code[t_end:code_end]
        raise Exception(f"Non-tokenized range at end: {t_end} {code_end}  \"{ntrange}\"\ntoken_list: {token_list}")


def _sort_identation (token_list) :
    # find contiguous TAB tokens
    found = []
    buf = []
    for t, token in enumerate(token_list):
        if token[0] == "TAB":
            buf.append(t)

        elif t > 0 and token_list[t-1][0] == "TAB":
            found.append([t-len(buf), t])
            buf = []

    #print(f"f {found}")

    # add BLOCK_START and BLOCK_END tokens
    lvl = 0
    last_flen = None
    last_breakline = None

    block_stack = []
    block_counter = 0
    for f in found:
        flen = f[1] - f[0]
        #print(f"f {f} flen {flen} last_flen {last_flen} lvl {lvl}")

        # if is starting a new block
        if flen == lvl + 1:
            #print(f"START")
            token_list.pop(f[0]-1)
            token_list.insert(f[0]-1, ["BLOCK_START", block_counter])

            block_stack.append(block_counter)
            block_counter += 1

            lvl += 1

        #print(f"LVL {lvl}")


        # get next breakline
        next_breakline = None
        def get_breakline () :
            next_breakline = None
            for t, token in enumerate(token_list[f[1]:]) :
                if token[0] == "BREAKLINE":
                    next_breakline = t + f[1]
                    break

            return next_breakline
        next_breakline = get_breakline()


        # if no next breakline found, raise exception
        if next_breakline == None:
            raise Exception ("No next breakline")

        #print(f"next_breakline: {next_breakline} {token_list[next_breakline]}")

        # check for end of block on identation to add the needed BLOCK_END tokens
        #print(f"flen: {flen} - block_stack: {block_stack}")
        #print(f"last_flen > flen: {last_flen} > {flen}")
        if last_flen != None:
            if last_flen > flen:
                #print(f"pop last_breakline: {last_breakline}")
                token_list.pop(last_breakline)

                pos = last_breakline
                for i in range(0, last_flen-flen):
                    #print(f"END i {i}")
                    token_list.insert(pos, ["BLOCK_END", block_stack.pop(), "return"])
                    pos += 1
                    lvl -= 1

        next_breakline = get_breakline()

        # check for end of expression to add BLOCK_END token
        expr_end = next_breakline == len(token_list) - 1
        #print(f"expr_end: next_breakline {next_breakline} len {len(token_list)-1}")
        if expr_end:
            token_list.pop(next_breakline)

            pos = next_breakline
            for i in range(0, len(block_stack)):
                #print(f"END i2 {i}")
                token_list.insert(pos, ["BLOCK_END", block_stack.pop(), "expr_end" ])
                pos += 1
                lvl -= 1

        next_breakline = get_breakline()

        last_flen = flen
        last_breakline = next_breakline

        #print()

    # remove now useless tokens
    if bool(1):
        tlcopy = token_list.copy()
        for t, token in enumerate(tlcopy):
            if token[0] in ["TAB", "BREAKLINE"]:
                token_list.remove(token)

    return token_list


if __name__ == "__main__":

    # set up command line argument parsing
    parser = argparse.ArgumentParser()
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--src")
    group.add_argument("--expr")

    args = parser.parse_args()

    # get the src file argument
    src = args.src

    # get the expr argument
    expr = args.expr

    # extract expr from src file
    if src != None:
        src = str(src)

        # create a file descriptor for the src file
        with open(src,"r") as fd:
        
            # read all content of the file into an variable
            code = fd.readlines()
            expr = "".join(code)

    elif expr != None:
        expr = str(expr)

    elif src == None and expr == None:
        raise Exception("Either --src or --expr argument must be provided")
        
    # generate token list from content variable
    token_list = tokenize(expr)

    print( list_.list_print(token_list) )
