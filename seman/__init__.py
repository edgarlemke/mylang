#!/usr/bin/python3

from .symboltable import symtbl_insert

# dummy x86_64 type table
types = [
    ["ui8", 1],
    ["i8", 1],
    ["byte", 1],
]


def get_symtbl (s_tree):
    #print(s_tree)

    symtbl = {}
    scopes = [[None, "GLOBAL", None]]


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

#        elif cat == "PKG_DECL":
#            # extract symbol info
#            cat, parent, children = node
#            sym_name = s_tree[children[0]][1]
#            sym_t = ["pkg"]
#            sym_pos = children[0]
#            # insert symbol in symbol table
#            symtbl_insert(symtbl, sym_name, sym_t, sym_pos, None)
#
#            # setup scope
#            new_scope = [i, cat, None]
#            scopes.append(new_scope)

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


def check (s_tree, symtbl, scopes, loaded_functions):
    #refs = _get_refs(s_tree, symtbl)

    # check package-independent SET and MUT rules
    _check_set_mut(s_tree, symtbl, scopes)
    _check_call(s_tree, symtbl, scopes, loaded_functions)

    #_check_set_mut_types()
    #_check_refs()


# check single set per name at every scope
def _check_set_mut(s_tree, symtbl, scopes):

    for sym_name in symtbl:
        sym_list = symtbl[sym_name]

        _check_set_mut_0(sym_list, "set", sym_name)
        _check_set_mut_0(sym_list, "mut", sym_name)

        _check_set_mut_1(sym_list, sym_name)

        _check_set_mut_2(sym_list, scopes, sym_name)

        
    return True


def _check_set_mut_0 (sym_list, arg, sym_name) :
    # check for ARG (mut/set) on a name already set in a function argument
    # or a name already set previously in the scope
    found = []
    for li in sym_list:
        if li[0][0] not in ["fn_arg", arg]:
            continue

        #print(f"li: {li}")
        #print(f"found: {found}")

        scope_node_index = li[2]
        #print(f"scope_node_index: {scope_node_index}")

        if scope_node_index in found:
            raise Exception(f"Immutable name already set before: {sym_name}")
        found.append(scope_node_index)


def _check_set_mut_1 (sym_list, sym_name) :
    # check for SETs on a name already set by MUT, and vice-versa, in the same scope
    for li in sym_list:
        if li[0][0] != "set":
            continue

        for li2 in sym_list:
            if li2[0][0] != "mut":
                continue

            if li[2] == li2[2]:
                raise Exception(f"SET/MUT conflict: {sym_name}")


def _check_set_mut_2 (sym_list, scopes, sym_name) :
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


def _check_call (s_tree, symtbl, scopes, loaded_functions):
    #print(f"loaded_functions: {loaded_functions}")
    #print(symtbl)

    for node in s_tree:
        name = node[0]
        if name != "CALL_DECL":
            continue

        fn_name = s_tree[ node[2][1] ][1]
        #print(f"fn_name: {fn_name}")

        match = False
        for pkg_name in symtbl:
            #print(f"pkg_name: {pkg_name}")
            pkg_syms = symtbl[pkg_name]

            for sym_name in pkg_syms:
                sym_list = pkg_syms[sym_name]

                if sym_list[0][0][0] != "fn":
                    continue

                match = match_fn(node, scopes, symtbl, s_tree, sym_name, pkg_name, loaded_functions)
                #print("match: %s" % match)

                # if matches exit loop
                if match != False:
                    break

            # if matches exit loop
            if match != False:
                break

        # if matches, a function was found, so call is valid
        if match != False:
            continue

        raise Exception(f"Call to undefined function: {fn_name}")


def _incl_pkgs (s_tree) :

    PATH = []

    included_pkgs = []

    for node in s_tree:

        if node[0] != "INCL_DECL":
            continue

        pkg = s_tree[ node[2][0] ]
        if pkg[0] == "NAME":
            pkg_name = pkg[1]
            included_pkgs.append( [pkg_name] )

        else:
            raise Exception("Invalid incl declaration: {pkg}")




def get_types (s_tree, scopes):
    types = []

    for node in s_tree:
        if node[0] != "TYPEDEF_DECL":
            continue

        # Get type name
        type_name = s_tree[ node[2][1] ][1]

        # Get type size
        size_expr = s_tree[ node[2][2] ]
        size_node = s_tree[ size_expr[2][0] ]
        if size_node[0] != "INT":
            raise Exception("Invalid typedef size!")
        type_size = size_node[1]

        # Check if typedef is declared in global scope
        if not _typedef_in_global_scope( node, s_tree, scopes ):
            raise Exception("Typedef not declared in global scope")

        types.append( [type_name, type_size] )

    return types

def _typedef_in_global_scope (node, s_tree, scopes) :

    #print(f"scopes: {scopes}")

    def x (node):
        #print(node)
        parent_index = node[1]

        if parent_index == None:
            return True

        node_parent = s_tree[ parent_index ]

        for s in scopes:
            scope_node_index = s[0]
            if scope_node_index == node[1]:
                return False

        return x(node_parent)

    return x(node)

    #return True



def typefy_functions (s_tree):
    for i, node in enumerate( s_tree ):
        if node[0] != "FN_DECL":
            continue

        # remove function name, return type and expr
        children = node[2][1:-2]

        # typefy function arguments
        len_ch = len(children)
        limit = int( len_ch / 2 )
        for ch in range(0,limit):
            type_i, value_i = children[ch*2:(ch*2)+2]
            ch_node = s_tree[type_i]

            if ch_node[0] == "TYPE":
                continue
            
            elif ch_node[0] != "NAME":
                raise Exception("Bug on function arguments typefying.")

            s_tree[type_i][0] = "TYPE"

        # typefy function return type
        all_children = node[2]
        s_tree[ all_children[ len(all_children)-2 ] ][0] = "TYPE"
        



def subst_types (s_tree, types) :

    # substitute all NAMEs for TYPEs in tree
    for i, node in enumerate(s_tree):
        if node[0] != "NAME":
            continue

        for t in types:
            if node[1] != t[0]:
                continue

            s_tree[i][0] = "TYPE"
            break

    typefy_functions(s_tree)
    _typefy_set_mut(s_tree)


def _typefy_set_mut(s_tree) :
    for i, node in enumerate(s_tree):
        if not( node[0] in ["SET_DECL", "MUT_DECL"] ):
            continue

        s_tree[ node[2][1] ][0] = "TYPE"


def match_fn(node, scopes, symtbl, s_tree, name, pkg_name, loaded_functions):
    if name not in loaded_functions.keys():
        return False

    for fn_name in loaded_functions.keys():
        fn_lf = loaded_functions[fn_name]

        for fn in fn_lf:
            fn_pkg_name, fn_arg_types, fn_ret_type = fn

            node_fn_name = s_tree[ node[2][1] ][1]
            
            if node_fn_name != fn_name:
                continue

            # get call argument types
            call_arg_types = _get_call_arg_types(node, pkg_name, s_tree, symtbl, scopes)

            #print("call_arg_types: %s" % call_arg_types)
            #print("fn_arg_types: %s" % fn_arg_types)

            if call_arg_types == fn_arg_types:
                return fn

    return False

def _get_call_arg_types(node, pkg_name, s_tree, symtbl, scopes):
    call_args = node[2][2:]
    arg_types = []

    for i in call_args:
        arg_type = False
        arg_node = s_tree[i]
        call_arg_name = arg_node[1]

        for sym_pkg_name in symtbl:
            # skip different packages
            if sym_pkg_name != pkg_name: 
                continue

            sym_pkg = symtbl[sym_pkg_name]

            for sym_key, sym_list in sym_pkg.items():
                # check arg name
                if call_arg_name != sym_key:
                    continue

                #print("k: %s" % sym_key)

                # check arg scope
                arg_scope = _get_scope(arg_node, pkg_name, s_tree, symtbl, scopes)

                # sym_list scope
                sym_node = s_tree[ sym_list[0][1] ]
                sym_scope = _get_scope(sym_node, pkg_name, s_tree, symtbl, scopes)

                #print("arg_scope: %s" % arg_scope)
                #print("sym_scope: %s" % sym_scope)

                if arg_scope != sym_scope:
                    continue

                # same name args, same scope args

                #print("sym_list: %s" % sym_list[0][0])
                all_arg_types = sym_list[0][0]

                if all_arg_types[0] in ['set', 'mut']:
                    arg_type = all_arg_types[1]
                    #print("s arg_type: %s" % arg_type)

                    arg_types.append(arg_type)
                    break

    #print("arg_types: %s" % arg_types)
    return arg_types


def _get_scope(node, pkg_name, s_tree, symtbl, scopes):
    #print("node: %s" % node)
    #print("s_tree: %s" % s_tree)
    #print("symtbl: %s" % symtbl)
    #print("scopes: %s" % scopes)

    pkg_scope = scopes[pkg_name]
    pkg_symtbl = symtbl[pkg_name]

    parent_i = node[2]
    parent = s_tree[parent_i]

    def iterup(node):
        #print("node: %s" % node)
        parent_i = node[1]
        #print("parent_i: %s" % parent_i)

        for s in pkg_scope:
            # global scope
            if parent_i == None and s[2] == None:
                return s

            # some local scope
            if parent_i == s[0]:
                return s

        if parent_i == None:
            return False

        parent = s_tree[parent_i]
        return iterup(parent)

    return iterup(parent)

def _get_fn_arg_types(node, pkg_name, s_tree, symtbl, scopes):
    pass
