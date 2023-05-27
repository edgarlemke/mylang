import eval_types


def eval(li, scope):
    #    print(f"eval {li} {scope}")

    if scope is None:
        scope = runtime_scope

    if len(li) == 0:
        return li

    if li[0] == "data":
        return li

    new_li = None
    macros = scope[1]
    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            new_li, found_macro = expand_macro(new_li)
            # print(f"expand new_li: {new_li}")
            expand = found_macro

        # print(f"over new_li: {new_li}")

        li = new_li

    is_macro = li[0] == "macro"
    is_list = isinstance(li[0], list)

    if is_list:
        for key, item in enumerate(li):
            li[key] = eval(item, scope)

    else:
        # print(f"!!! {li}")
        called = False
        li, called = call_fn(li, scope[0])
        li, called = call_internal(li, scope)

#        if not called:
#            print(f"#####  NOT CALLED: {li}")

    return li


def call_fn(li, variables):
    funcs = [v for v in variables if v[1] == "fn"]
    # print(f"funcs: {funcs}")
    for fn in funcs:
        name = fn[0]

        # if function name matches first item of list
        if li[0] == name:
            print(li)
            methods = fn[2]
            candidates = []
            for m in methods:
                # print(f"method: {m}")

                # match types
                notmatch = False
                for arg_i, arg in enumerate(li[1:]):
                    # print(f"argument: {arg}")

                    # break in methods without the arguments
                    if len(m[0]) < arg_i + 1:
                        notmatch = True
                        break

                    marg = m[0][arg_i]

                    if arg[0][0] == "data":
                        if arg[0][1][0] != marg[0]:
                            notmatch = True
                            break

                    else:
                        print(f"WHAAAT")

                if not notmatch:
                    candidates.append(m)

            if len(candidates) > 1:
                raise Exception(f"Method candidates mismatch: {name} {candidates}")

            if len(candidates) == 0:
                # return (li, False)
                continue  # skip to next fn

            the_method = candidates[0]

            return (eval(the_method[2]), True)

    return (li, False)


def call_internal(li, scope):
    names = scope[0]
    internals = [n for n in names if n[1] == "internal"]
    # print(f"internals: {internals}")
    for i in internals:
        name = i[0]
        if li[0] == name:
            return (i[2](li, scope), True)

    return (li, False)


def expand_macro(li):
    # print(f"expand_macro: {li}")

    new_li = li.copy()
    found_macro = False

    # for each item in li
    for index, item in enumerate(li):
        # print(f"LI index: {index} item: {item}")

        found_macro = False
        for macro in macros:
            # print(f"macro: {macro}")

            found_macro, full_match, bindings = match_macro(li, index, macro)
            # print(f"AA> {new_li} {found_macro}")

            if found_macro:
                # expand macro
                new_li = li.copy()
                # print(f"full_match: {full_match}")

                for i in reversed(full_match):
                    new_li.pop(i)

                # print(f"all bindings: {bindings}")

                def subst_item(extended):
                    # print(f"subs_item: {extended}")
                    new_extended = extended.copy()

                    for index, item in enumerate(extended):
                        # print(f"ext index: {index} item: {item}")
                        if isinstance(item, list):
                            new_extended[index] = subst_item(item)

                        else:
                            for b in bindings:
                                name, value = b
                                # print(f"bindings name {name} value {value} item {item}")

                                if name == item:
                                    new_extended[index] = value

                    return new_extended

                subst_extended = subst_item(macro[2])
                for i in reversed(subst_extended):
                    new_li.insert(full_match[0], i)

                break

        if found_macro:
            break

    return [new_li, found_macro]


def match_macro(li, index, macro):
    # print(f"match_macro - li: {li} index: {index} macro: {macro}")

    alias, syntax, extended = macro

    # li_piece = li[index : index+len(syntax)]
    li_piece = li[index:]
    bindings = []

    full_match = False
    for cur_index, cur in enumerate(li_piece):
        # print(f"cur {cur_index} {cur}")

        matching = []

        for cur_index2, cur2 in enumerate(li_piece[cur_index:cur_index + len(syntax)]):
            # print(f"cur2 {cur_index2} {cur2}")
            if syntax[cur_index2] == cur2:
                matching.append(cur_index + cur_index2)
                # print(f">>> common matching {cur2} against {syntax[cur_index2]}")

            elif syntax[cur_index2][0] == "'":
                bindings.append([syntax[cur_index2], cur2])
                matching.append(cur_index + cur_index2)
                # print(f">>> quoted maching {cur2} against {syntax[cur_index2]}")

            else:
                # print(f">>> no match {cur2} against {syntax[cur_index2]}")
                bindings = []
                break

        if len(matching) == len(syntax):
            # print(f"BINGO ==> matching: {matching} syntax: {syntax}\n")
            full_match = matching
            break

    if not full_match:
        return (False, full_match, [])

    return (True, full_match, bindings)


# RUNTIME INTERNALS
#
def __fn__(node, scope):
    """
    Declare a new function.

    Syntax is:
    fn ((argtype1 arg1)(argtype2 arg2)) (ret_type) (body)
    """
    # print(f"calling __fn__ {node}")

    fn, args, ret_type, body = node
    types = [t[0] for t in scope[0] if t[1] == "type"]

    # check if types of the arguments are valid
    for arg in args:
        type_, name = arg
        if type_ not in types:
            raise Exception(f"Function argument has invalid type: {arg} {node}")

    # check if the return type is valid
    if ret_type not in types:
        raise Exception(f"Function return type has invalid type: {ret_type} {node}")

    # create new scope
    child_scope = [[], [], scope, []]
    scope[3].append(child_scope)

    return node


def __set__(node):
    """
    Set a variable in the current variables namespace.
    """

    print(f"calling __set__ {node}")

    _validate_set(node)

    name = node[1]
    data = node[2]
    type_ = data[0]

    if data[0] == "fn":
        value = list(data[1:4])
        all_fn = [(i, var) for i, var in enumerate(cur_scope[0]) if var[1] == "fn" and var[0] == name]
        # print(f"all_fn: {all_fn}")

        if all_fn == []:
            cur_scope[0].append([name, type_, [value]])

        else:
            match_fn = all_fn[0]
            i, var = match_fn

            cur_scope[0][i][2].append(value)

    else:
        value = data[1]

        valid_value = None
        for T in eval_types.types:
            if T[0] == type_:
                valid_value = T[1](value)

        # remove old value from variables
        for index, v in enumerate(variables):
            if v[0] == name:
                variables.remove(v)
            break

        # insert new value into variables
        variables.append([name, type_, valid_value])

    # print(f"variables after set: {variables}")
    retv = ["data", ["set", name, type_, value]]
    # print(f"returning {retv}")
    return retv


def _validate_set(node):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for set: {node}")

    return True


def __macro__(node):
    """
    Set a new macro in the current macros namespace.
    """

    print(f"calling __macro__ {node}")

    alias = node[1]
    # print(f"alias: {alias}")

    syntax = node[2]
    # print(f"syntax: {syntax}")

    expanded = node[3]
    # print(f"expanded: {expanded}")

    def join_quotes(li):
        # print(f"join_quotes {li}")

        to_join = []

        kuote = False
        for index, i in enumerate(li.copy()):
            if i == "'":
                kuote = True

            elif kuote == True:
                to_join.append([index - 1, index])
                kuote = False

            elif isinstance(i, list):
                li[index] = join_quotes(i)

        for j in reversed(to_join):
            start, end = j
            # print(f"start {start} {li[start]}")
            # print(f"end {end} {li[end]}")

            # print(f"old li {li} {li[start]}")
            quote = li.pop(start)
            # print(f"old li2 {li} {li[start]}")
            value = li.pop(start)
            # print(f"new_li {li}")

            li.insert(start, "".join([quote, value]))

        return li

    new_syntax = join_quotes(syntax)
    # print(f"new_syntax: {new_syntax}")

    new_expanded = join_quotes(expanded)
    # print(f"new_expanded: {new_expanded}")

    macros.append([alias, new_syntax, new_expanded])

    return []


def __if__(node):
    """
Evaluates if the first list is equals (data (bool true)), if yes returns the second list, if no returns the third list.
    """
    print(f"calling __if__: {node}")

    if_, condition_list, true_list, false_list = node

    result = eval(condition_list)
    # print(f"result: {result}")

    is_true = result[0] == 'data' and result[1][0] == 'bool' and result[1][1] == 'true'

    if is_true:
        return true_list

    else:
        return false_list


# def __let__(node):
#    """
#    Creates a local scope and bind the given variables to it, the evaluates it
#    """
#    print(f"calling __let__: {node}")
#
#    let_, variables, code = node
#
#    new_scope = [
#        variables,
#        [],
#        cur_scope,
#        []
#    ]
#    cur_scope[3].append(new_scope)
#
#    print(f"scopes: {scopes}")


def __data__(node):
    print(f"calling __data__: {node}")


def __use__(node):
    print(f"calling __use__: {node}")


def __meta__(node):
    print(f"calling __meta__: {node}")
#
#


# META INTERNALS
#
def __meta_fn__(node):
    print(f"calling __meta_fn__: {node}")


def __meta_set__(node):
    print(f"calling __meta_set__: {node}")


def __meta_let__(node):
    print(f"calling __meta_let__: {node}")


def __meta_macro__(node):
    print(f"calling __meta_macro__: {node}")


def __meta_if__(node):
    print(f"calling __meta_if__: {node}")


def __meta_data__(node):
    print(f"calling __meta_data__: {node}")


def __meta_use__(node):
    print(f"calling __meta_data__: {node}")
#
#


meta_scope = [
  [
    ["fn", "internal", __meta_fn__],  # declare a function
#    ["set", "internal", __meta_set__],  # set a name in local scope
    ["let", "internal", __meta_let__],  # abbreviation of declaring function and calling it with arguments
    ["macro", "internal", __meta_macro__],  # set a new macro in local scope
    ["if", "internal", __meta_if__],  # compare conditions and return the appropriate list
    ["data", "internal", __meta_data__],  # return data not to be eval-uated
    ["use", "internal", __meta_use__],  # load external package into local scope

  ],
  [],
  None,
  []
]
runtime_scope = [
  [
    ["fn", "internal", __fn__],  # declare a function
#    ["set",   "internal", __set__  ], # set a name in local scope
#    ["let",   "internal", __let__  ], # abbreviation of declaring function and calling it with arguments
#    ["macro", "internal", __macro__], # set a new macro in local scope
#    ["if",    "internal", __if__   ], # compare conditions and return the appropriate list
#    ["data",  "internal", __data__ ], # return data not to be eval-uated
#    ["use",   "internal", __use__  ], # load external package into local scope
#    ["meta", "internal", __meta__],  # evalute expressions with meta scope

  ],
  [],
  None,
  []
]


def _add_types():
    types = [
      ["i8", "type", [1]],
      ["i16", "type", [2]],
      ["i32", "type", [4]],
      ["i64", "type", [8]],

      ["u8", "type", [1]],
      ["u16", "type", [2]],
      ["u32", "type", [4]],
      ["u64", "type", [8]],

      ["byte", "type", [1]],
      ["bool", "type", [1]],

      ["f32", "type", [4]],
      ["f64", "type", [8]],

      ["struct", "type", ['?']],
      ["enum", "type", ['?']],
      ["ptr", "type", ['?']],
    ]

    for s in [meta_scope, runtime_scope]:
        for t in types:
            s[0].append(t)


_add_types()

# order of development: meta first, runtime second

# will the meta scope contain the runtime scope, or they can be separated?
#  probably easier to put together than to separate if needed

# should we serialize the SCOPE tree? serializing = easier references
#  only SCOPE tree seems interesting to serialize... but not yet

# which functions are the MVP? macro, if, data, set, mut, let, use, fn (useless in compile time until we have full compiler anyway)
#  runtime
#   set
#    check if name has already been set-ed,mut-ed in current scope and upper scopes
#   mut
#    check if name has already been set-ed in current scope and upper scopes (:= for setting first time, = for re-setting)
#   let
#    shortcut for declaring a function and calling it with parameters (validation is from fn)
#   fn
#    check function validity
#   if
#    executes code conditionally
#   macro
#    declares a macro in local scope
#   use
#    loads a package (fn are added to static overloading, constants, variables and structs not starting with _ are loaded into variable)

# should we pass scope to eval? yes

# plan creating scopes with fn
#  take scope
#  add new scope to children
#  enter new scope, binding the parameters
#  there will be no closures
#  compiler time can allocate scope dinamically, runtime when function is declared (fn actually must be called)

# scopes = [
#    [  # META
#        [     # variables
#            ["set", "internal", __set__],  # set a constant in local scope
#            ["mut", "internal", __mut__],  # set a mutable variable in local scope
#            ["let", "internal", __let__],  # declare new local scope
#            ["macro", "internal", __macro__],  # set a new macro in local scope
#            ["if", "internal", __if__],  # compare conditions and return the appropriate list
#            ["data", "internal", __data__],  # return data not to be eval-uated
#            ["use", "internal", __use__],  # load external package into local scope
#        ],
#        [],   # macros
#        None,  # parent
#        [],   # children
#    ],
#    [  # RUNTIME
#        [     # variables
#            ["meta", "internal", __meta__],  # call compile time instructions
#
#            # ["set",   "internal", __set__  ], # check constant setting
#            # ["mut",   "internal", __mut__  ], # check mutable variable setting
#            # ["let",   "internal", __let__  ], # check lets
#            ["macro", "internal", __macro__],  # set a new macro in local scope
#            ["if", "internal", __if__],  # compare conditions and return the appropriate list
#            ["data", "internal", __data__],  # return data not to be eval-uated
#            ["use", "internal", __use__],  # load external package into local scope
#        ],
#        [],   # macros
#        None,  # parent
#        [],   # children
#    ]
# ]
# cur_scope = scopes
