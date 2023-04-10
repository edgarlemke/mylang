def extract_fn_decls(s_tree, symtbl, pkg):
    fn_decls = {}

    # fn_syms = []
    for sym_name in symtbl:
        sym_list = symtbl[sym_name]

        for sym in sym_list:
            if sym[0][0] != "fn":
                continue

            fn_name = sym_name
            fn_args = []
            fn_ret_type = None

            fn_name_node = s_tree[sym[1]]
            fn_decl_node = s_tree[fn_name_node[2]]

            # get args
            fn_args_nodes = fn_decl_node[2][1:-2]
            for i in range(0, int(len(fn_args_nodes) / 2)):
                type_node = s_tree[fn_args_nodes[i * 2]]
                # name_node = s_tree[ fn_args_nodes[(i*2)+1] ]

                fn_args.append(type_node[1])

            # get return type
            ret_node_i = fn_decl_node[2][len(fn_decl_node[2]) - 2]
            ret_node = s_tree[ret_node_i]
            fn_ret_type = ret_node[1]

            # append function
            fn_decl = [pkg, fn_args, fn_ret_type]

            if fn_name not in fn_decls.keys():
                fn_decls[fn_name] = []

            fn_decls[fn_name].append(fn_decl)

    return fn_decls
