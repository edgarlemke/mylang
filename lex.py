#!/usr/bin/python3
# coding: utf-8

import argparse
import re

import list as list_



def tokenize (code):
    """
    Tokenize code according to rules.

    Returns a list
    """

    # return variable
    token_list = []

    # rules list
    # structure of rules is a list: ["TOKEN_CAT", "REGEXP"]
    # TOKEN_CAT is the token category keyword
    # REGEXP is the regular expression for matching tokens
    rules_list = [
        ["PAR_OPEN", "\("],
        ["PAR_CLOSE", "\)"],
        ["SPACE", " "],
        ["BREAKLINE", "\n"],
        ["QUOTE", "\""],
        ["VALUE", "\w+"],
    ]

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

        # if start is different from end, add quoted VALUE token to list
        if value_start != value_end:
            value = code[value_start : value_end]
            token = ["VALUE", value_start, value_end, value]
            token_list.append(token)

        i += 2

    # remove tokens with same start and end (meant for VALUE tokens)
    cp = token_list.copy()
    for token in cp:
        for token2 in cp:
            # change only different tokens, skip non-VALUE tokens
            if id(token) == id(token2) or token[0] != "VALUE":
                continue

            # token[0] is always "VALUE"...

            # remotions for tokens of same start and end
            if (token[1] == token2[1]) and (token[2] == token2[2]):
                # remove duplicated VALUE tokens
                if token2[0] == "VALUE":
                    cp.remove(token2)

                # remove SPACE, PAR_OPEN and PAR_CLOSE tokens that correspond to VALUE tokens between QUOTE tokens
                if token2[0] in ['SPACE','PAR_OPEN','PAR_CLOSE']:
                    cp.remove(token2)
            
            ## remove QUOTE tokens that correspond to scaped quotes between QUOTE tokens
            if token2[0] == "QUOTE" and token[1] == token2[1]-1 and token[2] == token2[2]:
               cp.remove(token2)
    token_list = cp

    # sort token_list list by start position of the token
    token_list.sort(key=lambda x: x[1]) 

    # check for non-tokenized ranges
    _check_nontokenized(token_list, code)

    # remove breaklines
    cp = token_list.copy()
    for token in cp:
        if token[0] == "BREAKLINE":
            cp.remove(token)
    token_list = cp

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
        
    # generate token list from content variable
    token_list = tokenize(expr)

    print( list_.list_print(token_list) )
