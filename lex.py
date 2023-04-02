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

    token_list = _sort_indentation(token_list)


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


def _sort_indentation (token_list) :
    # add breaklines in the end, so the programmer doesn't need to do it ;)
    for i in range(0,2):
        token_list.append(["BREAKLINE"])

    #print(f"token_list: {token_list}")

    # split tokens in lines based on BREAKLINEs
    lines = {}
    line_ct = 0
    for token in token_list:
        if line_ct not in lines.keys():
            lines[line_ct] = []

        if token[0] != "BREAKLINE":
            lines[line_ct].append(token)
        else:
            line_ct += 1

    new_token_list = []
    level = 0
    for ln, ln_content in lines.items():
        #empty_line = len(ln_content) == 0

        tabs_in_line = []
        for token in ln_content.copy():
            if token[0] == "TAB":
                tabs_in_line.append(token)
                ln_content.remove(token)

        #print(f"previous level: {level}")
        #print(f"tabs_in_line {ln}: {tabs_in_line}")
        if len(tabs_in_line) == level+1:
            #print(f"ADD BLOCK_START {level}")
            ln_content.insert(0, ["BLOCK_START", level])
            level += 1

        elif len(tabs_in_line) < level:
            diff = level-len(tabs_in_line)

            for i in reversed(range(0, diff)):
                sub = level - i - 1
                #print(f"ADD BLOCK_END {sub}")
                #print(f"level {level} diff {diff} i {i}")
                ln_content.insert(0, ["BLOCK_END", sub])
            
            level -= diff
        #print(f"current level: {level}\n")

        new_token_list += ln_content

    return new_token_list


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
