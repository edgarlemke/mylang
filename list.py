#!/usr/bin/python3


def list_print(l):
    """
    Convert Python3 lists to their printable version in LISP-like format

    Returns a str
    """

    # lists always start with (
    to_print = ["("]

    # iter over list, looking for other lists to convert
    for i in l:
        # if found a list, call this same function to convert it
        if isinstance(i, list):
            cvt = list_print(i)

        # if didn't find a list, quote and escape needed characters
        else:
            str_i = str(i)

            quoted_chars = ["(", ")", " ", "\""]
            esc_chars = ["\""]

            cvt_li = []
            quote = False
            # iter over string checking for quoted and escaped chars
            for index, ch in enumerate(str_i):
                # detect need for quotes
                if ch in quoted_chars:
                    quote = True

                # escape char
                if ch in esc_chars and str_i[index - 1] != "\\":
                    ch = f"\\{ch}"

                cvt_li.append(ch)

            # add quotes if needed
            if quote:
                cvt_li = ["\""] + cvt_li + ["\""]

            # join back into str
            cvt = "".join(cvt_li)

        # if there's previous content in to_print list, add a space before our
        # new content
        if len(to_print) > 1 and to_print[len(to_print) - 1] != ")":
            to_print.append(" ")

        # append the converted new content to to_print
        to_print.append(cvt)

    # lists always end with )
    to_print.append(")")

    # join the to_print list into a str
    r = "".join(to_print)

    return r
