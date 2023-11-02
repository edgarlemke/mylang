#!/usr/bin/python3
# coding: utf-8

import argparse
import re

import list as list_
from shared import debug


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
    ["COMMA", ","],

    ["LIT", r'[^()\s\n\t#,"]+'],
    # ["LIT", "\\w+"],
    # ["LIT", "[0-9]+\\.[0-9]+"],
    # ["LIT", "\\+|\\'|\\=|\\-|\\*|\\/|\\%|\\<|\\>|\\^|\\!"],
]


def tokenize(code, autolist=True):
    """
    Tokenize code according to rules.

    Returns a list
    """

    token_list = _match_tokens(code)
    #    debug(f"tokenize():  token_list after _match_tokens: {token_list}")

    if len(token_list) == 0:
        raise Exception("No token match!")

    # match literals tokens
    token_list = _match_lit_tokens(token_list, code)
    #    debug(f"tokenize():  token_list after _match_lit_tokens: {token_list}")

    # sort out duplicated tokens
    token_list = _decide_dup_tokens(token_list, ["LIT"])
    #    debug(f"tokenize():  token_list after _decide_dup_tokens: {token_list}")

    # sort token_list list by start position of the token
    token_list.sort(key=lambda x: x[2])
    #    debug(f"tokenize():  token_list after sort: {token_list}")

    token_list = _remove_comments(token_list)
    debug(f"tokenize():  token_list after _remove_comments: {token_list}")

    # sort autolist if needed
    if autolist:
        _check_indentation(token_list)

        token_list = _sort_autolist(token_list)
        debug(f"tokenize():  token_list after _sort_autolist: {token_list}")

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
    # print(f"token_list: {token_list}")
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

    # print(f"quotes: {quotes}")

    # iter over every two quotes
    to_add = []
    i = 0
    while i < len(quotes):
        quote = quotes[i]
        # print(f"i: {i} quote: {quote}")

        # get initial lit start and end
        lit_start = quote[2] + 1
        lit_end = len(code)
        # print(f"lit_start: {lit_start} lit_end: {lit_end}")

        # if there's a next QUOTE, get a new literal end
        # print(f"len(quotes) > (i + 1) - {len(quotes)} > {(i + 1)}")
        if len(quotes) > (i + 1):
            # print(">")
            end_quote = quotes[i + 1]
            lit_end = end_quote[3] - 1

        # print(f"new lit_end: {lit_end} {lit_start}")

        value = code[lit_start: lit_end]
        token = ["TOKEN", "LIT", lit_start, lit_end, value]
        to_add.append(token)

        i += 2

    for lit_token in to_add:
        token_list.append(lit_token)

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

            if token2[1] == "SPACE" and token[1] == "LIT" and token[2] <= token2[2] and token[3] >= token2[3]:
                rem(token2)

            if token2[1] == "QUOTE":
                rem(token2)

    return token_list_iter


def _check_indentation(token_list):
    debug(f"_check_indentation():  token_list: {token_list}")

    lines = []
    buf = []

    for token in token_list:
        if token[1] == "BREAKLINE":
            lines.append(buf.copy())
            buf = []
        else:
            buf.append(token)

    if len(buf) > 0:
        lines.append(buf.copy())

    debug(f"_check_indentation():  lines: {lines}")

    for line in lines:
        debug(f"_check_indentation():  line: {line}")

        for token in line:
            if token[1] == "SPACE":
                raise Exception("Invalid space at beginning of line")

            elif token[1] == "TAB":
                continue

            else:
                break


def _sort_autolist(token_list):
    debug(f"\n\n_sort_autolist()")
    # debug(f"\n\n_sort_autolist():  token_list: {token_list}")

    # add breaklines in the end, so the user doesn't need to do it ;)
    for i in range(0, 2):
        token_list.append(["TOKEN", "BREAKLINE"])

    debug(f"""_sort_autolist():  old par_open_nodes: {[n for n in token_list if n[1] == "PAR_OPEN"]} {len([n for n in token_list if n[1] == "PAR_OPEN"])}\n""")
    debug(f"""_sort_autolist():  old par_close_nodes: {[n for n in token_list if n[1] == "PAR_CLOSE"]} {len([n for n in token_list if n[1] == "PAR_CLOSE"])}""")

    # split tokens in lines based on BREAKLINEs
    lines = {}
    line_ct = 0
    for token in token_list:
        if line_ct not in lines.keys():
            lines[line_ct] = []

        if token[1] != "BREAKLINE":
            lines[line_ct].append(token)
        else:
            line_ct += 1

    # iter over lines
    blocked_lines = []
    popped = []
    level = 0
    mark_block_end = False
    for ln, ln_content in lines.items():
        empty_line = len(ln_content) == 0
        tilend = [len(lines[i]) == 0 for i in range(ln, len(lines) - 1)]
        eof = all(tilend)

        # count tabs and remove them
        tabs_in_line = []
        for token in ln_content.copy():
            if token[1] == "TAB":
                tabs_in_line.append(token)
                ln_content.remove(token)

        # if the line still has content
        if len(ln_content) > 0:

            # NOTE: the "text" parts MUST be different

            # if the line doesn't start with PAR_CLOSE
            if ln_content[0][1] != "PAR_CLOSE":
                # add PAR_OPEN at the beginning of the line
                ln_content.insert(0, ["TOKEN", "PAR_OPEN", '', '', "(", f"start line {ln+1}"])

                # add PAR_CLOSE at the end of the line
                ln_content.append(["TOKEN", "PAR_CLOSE", '', '', ")", f"end line {ln+1}"])

        # if starting a new level with tab
        start_block = False
        end_block = False
        if len(tabs_in_line) == level + 1:
            level += 1

            # remove PAR_CLOSE from previous line
            pop_index = len(blocked_lines[ln - 1]) - 1
            pop_item = blocked_lines[ln - 1].pop(pop_index)
            popped.append(pop_item)

            debug(f"_sort_autolist():  pop_index: {pop_index}  pop_item: {pop_item}")

            # insert PAR_OPEN at the beginning of current line
            insert_item = ["TOKEN", "PAR_OPEN", '', '', "(", f"start blk level {level} line {ln+1}"]
            debug(f"_sort_autolist():  inserting {insert_item} at 0")
            ln_content.insert(0, insert_item)

            start_block = True

        # elif decreasing level receding tabs
        elif len(tabs_in_line) < level:
            debug(f"\n_sort_autolist():  len(tabs_in_line) < level: {len(tabs_in_line)} < {level}")

            if (empty_line and eof) or (not empty_line and not eof):
                # get difference between current level and tabs in line
                diff = level - len(tabs_in_line)
                debug(f"_sort_autolist():  diff: {diff}")

                for p in popped:
                    debug(f"_sort_autolist():  popped: {p}")

                # for every level in difference
                range_end = diff * 2
                # if eof:
                #    range_end += 1
                for i in reversed(range(0, range_end)):
                    debug(f"_sort_autolist():  i: {i}")

                    # get sub for identification
                    sub = level - i  # - 1

                    # insert PAR_CLOSE at the beginning of current line
                    insert_item = ["TOKEN", "PAR_CLOSE", '', '', ")", f"end blk sub {sub} line {ln+1}"]
                    debug(f"_sort_autolist():  inserting {insert_item} at 0")
                    ln_content.insert(0, insert_item)

                level -= diff
                end_block = True

            # else:
            #    print(f"SOME ELSE HERE {ln+1}")

        blocked_lines.append(ln_content)

    new_token_list = []
    for bln in blocked_lines:
        new_token_list += bln

    # debug(f"_sort_autolist():  new_token_list: {new_token_list}")

    debug(f"""_sort_autolist():  par_open_nodes: {[n for n in new_token_list if n[1] == "PAR_OPEN"]} {len([n for n in new_token_list if n[1] == "PAR_OPEN"])}\n""")
    debug(f"""_sort_autolist():  par_close_nodes: {[n for n in new_token_list if n[1] == "PAR_CLOSE"]} {len([n for n in new_token_list if n[1] == "PAR_CLOSE"])}\n""")

    return new_token_list


if __name__ == "__main__":

    # set up command line argument parsing
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--src")
    group.add_argument("--expr")

    parser.add_argument("--disable-autolist", action="store_false")

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
    token_list = tokenize(expr, autolist=not (args.disable_autolist))

    print(list_.list_print(token_list))
