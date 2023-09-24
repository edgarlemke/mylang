import argparse
import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)


def __fn__(node, scope):
    # print(f"back-end __fn__: {node}")

    # compile-time validation
    import frontend.compiletime as ct
    ct.validate_fn(node, scope)

    # back-end validation
    _validate_fn(node, scope)
    return []


def _validate_fn(node, scope):
    import frontend.compiletime as ct

    fn, args, ret_type, body = node
    types = [t[0] for t in scope[0] if t[2] == "type"]

    # check if types of the arguments are valid
    split_args = ct.split_function_arguments(args)
    for arg in split_args:
        # type_, name = arg
        name, type_ = arg
        if type_ not in types:
            raise Exception(f"Function argument has invalid type: {arg} {node}")

    # check if the return type is valid
    if ret_type not in types:
        raise Exception(f"Function return type has invalid type: {ret_type} {node}")


def __handle__(node, scope):
    return []


functions_stack = []


def __set__(node, scope):
    DEBUG = False
    # DEBUG = True

    import eval

    if DEBUG:
        print(f"__set__():  backend {node}")

    # compile-time validation
    import frontend.compiletime as ct
    ct.__set__(node, scope, split_args=False)

    # if DEBUG:
    #    print(f"\nscope: {scope}\n\n")

    # back-end validation
    _validate_set(node, scope)

    names = scope[0]
    set_, mutdecl, name, data = node

    name_candidate = []
    if len(data) == 1:
        if isinstance(name, list):
            name_to_get = name[0]
        else:
            name_to_get = name

        name_candidate = eval.get_name_value(name_to_get, scope)
        if name_candidate == []:
            raise Exception(f"Unassigned name: {name}")

        type_ = name_candidate[2]

    elif len(data) == 2:
        type_ = data[0]

    # if node sets a function
    if type_ == "fn":
        fn_content = data[1]

        # solve function overloaded name to a single function name
        uname = _unoverload(name, fn_content[0])

        # get argument types
        args = []

        # convert argument types
        function_arguments = fn_content[0]
        # print(f"function_arguments: {function_arguments}")
        for arg in function_arguments:
            # print(f"arg: {arg}")
            args.append(f"{_convert_type(arg[1])} %{arg[0]}")

        if DEBUG:
            print(f"__set__():  backend - function_arguments: {function_arguments}")

        # get return type and body
        if len(fn_content) == 2:
            fn_return_type = None
            fn_body = fn_content[1]

        elif len(fn_content) == 3:
            fn_return_type = fn_content[1]
            fn_body = fn_content[2]

        # convert return type
        return_type = "void"
        if fn_return_type is not None:
            return_type = _convert_type(fn_return_type)

        if DEBUG:
            print(f"__set__():  backend return_type: {return_type}")

        # create function body scope
        import copy
        function_body_scope = copy.deepcopy(eval.default_scope)

        # set scope child
        scope[3].append(function_body_scope)

        # set function body scope parent
        function_body_scope[2] = scope

        # set scope return calls
        function_body_scope[6] = scope[6]

        # set scope as backend scope
        function_body_scope[7] = True

        # setup function arguments
        for function_argument in function_arguments:
            if DEBUG:
                print(f"__set__():  backend - function_argument: {function_argument}")

            argument_list = [function_argument[0], "const", function_argument[1], None]
            function_body_scope[0].append(argument_list)

        if DEBUG:
            print(f"__set__():  backend - function_body_scope: {function_body_scope}")

        functions_stack.append([uname, function_body_scope, function_arguments])

        # sort out body IR
        result = eval.eval(fn_body, function_body_scope)
        # print(f"result: {result}")

        functions_stack.pop()

        # if len(result) == 0:
        body = ["\tstart:"]
        # body = ["br label %start", "start:"]
        # else:

        if len(result) > 0:
            body.append(result)

        if DEBUG:
            print(f"__set__():  backend - body: {body}")

        serialized_body = _serialize_body(body)

        if DEBUG:
            print(f"__set__():  serialized_body: {serialized_body}")

        if "ret" not in serialized_body[len(serialized_body) - 1]:
            serialized_body.append([f"\t\tret {return_type}"])

        # declaration, definition = _write_fn(uname, args, return_type, body)
        retv = _write_fn(uname, args, return_type, serialized_body)

    else:
        tmp_name = None

        if DEBUG:
            print(f"__set__():  type isn't fn - name: {name} type: {type_}")

        if isinstance(type_, list) and type_[0] == "Array":
            pass

        elif len(functions_stack) > 0:  # and mutdecl == "mut":
            function_name = functions_stack[len(functions_stack) - 1][0]
            if len(data) == 1:
                _increment_NAME(function_name, name)

            tmp_name = _get_NAME(function_name, name)

        else:
            # print(f"YAY: {name}")
            pass

        if DEBUG:
            print(f"__set__():  tmp_name: {tmp_name}")

        if type_ == "Str":
            str_, size = _converted_str(data[1])

            retv = f"""
\t\t%{tmp_name} = alloca %struct.Str, align 8

\t\t%{name}_str = alloca [{size} x i8]
\t\tstore [{size} x i8] c"{str_}", i8* %{name}_str

\t\t%{name}_str_ptr = getelementptr [{size} x i8], [{size} x i8]* %{name}_str, i64 0, i64 0

\t\t%{name}_addr_ptr = getelementptr %struct.Str, %struct.Str* %{tmp_name}, i32 0, i32 0
\t\tstore i8* %{name}_str_ptr, i8* %{name}_addr_ptr, align 8

\t\t%{name}_size_ptr = getelementptr %struct.Str, %struct.Str* %{tmp_name}, i32 0, i32 1
\t\tstore i64 {size}, i64* %{name}_size_ptr, align 8
""".split("\n")

        elif type_ in ["int", "uint", "float", "bool"]:
            if DEBUG:
                print("__set__():  backend - type_ is int uint float or bool")

            t = _convert_type(type_)

            if len(data) == 1:
                value = data[0]
                # _increment_NAME(function_name, name)
                # tmp_name = _get_NAME(function_name, name)

            elif len(data) == 2:
                value = data[1]

            if type_ in ["int", "uint"]:
                if value[:2] == "0x":
                    value = int(value, base=16)

            if DEBUG:
                print(f"__set__():  backend - value: {value}")

            if isinstance(value, list):
                if DEBUG:
                    print(f"__set__():  backend - calling return_call()")
                value, stack = return_call(value, scope, [])
                if DEBUG:
                    print(f"__set__():  backend - value: {value} stack: {stack}")

                stack.append(f"\t\t%{tmp_name} = {value}")
                retv = "\n".join(stack)
                if DEBUG:
                    print(f"__set__():  backend - retv: {retv}")

                # clean stack from return_call
                stack = []

            else:
                # check if it's at global backend scope
                if scope[2] is None:
                    if DEBUG:
                        print(F"__set__():  backend - global scope")
                    retv = f"@{name} = global {t} {value}"

                # not global backend scope
                else:
                    if DEBUG:
                        print(f"__set__():  backend - not global scope")
                    # allocate space in stack and set value
                    retv = f"""\t\t%{name}_stack = alloca {t}
\t\tstore {t} {value}, {t}* %{name}_stack
\t\t%{tmp_name} = load {t}, {t}* %{name}_stack
"""
            if DEBUG:
                print(f"__set__():  backend - retv: {retv}")

        elif type_ == "struct":
            if len(data) == 1:
                value = data[0]
                converted_member_types = []

                if DEBUG:
                    print(f"value: {value}")

                for struct_member in value:
                    if DEBUG:
                        print(f"struct_member: {struct_member}")
                    converted_member_types.append(_convert_type(struct_member[1]))

                joined_converted_member_types = ", ".join(converted_member_types)
                retv = f"%{name} = type {{ {joined_converted_member_types} }}"

            elif len(data) == 2:
                value = data[1]
                retv = ""

            else:
                raise Exception("Invalid size of struct")

        # test for composite types
        elif len(type_) > 1:
            if DEBUG:
                print(f"__set__():  backend - type_: {type_}")

            type_value = eval.get_name_value(type_[0], scope)
            if DEBUG:
                print(f"__set__():  backend - type_value: {type_value}")

            # check for arrays
            # print(type_value)
            if type_value[0] == "Array":
                if DEBUG:
                    print(f"__set__():  backend - Array found! data: {data} name_candidate: {name_candidate}")

                # check if array is already set
                retv = None
                if name_candidate != []:
                    member_index = 0
                    array_size = 64

                    retv = _set_array_member(type_value, member_index, type_, data[0], name[0], array_size)

                else:
                    retv = _set_array(type_value, type_, data, name)


#                if type_value[2] == "struct":
#                    # if not a generic struct
#                    if len(type_value[3][0]) == 0:
#                        retv = 555
#
#                    # else, it's a generic struct
#                    else:
#                        # assemble name from type variables
#                        generic_struct_name = "_".join([type_value[0]] + type_[1:])
#
#                        if DEBUG:
#                            print(f"generic_struct_name: {generic_struct_name}")
#
#                        stack = [f"%{name}_stack = alloca %struct.{generic_struct_name}"]
#
#                        if type_value[0] == "Array":
#                            print("ARRAY")
#
#                        for member_index, member_value in enumerate(data[1]):
#                            print(f"member_value: {member_value}")
#
#                            # convert value type
#                            # converted_type = _convert_type(type_value[3][1][member_index][1])
#                            infered_type_argument = eval._infer_type(member_value)
#                            converted_type = _convert_type(infered_type_argument[0])
#
#                            # append alloca to stack
#                            stack.append(f"%{name}_{member_index} = alloca {converted_type}")
#
#                   retv = "\n".join(stack)
            else:
                raise Exception(f"Unknown composite type {type_}")

        else:
            # print("AQUI")

            # if it's simple unknown type
            if len(type_) == 1:
                raise Exception(f"Unknown type {type_}")

    if DEBUG:
        print(f"__set__():  backend - exiting __set__()")

    return retv


def _set_array(type_value, type_, data, name):
    array_struct_name = "_".join([type_value[0]] + type_[1:])

    array_size = len(data[1])
    array_members_type = _convert_type(type_[1])

    # setup stack with start of array initialization
    stack = [f"""\t\t; start of initialization of {name} Array
\t\t%{name}_Array = alloca %{array_struct_name}
\t\t%{name}_Array_members = alloca [{array_size} x {array_members_type}]
"""]

    # initialize array members
    for member_index in range(0, array_size):
        value_to_store = data[1][member_index]

        # if value is ?, keep array members uninitialized - unsafer but cheaper
        if value_to_store == "?":
            continue

        stack.append(f"""\t\t%{name}_member_{member_index}_ptr = getelementptr [{array_size} x {array_members_type}], [{array_size} x {array_members_type}]* %{name}_Array_members, i32 0, i32 {member_index}
\t\tstore {array_members_type} {data[1][member_index]}, {array_members_type}* %{name}_member_{member_index}_ptr
""")

    # end of array initialization
    stack.append(f"""\t\t%{name}_Array_ptr = getelementptr %{array_struct_name}, %{array_struct_name}* %{name}_Array, i32 0, i32 0

\t\t%{name}_Array_members_ptr = getelementptr %{array_struct_name}, %{array_struct_name}* %{name}_Array_ptr, i32 0, i32 0
\t\tstore [{array_size} x {array_members_type}]* %{name}_Array_members, [{array_size} x {array_members_type}]* %{name}_Array_members_ptr

\t\t%{name}_Array_size_ptr = getelementptr %{array_struct_name}, %{array_struct_name}* %{name}_Array, i32 0, i32 1
\t\tstore i64 {array_size}, i64* %{name}_Array_size_ptr
\t\t; end of initialization of {name} Array
""")

    retv = "\n".join(stack)
    return retv


def _set_array_member(type_value, member_index, type_, data, name, array_size):
    array_members_type = _convert_type(type_[1])

    value = data

    retv = f"""\t\t%{name}_member_{member_index}_ptr = getelementptr [{array_size} x {array_members_type}], [{array_size} x {array_members_type}]* %{name}_Array_members, i32 0, i32 {member_index}
\t\tstore {array_members_type} {value}, {array_members_type}* %{name}_member_{member_index}_ptr
"""

    return retv


def _converted_str(str_):
    encoded = str_.encode('utf-8')

    buf = []
    size = 0
    for ch in encoded:
        size += 1

        if ch < 128:
            buf.append(chr(ch))

        else:
            buf.append(f"\\{format(ch, 'x')}")

    result = "".join(buf)

    return (result, size)


def _validate_set(node, scope):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_validate_set():  backend - node: {node}")

    import eval

    set_, mutdecl, name, data = node

    if len(data) == 1:
        if DEBUG:
            print(f"_validate_set():  backend - len(data) == 1 - name: {name}")

        if isinstance(name, list):
            name_to_get = name[0]

        else:
            name_to_get = name

        name_candidate = eval.get_name_value(name_to_get, scope)
        if name_candidate == []:
            raise Exception(f"Reassigning not assigned name: {name} {data}")

        if DEBUG:
            print(f"_validate_set():  backend - name_candidate: {name_candidate}")

        type_ = name_candidate[2]
        if DEBUG:
            print(f"_validate_set():  backend - type_: {type_}")

    elif len(data) == 2:
        if DEBUG:
            print(f"_validate_set():  backend - len(data) == 2")

        type_ = data[0]
        # value = data[1]

    # validate type
    if not _validate_type(type_, scope):
        raise Exception(f"Constant assignment has invalid type - type_: {type_} - node: {node}")

    if DEBUG:
        print(f"_validate_set():  backend - node OK: {node}")

    return


def _unoverload(name, function_arguments):
    # print(f"_unoverload: {node}")

    # extract node, get function name
    # set_, mutdecl, name, data = node
    # type_ = data[0]
    # fn_content = data[1]

    # function_arguments = fn_content[0]
    # print(f"function_arguments: {function_arguments}")

    arg_types = []
    for arg in function_arguments:
        # print(f"arg: {arg} -  {node}")
        arg_types.append(arg[1])

    unamel = [name]
    if len(arg_types) > 0:

        buffer = []
        for arg_type in arg_types:
            if isinstance(arg_type, list):
                buffer.append("_".join(arg_type))
            else:
                buffer.append(arg_type)

        unamel += ["__", "_".join(buffer)]
    uname = "".join(unamel)
    # print(f"uname: {uname}")

    return uname


def _convert_type(type_):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_convert_type: {type_}")

    # convert integers
    if type_ in ["int", "uint"]:
        converted_type = "i64"

    # convert bytes
    if type_ == "byte":
        converted_type = "i8"

    # convert booleans
    elif type_ == "bool":
        converted_type = "i1"

    # convert floats
    elif type_ == "float":
        converted_type = "float"

    # convert pointers
    elif type_[0] == "ptr":
        converted_type = f"{_convert_type(type_[1])}*"

    elif type_[0] == "Array":
        converted_type = f"i8*"

    # convert Str (strings)
    elif type_ == "Str":
        converted_type = "%struct.Str*"

    return converted_type


def _validate_type(type_, scope):
    DEBUG = False

    # get types and structs from scope and parent scopes
    all_types = []
    all_structs = []

    def iterup(scope, all_types, all_structs):
        # print(f"\n!! iterup - scope: {scope}\n")

        parent_scope = scope[2]
        children_scopes = scope[3]

        if parent_scope is not None:
            iterup(parent_scope, all_types, all_structs)

        types = [t[0] for t in scope[0] if t[2] == "type" and t[0] not in all_types]
        all_types += types
        # print(f"types: {types}")

        structs = [s[0] for s in scope[0] if s[2] == "struct" and s[0] not in all_structs]
        all_structs += structs
        # print(f"structs: {structs}")

    iterup(scope, all_types, all_structs)
    exceptions = ["fn"]
    valid_types = (all_types + all_structs + exceptions)

    def loop(current_type):
        for each_type in current_type:
            if DEBUG:
                print(f"loop():  each_type: {each_type}")

            if isinstance(each_type, list):
                return loop(each_type)

            else:
                if each_type not in valid_types:
                    return False

        return True

    if isinstance(type_, list):
        return_value = loop(type_)
    else:
        return_value = loop([type_])

    return return_value


def _write_fn(fn, args, return_type, body):
    # arg_types = [ arg[1] for arg in args ]
    # decl_args = ", ".join(arg_types)
    # declaration = f"declare {return_type} @{fn}({decl_args})"
    # print(f"declaration: {declaration}")

    def_args = ", ".join(args)
    definition = [f"define {return_type} @{fn}({def_args}) {{", body, "}"]
    # print(f"definition: {definition}")

    # return [declaration, definition]
    return definition


def _serialize_body(body):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_serialize_body():  {body}")

    serialized = []

    def iter(li):
        if DEBUG:
            print(f"iter():  li: {li}")

        for child in li:
            if DEBUG:
                print(f"\niter():  child: {child}")
            if isinstance(child, list):
                if DEBUG:
                    print(f"iter():  gonna iter over {child}")
                iter(child)
            else:
                if DEBUG:
                    print(f"iter():  appending {child}")
                serialized.append(child)

        if DEBUG:
            print(f"\niter():  exiting {li}\n\n -> serialized: {serialized}\n")

    iter(body)

    if DEBUG:
        print(f"_serialize_body():  - exiting -> serialized: {serialized}\n")

    return serialized


def __macro__(node, scope):
    return []


def __if__(node, scope):
    DEBUG = False
    # DEBUG = True

    _validate_if(node, scope)

    if DEBUG:
        print(f"__if__():  backend - node: {node}")

    import eval

    stack = ["\t\t; if start"]

    # extract elifs from node
    elifs = [child for child in node[3:] if isinstance(child, list) and len(child) > 0 and child[0] == "elif"]
    if DEBUG:
        print(f"__if__():  backend - elifs: {elifs}")

    # extract else from node
    else_ = [child for child in node[2:] if isinstance(child, list) and len(child) > 0 and child[0] == "else"]
    if DEBUG:
        print(f"__if__():  backend - !!!! else_: {else_}")

    if len(else_) > 0:
        else_ = else_[0]
    else:
        else_ = None

    if DEBUG:
        print(f"__if__():  backend - else_: {else_}")

    # get labels
    then_label = _get_var_name("if", "if_then_block_")

    elif_labels = []
    for elif_ in elifs:
        elif_labels.append([elif_, _get_var_name("if", "if_elif_block_")])

    else_label = None
    if else_ is not None:
        else_label = _get_var_name("if", "if_else_block_")

    end_label = _get_var_name("if", "if_end_")

    if len(elif_labels) > 0:
        first_elif = elif_labels[0]
        x_label = first_elif[1] + "_test"

    elif else_ is not None:
        x_label = else_label

    elif else_ is None:
        x_label = end_label

    condition_ir = _get_condition_ir(node, scope, then_label, x_label)
    stack += ["\t\t; if - then condition test"]
    stack += [condition_ir]

    then_code = eval.eval(node[2], scope)
    if DEBUG:
        print(f"__if__():  backend - then_code: {then_code}")

    stack += [f"\t\t; if - then code block\n\t{then_label}:"] + then_code + [f"\t\tbr label %{end_label}\n"]

    x_size = len(node[3:])
    if DEBUG:
        print(f"__if__():  backend - x_size: {x_size}")

    for else_index in range(0, 0 + x_size):
        item = node[else_index + 3]
        if DEBUG:
            print(f"__if__():  backend - else_index: {else_index} item: {item}")

        # handle elif
        if len(item) > 0 and item[0] == "elif":
            if DEBUG:
                print("__if__():  backend - elif")

            # append elif label
            elif_label = elif_labels[else_index][1]
            stack += [f"\t\t; if - elif condition test\n\t{elif_label}_test:"]

            # check if needs to add branch for next elif
            if len(elif_labels) > else_index + 1:
                next_x_label = elif_labels[else_index + 1][1] + "_test"

            # else, check if there's an else
            elif else_ is not None:
                next_x_label = else_label

            # else, use end_label
            else:
                next_x_label = end_label

            elif_condition_ir = _get_condition_ir(item, scope, elif_label, next_x_label)
            if DEBUG:
                print(f"__if__():  backend - elif_condition_ir: {elif_condition_ir}")

            stack += [elif_condition_ir]

            # get elif code
            elif_code = eval.eval(item[2], scope)
            if DEBUG:
                print(f"__if__():  backend - elif_code: {elif_code}")

            stack += [f"\t\t; if - elif code block\n\t{elif_label}:"]
            stack += elif_code
            stack += [f"""\t\tbr label %{end_label}\n"""]

        else:
            if DEBUG:
                print(f"__if__():  backend - else - item: {item}")

            if len(item) == 0:
                continue

            else_code = eval.eval(item[1], scope)
            if DEBUG:
                print(f"__if__():  backend - else_code: {else_code}")

            stack += [f"\t\t; if - else code block\n\t{else_label}:"] + else_code + [f"""
\t\tbr label %{end_label}\n"""]

    stack += [f"""\t\t; if - end block
\t{end_label}:
\t\t; if end
"""]

    if DEBUG:
        print(f"__if__():  backend - stack: {stack}")

    S = _serialize_body(stack)
    # print(f"S: {S}")

    result = "\n".join(S)
    # result = "\n".join(stack)
    if DEBUG:
        print(f"__if__():  backend - result: {result}")

    return result


def _validate_if(node, scope):
    pass


def _get_condition_ir(node, scope, then_label, x_label):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"_get_condition_ir():  node: {node} scope: {hex(id(scope))} then_label: {then_label} x_label: {x_label}")

    import eval
    condition_name = _get_var_name("if", "condition_")

    if isinstance(node[1], list):
        condition_function = eval.get_name_value(node[1], scope)
        condition_call, stack = return_call(node[1], scope, [])
        if DEBUG:
            print(f"_get_condition_ir():  backend - condition_call: {condition_call}")

        retv = stack + [f"""\t\t%{condition_name}  = {condition_call}
\t\tbr i1 %{condition_name}, label %{then_label}, label %{x_label}\n"""]
        return "\n".join(retv)

    else:
        # try to infer type
        infered_type_value = eval._infer_type(node[1])
        if DEBUG:
            print(f"infered_type_value: {infered_type_value}")

        value = None

        # check infered type
        if infered_type_value is not None:
            if infered_type_value[0] != "bool":
                raise Exception("Invalid value for if test: {node}")

            # translate value
            value = "1" if node[1] == "true" else "0"

        else:
            # try to get value
            name_value = eval.get_name_value(node[1], scope)
            if DEBUG:
                print(f"_get_condition_ir():  backend - name_value: {name_value}")

            if len(name_value) == 0:
                raise Exception(f"Unassigned name: {node[1]}")

            if name_value[2] != "bool":
                raise Exception("Invalid value for if test: {node}")

            value = "1" if name_value[3] == "true" else "0"

        return f"\t\tbr i1 {value}, label %{then_label}, label %{x_label}\n"


def __elif__(node, scope):
    DEBUG = False
    # DEBUG = True

    if DEBUG:
        print(f"__elif__():  backend - node: {node}")


def __data__(node, scope):
    return node[1:]


def __write_ptr__(node, scope):
    return []


def __read_ptr__(node, scope):
    return []


def __get_ptr__(node, scope):
    return []


def __size_of__(node, scope):
    return []


def __unsafe__(node, scope):
    return []


def __linux_write__(node, scope):
    # print(f"calling __linux_write__: {node}")
    # print(f"SCOPE: {scope}")

    _validate_linux_write(node, scope)

    # convert fd
    from eval import eval
    fd = eval([node[1]], scope)
    fd[0] = _convert_type(fd[0])
    fd_arg = " ".join(fd)
    # print(f"fd: {fd}")

    # if type(node[2]) == list:
    #    print(f"node[2]: {node[2]}")
    # text = eval([ node[2] ], scope)
    text = node[2]
    # print(f"text: {text}")

    template = f"""
%str_addr_ptr = getelementptr %struct.Str, %struct.Str* %text, i32 0, i32 0
%str_size_ptr = getelementptr %struct.Str, %struct.Str* %text, i32 0, i32 1

%addr = load i8*, %struct.Str* %str_addr_ptr
%size = load i64, %struct.Str* %str_size_ptr

call void @linux_write({fd_arg}, i8* %addr, i64 %size)
"""

    return template.split("\n")


def _validate_linux_write(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for linux_write: {node}")


def return_call(node, scope, stack=[]):
    DEBUG = False
    # DEBUG = True

    import eval

    if DEBUG:
        print(f"return_call():  node: {node} scope: {hex(id(scope))} stack: {stack}")

    # find out function name
    li_function_name = node[0]

    value = eval.get_name_value(li_function_name, scope)
    if DEBUG:
        print(f"return_call():  value: {value}")

    # matches = [name for name in scope[0] if name[0] == li_function_name]

    # if len(matches) == 0:
    #    raise Exception(f"No name matches for function: {li_function_name}")

    # value = matches[0]
    # print(f"value2: {value}")

    if value == False:
        raise Exception(f"No name matches for function: {li_function_name}")

    method, solved_arguments = eval.find_function_method(node, value, scope)
    if DEBUG:
        print(f"return_call():  method: {method}")

    function_arguments = method[0]
    if DEBUG:
        print(f"return_call():  function_arguments: {function_arguments}")

    function_name = _unoverload(li_function_name, function_arguments)
    if DEBUG:
        print(f"return_call():  function_name: {function_name}")

    # find out arguments
    converted_arguments = []
    for argument_index, argument in enumerate(function_arguments):
        if DEBUG:
            print(f"return_call():  argument: {argument}")

        name, type_ = argument
        converted_type = _convert_type(type_)

        # fulfill llvm requirement to convert float values types to doubles
        if converted_type == "float":
            converted_type = "double"

        argument_value = node[argument_index + 1]
        if DEBUG:
            print(f"return_call():  argument_value: {argument_value}")

        if isinstance(argument_value, list):
            scope_argument_value = eval.get_name_value(argument_value[0], scope)

            if DEBUG:
                print(f"return_call():  before return_call() call - stack: {stack}\n")
            result, stack = return_call(argument_value, scope, stack)

            if DEBUG:
                print(f"return_call():  result: {result} stack_: {stack}")

            tmp = _get_var_name(function_name, "tmp_")
            call_ = f"\t\t%{tmp} = {result}"

            if DEBUG:
                print(f"return_call():  appending call_ {call_} to stack")

            stack.append(call_)

            if DEBUG:
                print(f"return_call():  stack after append: {stack}")

            argument_value = f"%{tmp}"

        else:
            scope_argument_value = eval.get_name_value(argument_value, scope)
            if DEBUG:
                print(f"return_call():  scope_argument_value: {scope_argument_value}")

            if scope_argument_value != []:
                argument_name = False
                if len(functions_stack) > 0:
                    arguments_matches = [arg for arg in functions_stack[len(functions_stack) - 1][2] if argument_value == arg[0]]
                    # print(f"arguments_matches: {arguments_matches}")

                    if len(arguments_matches) > 0:
                        argument_value = f"%{argument_value}"
                        argument_name = True

                if not argument_name:
                    NAME = _get_NAME(function_name, argument_value)
                    argument_value = f"%{NAME}"

                # print(f"argument_value: {argument_value}")

        converted_argument = f"{converted_type} {argument_value}"

        if DEBUG:
            print(f"return_call():  converted_argument: {converted_argument}")

        converted_arguments.append(converted_argument)

    converted_function_arguments = ", ".join(converted_arguments)

    # find out return type
    if len(method) == 2:
        function_return_type = "void"

    elif len(method) == 3:
        function_return_type = _convert_type(method[1])

    value = f"call {function_return_type} @{function_name}({converted_function_arguments})"

    if DEBUG:
        print(f"return_call():  exiting return_call():  value: {value}  stack: {stack}\n")

    return value, stack


_var_names = {}


def _get_var_name(function_name, prefix):
    # initialize key in _var_names for function_name
    if function_name not in _var_names.keys():
        _var_names[function_name] = 0

    # get name
    var_name = f"{prefix}{_var_names[function_name]}"

    # increment counter
    _var_names[function_name] += 1

    return var_name


_nyaa = {}


def _get_NAME(function_name, name):
    # initialize key in _nyaa for function_name
    if function_name not in _nyaa.keys():
        _nyaa[function_name] = {}

    # initialize key in _nyaa[function_name] for name
    if name not in _nyaa[function_name].keys():
        _nyaa[function_name][name] = 0

    NAME = f"{name}_{_nyaa[function_name][name]}"

    return NAME  # _nyaa[function_name][name]


def _increment_NAME(function_name, name):
    _nyaa[function_name][name] += 1


scope = [
  [  # names
    ["fn", "mut", "internal", __fn__],
    ["handle", "mut", "internal", __handle__],
    ["set", "mut", "internal", __set__],
    ["macro", "mut", "internal", __macro__],

    ["if", "mut", "internal", __if__],
    ["elif", "mut", "internal", __elif__],

    ["data", "mut", "internal", __data__],
    ["write_ptr", "mut", "internal", __write_ptr__],
    ["read_ptr", "mut", "internal", __read_ptr__],
    ["get_ptr", "mut", "internal", __get_ptr__],
    ["size_of", "mut", "internal", __size_of__],
    ["unsafe", "mut", "internal", __unsafe__],

    ["linux_write", "const", "internal", __linux_write__],

    ["int", "const", "type", [8]],

    ["uint", "const", "type", [8]],

    ["ptr", "const", "type", [8]],

    ["byte", "const", "type", [1]],
    ["bool", "const", "type", [1]],

    ["float", "const", "type", [8]],

    ["Array", "const", "type", ['?']],
    ["struct", "const", "type", ['?']],
    ["enum", "const", "type", ['?']],

    ["Str", "const", "type", ['?']],
  ],
  [],    # macros
  None,  # parent scope
  [],    # children scope
  True,  # is safe scope
  None,  # forced handler
  return_call,   # eval return call handler
  True,   # backend scope
]


def _setup_scope():
    from . import bool as bool_
    from . import uint as uint
    from . import int as int_
    from . import float as float_

    names = [

    ["and_bool_bool", "const", "internal", bool_.__and_bool_bool__],
    ["or_bool_bool", "const", "internal", bool_.__or_bool_bool__],
    ["xor_bool_bool", "const", "internal", bool_.__xor_bool_bool__],
    ["not_bool", "const", "internal", bool_.__not_bool__],
    ["eq_bool_bool", "const", "internal", bool_.__eq_bool_bool__],

    ["add_int_int", "const", "internal", int_.__add_int_int__],
    ["sub_int_int", "const", "internal", int_.__sub_int_int__],
    ["mul_int_int", "const", "internal", int_.__mul_int_int__],
    ["div_int_int", "const", "internal", int_.__div_int_int__],
    ["and_int_int", "const", "internal", int_.__and_int_int__],
    ["or_int_int", "const", "internal", int_.__or_int_int__],
    ["xor_int_int", "const", "internal", int_.__xor_int_int__],
    ["not_int", "const", "internal", int_.__not_int__],
    ["eq_int_int", "const", "internal", int_.__eq_int_int__],
    ["gt_int_int", "const", "internal", int_.__gt_int_int__],
    ["ge_int_int", "const", "internal", int_.__ge_int_int__],
    ["lt_int_int", "const", "internal", int_.__lt_int_int__],
    ["le_int_int", "const", "internal", int_.__le_int_int__],
    ["shl_int_int", "const", "internal", int_.__shl_int_int__],
    ["shr_int_int", "const", "internal", int_.__shr_int_int__],

    ["add_uint_uint", "const", "internal", uint.__add_uint_uint__],
    ["sub_uint_uint", "const", "internal", uint.__sub_uint_uint__],
    ["mul_uint_uint", "const", "internal", uint.__mul_uint_uint__],
    ["div_uint_uint", "const", "internal", uint.__div_uint_uint__],
    ["and_uint_uint", "const", "internal", uint.__and_uint_uint__],
    ["or_uint_uint", "const", "internal", uint.__or_uint_uint__],
    ["xor_uint_uint", "const", "internal", uint.__xor_uint_uint__],
    ["not_uint", "const", "internal", uint.__not_uint__],
    ["eq_uint_uint", "const", "internal", uint.__eq_uint_uint__],
    ["gt_uint_uint", "const", "internal", uint.__gt_uint_uint__],
    ["ge_uint_uint", "const", "internal", uint.__ge_uint_uint__],
    ["lt_uint_uint", "const", "internal", uint.__lt_uint_uint__],
    ["le_uint_uint", "const", "internal", uint.__le_uint_uint__],
    ["shl_uint_int", "const", "internal", uint.__shl_uint_int__],
    ["shr_uint_int", "const", "internal", uint.__shr_uint_int__],

    ["add_float_float", "const", "internal", float_.__add_float_float__],
    ["sub_float_float", "const", "internal", float_.__sub_float_float__],
    ["mul_float_float", "const", "internal", float_.__mul_float_float__],
    ["div_float_float", "const", "internal", float_.__div_float_float__],
    ["eq_float_float", "const", "internal", float_.__eq_float_float__],
    ["gt_float_float", "const", "internal", float_.__gt_float_float__],
    ["ge_float_float", "const", "internal", float_.__ge_float_float__],
    ["lt_float_float", "const", "internal", float_.__lt_float_float__],
    ["le_float_float", "const", "internal", float_.__le_float_float__],

    ]

    for name in names:
        scope[0].append(name)


_setup_scope()
