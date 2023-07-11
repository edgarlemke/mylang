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
    ["PAR_OPEN", "\\("],
    ["PAR_CLOSE", "\\)"],
    ["SPACE", " "],
    ["BREAKLINE", "\n"],
    ["TAB", "\t"],
    ["QUOTE", "\""],
    ["HASH", r'#'],

    ["LIT", r'[^()\s\n\t#"]+'],
    # ["LIT", "\\w+"],
    # ["LIT", "[0-9]+\\.[0-9]+"],
    # ["LIT", "\\+|\\'|\\=|\\-|\\*|\\/|\\%|\\<|\\>|\\^|\\!"],
]


def tokenize(code):
    """
    Tokenize code according to rules.

    Returns a list
    """

    token_list = _match_tokens(code)

    if len(token_list) == 0:
        raise Exception("No token match!")

    token_list = _match_lit_tokens(token_list, code)
    token_list = _decide_dup_tokens(token_list, ["LIT"])

    # sort token_list list by start position of the token
    token_list.sort(key=lambda x: x[2])
    token_list = _remove_comments(token_list)
#
#
#    # check for non-tokenized ranges
#    _check_nontokenized(token_list, code)
#
#    token_list = _match_singleline_comments(token_list)
#
    token_list = _sort_indentation(token_list)
#
#    token_list = _sort_op_order(token_list)

    return token_list


def _match_tokens(code):
    token_list = []

    # iter over rules list matching tokens
    for rule in rules_list:
        # shortcut variables
        token_cat = rule[0]
        regexp = rule[1]

        # find all matches for regexp in code
        matches = re.finditer(regexp, code, flags=re.UNICODE)
        # iter over matches
        for match in matches:
            # extract start, end and value
            start = match.span()[0]
            end = match.span()[1]
            value = match.group()

            # register the info as a found token
            token = ["TOKEN", token_cat, start, end, value]
            # print(token)
            token_list.append(token)

    return token_list


def _remove_comments(token_list):
    new_token_list = token_list.copy()

#    hash_tokens = [(index, t) for index, t in enumerate(token_list) if t[1] == "HASH"]
#
#    to_remove = []
#
#    for index, t in hash_tokens:
#        for new_index, token in enumerate(new_token_list[index:]):
#            print(f"token: {token}")
#            #if token[1] == "BREAKLINE":
#            #    to_remove.append([index, new_index])
#            #    break
#
#    print(f"to_remove: {to_remove}")

    # get tokens to remove
    to_remove = []
    remove = False
    for index, t in enumerate(new_token_list):
        # set remove if hash is found
        if t[1] == "HASH":
            remove = True

        if remove:
            to_remove.append(index)

        # unset remove if breakline is found
        if t[1] == "BREAKLINE" and remove:
            remove = False

    # print(f"old token_list: {new_token_list}")
    # print(f"to_remove: {to_remove}")

    # remove tokens in reversed order to preserve indexes
    for i in reversed(to_remove):
        new_token_list.pop(i)

    # print(f"new_token_list: {new_token_list}")

    return new_token_list


def _match_lit_tokens(token_list, code):
    quotes = []
    for token in token_list:
        # skip all non-QUOTE tokens
        if token[1] != "QUOTE":
            continue

        # skip escaped QUOTE tokens, convert them to LIT tokens
        # keeping escaped \ char as LIT
        if code[token[2] - 1] == "\\" and code[token[2] - 2] != "\\":
            continue

        quotes.append(token)

    # iter over every two quotes
    i = 0
    while i < len(quotes):
        quote = quotes[i]

        # get initial lit start and end
        lit_start = quote[2] + 1
        lit_end = len(code)

        # if there's a next QUOTE, get a new literal end
        if len(quotes) > (i + 1):
            end_quote = quotes[i + 1]
            lit_end = end_quote[3] - 1

        # if start is different from end, add LIT token to list
        if lit_start != lit_end:
            value = code[lit_start: lit_end]
            token = ["TOKEN", "LIT", lit_start, lit_end, value]
            token_list.append(token)

        i += 2

    return token_list


def _decide_dup_tokens(token_list, to_remove):
    token_list_iter = token_list.copy()
    removed = []
    for token in token_list:
        for token2 in token_list:
            # skip already removed tokens
            if token in removed or token2 in removed:
                continue

            # change only different tokens
            if id(token) == id(token2):
                continue

            def rem(t):
                # print(f"t: {t}")
                # print(f"token_list_iter: {token_list_iter}")
                # print(f"removed: {removed}")
                if t not in removed:
                    token_list_iter.remove(t)
                    removed.append(t)

#            print(f"token: {token}")
#            print(f"token2: {token2}")

            if (token[2] <= token2[2]) and (token[3] >= token2[3]):

                #                if token[0] == "QVALUE":
                #                    if token2[0] in ["PAR_OPEN", "PAR_CLOSE", "SPACE"]:
                #                        rem(token2)
                #
                if token2[1] in to_remove:
                    rem(token2)

                if (token[2] == token2[2] and token[3] > token2[3]) or (
                        token[2] < token2[2] and token[3] == token2[3]):
                    rem(token2)

    return token_list_iter


# def _match_singleline_comments(token_list):
#    token_list_iter = token_list.copy()
#
#    buf = []
#    comment_lines = []
#    for index, token in enumerate(token_list):
#        if token[0] == "HASH":
#            buf.append(index)
#
#        elif len(buf) > 0:
#            buf.append(index)
#
#        if token[0] == "BREAKLINE" or index == len(token_list) - 1:
#            comment_lines.append(buf.copy())
#            buf = []
#
#    for ln in comment_lines:
#        for token in ln:
#            token_list_iter.remove(token_list[token])
#
#    return token_list_iter


# def _check_nontokenized(token_list, code):
#    last_t = None
#    for t in token_list:
#        t_start = int(t[2])
#
#        # check for the start
#        if last_t is None:
#            if t_start > 0:
#                ntrange = code[0:t_start]
#                raise Exception(
#                    f"Non-tokenized range at start: 0 {t_start}  \"{ntrange}\"\ntoken_list: {token_list}")
#
#        # check for the middle
#        else:
#            last_t_end = int(last_t[3])
#
#            if t_start > last_t_end:
#                ntrange = code[last_t_end:t_start]
#                raise Exception(
#                    f"Non-tokenized range at middle: {last_t_end} {t_start}  \"{ntrange}\"\ntoken_list: {token_list}")
#
#        last_t = t
#
#    # check for the end
#    t_end = int(t[3])
#    code_end = len(code)
#    if t_end < code_end:
#        ntrange = code[t_end:code_end]
#        raise Exception(
#            f"Non-tokenized range at end: {t_end} {code_end}  \"{ntrange}\"\ntoken_list: {token_list}")


def _sort_indentation(token_list):
    # add breaklines in the end, so the programmer doesn't need to do it ;)
    for i in range(0, 2):
        token_list.append(["TOKEN", "BREAKLINE"])

    # print(f"token_list: {token_list}")

    # split tokens in lines based on BREAKLINEs
    lines = {}
    line_ct = 0
    for token in token_list:
        if line_ct not in lines.keys():
            # lines[line_ct] = [["TOKEN", "PAR_OPEN"]]
            lines[line_ct] = []

        if token[1] != "BREAKLINE":
            lines[line_ct].append(token)
        else:
            # lines[line_ct].append(["TOKEN", "PAR_CLOSE"])
            line_ct += 1

    blocked_lines = []
    level = 0
    mark_block_end = False
    for ln, ln_content in lines.items():
        # print(f"ln: {ln} {ln_content}")
        empty_line = len(ln_content) == 0
        tilend = [len(lines[i]) == 0 for i in range(ln, len(lines) - 1)]
        eof = all(tilend)
        # print(eof)

        tabs_in_line = []
        for token in ln_content.copy():
            if token[1] == "TAB":
                tabs_in_line.append(token)
                ln_content.remove(token)

        # print(f"previous level: {level}")
        # print(f"tabs_in_line {ln}: {tabs_in_line}")

        if len(ln_content) > 0:

            # the "text" parts must be different
            ln_content.insert(0, ["TOKEN", "PAR_OPEN", f"start ln {ln}", '', "("])
            ln_content.append(["TOKEN", "PAR_CLOSE", f"end ln {ln}", '', ")"])

        # if starting a new level with tab
        abc = False
        xyz = False
        if len(tabs_in_line) == level + 1:
            # print(f"ADD BLOCK_START {level}")
            # ln_content.insert(0, ["TOKEN", "BLOCK_START", level])
            level += 1

            # remove PAR_CLOSE from previous line
            blocked_lines[ln - 1].pop(len(blocked_lines[ln - 1]) - 1)

            # insert PAR_OPEN at the start of current line
            ln_content.insert(0, ["TOKEN", "PAR_OPEN", 'start blk {level}', '', "("])
            # ln_content.insert(0, ["TOKEN", "SPACE", '?', '?', " "])

            abc = True

        # elif decreasing level receding tabs
        elif len(tabs_in_line) < level:
            if (empty_line and eof) or (not empty_line and not eof):
                diff = level - len(tabs_in_line)

                # ln_content.insert(0, ["TOKEN", "PAR_CLOSE", '#', '#', ")"])
                for i in reversed(range(0, diff + 1)):
                    sub = level - i - 1
                    # print(f"ADD BLOCK_END {sub}")
                    # print(f"level {level} diff {diff} i {i}")
                    # ln_content.insert(0, ["TOKEN", "BLOCK_END"])
                    # blocked_lines[ ln-1 ].append(["TOKEN", "BLOCK_END", 0, 0, ")"])
                    ln_content.insert(0, ["TOKEN", "PAR_CLOSE", f"end blk {sub}", '', ")"])

                level -= diff
                xyz = True

        # if len(ln_content):
        # if not abc:
        #    ln_content.insert(0, ["TOKEN", "PAR_OPEN"])
        # if not xyz:
        #    ln_content.append(["TOKEN", "PAR_CLOSE"])

        blocked_lines.append(ln_content)

    new_token_list = []
    for bln in blocked_lines:
        # print(f"bln: {bln}")
        new_token_list += bln

    # print(f"new_token_list: {new_token_list}")

    return new_token_list


# def _sort_op_order(token_list):
#    tl = token_list.copy()
#
#    xyz = ["'a+'b", "add('a 'b)"]
#
#    return tl


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
    if src is not None:
        src = str(src)

        # create a file descriptor for the src file
        with open(src, "r") as fd:

            # read all content of the file into an variable
            code = fd.readlines()
            expr = "".join(code)

    elif expr is not None:
        expr = str(expr)

    elif src is None and expr is None:
        raise Exception("Either --src or --expr argument must be provided")

    # generate token list from content variable
    token_list = tokenize(expr)

    print(list_.list_print(token_list))
