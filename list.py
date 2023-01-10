#!/usr/bin/python3


def list_print (l) :
    """
    Convert Python3 lists to their printable version in LISP-like format

    Returns a str
    """

    # lists always start with (
    to_print = ["("]

    # iter over list, looking for other lists to convert
    for i in l:
        # if found a list, call this same function to convert it
        if type(i) == list:
            cvt = list_print(i)

        # if didn't find a list, put the value between quotes for printing
        else:
            cvt = "\"%s\"" % str(i)

        # if there's previous content in to_print list, add a space before our new content
        if len(to_print) > 1 and to_print[len(to_print)-1] != ")":
            to_print.append(" ")

        # append the converted new content to to_print
        to_print.append(cvt)

    # lists always end with )
    to_print.append(")")

    # join the to_print list into a str
    r = "".join(to_print)

    return r
