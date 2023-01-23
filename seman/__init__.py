#!/usr/bin/python3

from .symboltable import symtbl_insert

types = [
    ["ui8", 1],
    ["i8", 1],
    ["byte", 1],
]


def get_symtbl (s_tree):
    #print(s_tree)

    symtbl = {}
    scopes = []


    def iterup (i):
        # get node
        node = s_tree[i]

        # get node's parent node
        parent_node_index = node[1]
        if parent_node_index == None:
            return 0

        parent = s_tree[ parent_node_index ]

        # check if scope node matches parent node, if it does return scope index
        for si, s in enumerate(scopes):
            scope_node_index = s[0]
            if parent_node_index == scope_node_index:
                return si

        return iterup(parent_node_index)


    for i, node in enumerate(s_tree):
        #print(f"{i} - {node}")

        cat = node[0]
        if cat == "FN_DECL":
            cat, parent, children = node

            indexes = [ ch for ch in children if s_tree[ch][0] == "NAME" ]
            names = [ s_tree[ch] for ch in children if s_tree[ch][0] == "NAME" ]
            #print(names)

            sym_name = names[0][1]
            fn_type = names[len(names)-1][1] 
            sym_t = ["fn", fn_type ]
            sym_pos = indexes[0] #names[0][2]

            #print(sym_name)
            #print(sym_pos)
            #print(sym_t)

            # find function's parent scope
            sym_scope = iterup(i)

            # setup function's children's scope
            new_scope = [i, cat, sym_scope]
            scopes.append(new_scope)

            symtbl_insert(symtbl, sym_name, sym_t, sym_pos, sym_scope)

            # handle arguments
            #
            args_indexes = indexes[1:-1]
            args = names[1:-1]
            arg_pairs = []
            pair = []
            #
            # get names back into pairs
            j = 0
            while j < len(args):
                pair.append( args[j] )

                if len(pair) == 2:
                    arg_pairs.append( [pair, args_indexes[j]] )
                    pair = []

                j+= 1
            for pair_index in arg_pairs:
                arg, arg_index = pair_index
                
                arg_sym_name = arg[1][1]
                arg_sym_t = [ "fn_arg", arg[0][1] ]
                arg_sym_pos = arg_index

                symtbl_insert(symtbl, arg_sym_name, arg_sym_t, arg_sym_pos, len(scopes)-1)
            #

        elif cat in ["SET_DECL", "MUT_DECL"]:
            # extract symbol info
            cat, parent, children = node
            sym_name = s_tree[children[0]][1]
            if cat == "MUT_DECL":
                sym_t = ["mut"]
            else:
                sym_t = ["set"]
            sym_t.append( s_tree[children[1]][1] )
            sym_pos = children[0]
            # find parent scope
            sym_scope = iterup(i)
            # insert symbol in symbol table
            symtbl_insert(symtbl, sym_name, sym_t, sym_pos, sym_scope)

        elif cat == "PKG_DECL":
            # extract symbol info
            cat, parent, children = node
            sym_name = s_tree[children[0]][1]
            sym_t = ["pkg"]
            sym_pos = children[0]
            # insert symbol in symbol table
            symtbl_insert(symtbl, sym_name, sym_t, sym_pos, None)

            # setup scope
            new_scope = [i, cat, None]
            scopes.append(new_scope)

    return (symtbl, scopes)


def _get_refs (s_tree, symtbl) :
    name_indexes = [i for i, node in enumerate(s_tree) if node[0] == "NAME"]

    # remove references that match symbols in symbol table
    for sym_key in symtbl:
        sym_list = symtbl[sym_key]

        for sym in sym_list:
            sym_pos = sym[1]

            for index in name_indexes:
                if sym_pos == index:
                    name_indexes.remove(index)

    # remove references that match types
    for index in name_indexes.copy():
        for type_ in types:
            if s_tree[index][1] == type_[0]:
                name_indexes.remove(index)

    return name_indexes


def check (s_tree, symtbl, scopes):
    refs = _get_refs(s_tree, symtbl)

    _check_set_mut(s_tree, symtbl, scopes)

# check single set per name at every scope
def _check_set_mut(s_tree, symtbl, scopes):

    for sym_name in symtbl:
        sym_list = symtbl[sym_name]

        # check for two SETs on the same name, in the same scope
        set_ = []
        for li in sym_list:
            if li[0][0] != "set":
                continue

            scope_node_index = li[2]
            if scope_node_index in set_:
                raise Exception(f"Immutable name already set before: {sym_name}")
            set_.append(scope_node_index)

        # check for SETs on a name already set by MUT, and vice-versa, in the same scope
        for li in sym_list:
            if li[0][0] != "set":
                continue

            for li2 in sym_list:
                if li2[0][0] != "mut":
                    continue

                if li[2] == li2[2]:
                    raise Exception(f"SET/MUT conflict: {sym_name}")
        
        # check for SETs and MUTs on name already set in function header or higher scopes
        def iterup(scope):
            if scope == None:
                return False

            scope_parent = scope[2]
            if scope_parent == None:
                return False

            match = False
            for li2 in sym_list:
                if li[0][0] not in ["set", "mut"] or li == li2:
                    continue

                # set variables to ease understanding
                target_sym_scope = li2[2]
                if target_sym_scope == scope_parent:
                    match = True

            if match:
                return match
            else:
                return iterup(scopes[scope_parent])


        # for each symbol of the same name
        for li in sym_list:
            if li[0][0] not in ["set", "mut"]:
                continue

            # get each symbol's scope
            sym_scope = li[2]
            scope = scopes[sym_scope]

            i = iterup(scope)
            if i:
                raise Exception(f"SET/MUT conflict in higher scope: {sym_name}")

    return True
