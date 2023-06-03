import eval_types
import re


def eval(li, scope):
    # print(f"\neval {li} {scope}")

    if scope is None:
        scope = runtime_scope

    if len(li) == 0:
        # print(f"exiting eval {li}")
        return li

#    if li[0] == "data":
#        return li

    new_li = None
    macros = scope[1]
    if len(macros):
        expand = True
        new_li = li.copy()
        while expand:
            new_li, found_macro = expand_macro(new_li, scope)
            # print(f"expand new_li: {new_li}")
            expand = found_macro

        # print(f"over new_li: {new_li}")

        li = new_li

    is_macro = li[0] == "macro"
    is_list = isinstance(li[0], list)

    if is_list:
        evaled_li = []
        for key, item in enumerate(li):
            # li[key] = eval(item, scope)
            e = eval(item, scope)
            if len(e) > 0:
                evaled_li.append(e)
        li = evaled_li

    else:
        # get all names matching list's first value
        name_matches = [n for n in scope[0] if n[0] == li[0]]
        # print(f"name_matches: {name_matches}")

        # check name_matches size
        if len(name_matches) == 0:
            raise Exception(f"Unassigned name: {li[0]}")
        elif len(name_matches) > 1:
            raise Exception(f"More than one name set, it's a bug! {li[0]}")

        # get the only valid name
        n = name_matches[0]
        # print(f"n: {n}")

        if n[2] in ["fn", "internal"]:
            # len 1, so is a reference
            if len(li) == 1:
                # print(f"fn ref {li}")
                li = n[1:]

            # len > 1, so is a function call
            else:
                if n[2] == "fn":
                    x = call_fn(li, n, scope)
                    li = x
                elif n[2] == "internal":
                    # print(f"!!! internal")
                    x = n[3](li, scope)
                    li = x

        else:
            li = n[1:]

    # print(f"exiting eval {li}")
    return li


def call_fn(li, fn, scope):
    # print(f"call_fn {li}")

    name = fn[0]
    methods = fn[3]
    candidates = []
    for m in methods:
        # print(f"method: {m}")

        # match types
        match = True
        for arg_i, arg in enumerate(li[1:]):
            # print(f"argument: {arg_i} {arg}")

            # break in methods without the arguments
            if len(m[0]) < arg_i + 1:
                match = False
                break

            # solve argument
            solved_arg = None

            is_list = isinstance(arg, list)
            if is_list:
                solved_arg = eval(arg, scope)

            else:
                name_value = get_name_value(arg, scope)
                found_value = name_value != []

                if found_value:
                    solved_arg = name_value

                else:
                    solved_arg = infer_type(arg)

            if solved_arg is None:
                match = False
                break

            if len(solved_arg) == 0:
                pass

            else:
                # print(f"solved_arg: {solved_arg}")
                # print(f"m[0]: {m[0]}")
                marg = m[0][arg_i][0]
                # print(f"marg: {marg}")

                if solved_arg[0] != marg[0]:
                    match = False
                    break

        if match:
            candidates.append(m)

    if len(candidates) == 0:
        raise Exception(f"No candidate function found: {name}")
    if len(candidates) > 1:
        raise Exception(f"Method candidates mismatch: {name} {candidates}")

    the_method = candidates[0][0]
#    print(f"the_method: {the_method}")

    retv = eval(the_method[2], scope)
    # print(f"exiting call_fn {li}")
    return retv


def get_name_value(name, scope):
    def iterup(scope):
        # print(f"interup {scope}")
        for n in scope[0]:
            # print(f"n: {n}")
            if n[0] == name:
                return list(n[2:])

        # didn't return found value...

        # if has parent scope, iterup
        if scope[2] is not None:
            return iterup(scope[2])
        # else, return empty list
        else:
            return []

    return iterup(scope)


def infer_type(arg):
    candidates = []

    int_regexp = "[0-9]+"
    m = re.match(int_regexp, arg)
    if m:
        candidates.append([m, "int"])

    float_regexp = "[0-9]+\\.[0-9]+"
    m = re.match(float_regexp, arg)
    if m:
        candidates.append([m, "float"])

    bool_regexp = "true|false"
    m = re.match(bool_regexp, arg)
    if m:
        candidates.append([m, "bool"])

    biggest = None
    for c in candidates:
        if biggest is None:
            biggest = c
        else:
            if len(c[0].group()) > len(biggest[0].group()):
                biggest = c

            elif len(c[0].group()) == len(biggest[0].group()):
                raise Exception("Two candidates with same size!")

    if biggest is None:
        return None

    return [biggest[1], arg]


def expand_macro(li, scope):
    # print(f"expand_macro: {li}")

    new_li = li.copy()
    found_macro = False

    # for each item in li
    for index, item in enumerate(li):
        # print(f"LI index: {index} item: {item}")

        found_macro = False
        for macro in scope[1]:
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
    Validate function declarations.

    Syntax:
    fn ((argtype1 arg1)(argtype2 arg2)) ret_type (body)
    """

    # print(f"calling __fn__ {node}")

    validate_fn(node, scope)

    # create new scope
    child_scope = [[], [], scope, []]
    scope[3].append(child_scope)

    return node


def validate_fn(node, scope):
    # check fn arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for fn: {node}")

    fn, args, ret_type, body = node
    types = [t[0] for t in scope[0] if t[2] == "type"]

    # check if types of the arguments are valid
    for arg in args:
        type_, name = arg
        if type_ not in types:
            raise Exception(f"Function argument has invalid type: {arg} {node}")

    # check if the return type is valid
    if ret_type not in types:
        raise Exception(f"Function return type has invalid type: {ret_type} {node}")


def __set__(node, scope):
    """
    Validate set i.e. constant setting.

    Syntax:
    set name mutability (type value)

    mutablity values can be "const" or "mut", without the quotes
    """

    # print(f"calling __set__ {node}")

    _validate_set(node, scope)

    names = scope[0]
    set_, mutdecl, name, data = node
    type_ = data[0]

    if type_ == "fn":
        value = list(data[1:4])
        all_fn = [(i, var) for i, var in enumerate(names) if var[1] == "fn" and var[0] == name]
        # print(f"all_fn: {all_fn}")

        if all_fn == []:
            # print(f"empty all_fn")
            names.append([name, mutdecl, type_, [value]])

        else:
            match_fn = all_fn[0]
            i, var = match_fn

            names[i][3].append(value)

    else:
        value = data[1]

        valid_value = None
        for T in [t for t in scope[0] if t[2] == "type"]:
            if T[0] == type_:
                valid_value = value

        # remove old value from names
        for index, v in enumerate(names):
            if v[0] == name:
                if v[1] == "const":
                    raise Exception("Trying to reassign constant: {node}")

                elif v[1] == "mut":
                    names.remove(v)
            break

        # insert new value into names
        names.append([name, mutdecl, type_, valid_value])

    # print(f"names after set: {names}")

    # retv = ["data", [type_, value]]
    # print(f"returning {retv}")
    return []


def _validate_set(node, scope):
    # check set arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for set: {node}")

    set_, mutdecl, name, data = node
    type_ = data[0]

    types = [t[0] for t in scope[0] if t[2] == "type"]
    exceptions = ["fn"]

    # check type
    if type_ not in types and type_ not in exceptions:
        raise Exception(f"Constant assignment has invalid type {type_} {node}")

    # check if value is valid for type
    pass


def __macro__(node, scope):
    """
    Set a new macro in the current scope.

    Syntax:
    macro alias (syntax) (expanded)
    """

    # print(f"calling __macro__ {node}")

    validate_macro(node, scope)

    macro, alias, syntax, expanded = node

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

    scope[1].append([alias, new_syntax, new_expanded])

    return []


def validate_macro(node, scope):
    # check macro arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for macro: {node}")


def __if__(node, scope):
    """
    """
#    print(f"calling __if__: {node}")

    validate_if(node, scope)

    return []

#    if_, condition_list, true_list, false_list = node
#
#    result = eval(condition_list)
#    # print(f"result: {result}")
#
#    is_true = result[0] == 'data' and result[1][0] == 'bool' and result[1][1] == 'true'
#
#    if is_true:
#        return true_list
#
#    else:
#        return false_list


def validate_if(node, scope):
    # check if arguments number
    if len(node) != 4:
        raise Exception(f"Wrong number of arguments for if: {node}")

    # check if condition is of type bool
    pass


def __let__(node, scope):
    """
    Shortcut for defining an anonymous function and calling it with the given arguments
    """
#    print(f"calling __let__: {node}")

    validate_let(node, scope)

    let_, args, body = node

    return []


def validate_let(node, scope):
    # check let arguments number
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for let: {node}")


def __data__(node, scope):
    # print(f"calling __data__: {node}")

    validate_data(node, scope)

    return node[1]


def validate_data(node, scope):
    # check data arguments number
    if len(node) != 2:
        raise Exception(f"Wrong number of arguments for data: {node}")


def __meta__(node, scope):
    #    print(f"calling __meta__: {node}")

    return eval(node[1:], meta_scope)
#
#


meta_scope = [
  [
    ["fn", "mut", "internal", __fn__],
    ["let", "mut", "internal", __let__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["data", "mut", "internal", __data__],
  ],
  [],
  None,
  []
]
runtime_scope = [
  [
    ["fn", "mut", "internal", __fn__],
    ["let", "mut", "internal", __let__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],
    ["if", "mut", "internal", __if__],
    ["data", "mut", "internal", __data__],
    ["meta", "mut", "internal", __meta__],
  ],
  [],
  None,
  []
]


def _add_types():
    types = [
#      ["i8", "mut", "type", [1]],
#      ["i16", "mut", "type", [2]],
#      ["i32", "mut", "type", [4]],
#      ["i64", "mut", "type", [8]],
      ['int', "mut", 'type', ['?']],  # signed int, register width

#      ["u8", "mut", "type", [1]],
#      ["u16", "mut", "type", [2]],
#      ["u32", "mut", "type", [4]],
#      ["u64", "mut", "type", [8]],
      ['uint', "mut", 'type', ['?']],  # unsigned int, register width

      ["byte", "mut", "type", [1]],
      ["bool", "mut", "type", [1]],

#      ["f32", "mut", "type", [4]],
#      ["f64", "mut", "type", [8]],
      ['float', "mut", 'type', ['?']],

      ["struct", "mut", "type", ['?']],
      ["enum", "mut", "type", ['?']],
      ["ptr", "mut", "type", ['?']],  # the size will probably be the same of int, have complementary type
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
