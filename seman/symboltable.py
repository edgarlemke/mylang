#!/usr/bin/python3


def symtbl_insert(symtbl, name, type_, pos, scope):

    if not (name in symtbl.keys()):
        symtbl[name] = []

    symtbl[name].append([type_, pos, scope])

    return symtbl
