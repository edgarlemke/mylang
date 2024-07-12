import copy
import argparse

import os
import sys
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(dir_path)
import eval
from shared import debug


def __fn__(node, scope):
    debug(f"__fn__():  backend - node: {node}")

    global function_global_stack

    # compile-time validation
    import frontend.compiletime as compiletime
    compiletime.__fn__(node, scope)

    # back-end validation
    _validate_fn(node, scope)

    if len(node) == 4:
        fn_, name, arguments, body = node
    elif len(node) == 5:
        fn_, name, arguments, return_type, body = node

    # split_arguments = compiletime.split_function_arguments(arguments)

    debug(f"__fn__():  backend - arguments: {arguments}")

    # solve function overloaded name to a single function name
    uname = _unoverload(name, arguments)

    # get argument types
    args = []
    # convert argument types
    for arg in arguments:
        debug(f"__fn__(): arg in arguments: {arg}")

        if len(arg) == 2:
            converted_argument_type = _convert_type(arg[1])

        elif len(arg) == 3 and arg[1] == "mut":
            converted_argument_type = _convert_type(arg[2])

        args.append(f"{converted_argument_type} %{arg[0]}")

    # convert return type
    if len(node) == 4:
        return_type = "void"
    if len(node) == 5:
        return_type = _convert_type(return_type)

    debug(f"__fn__():  backend return_type: {return_type}")

    # create function body scope
    import copy
    function_body_scope = copy.deepcopy(eval.default_scope)

    # set scope child
    scope["children"].append(function_body_scope)

    # set function body scope parent
    function_body_scope["parent"] = scope

    # set scope return calls
    function_body_scope["return_call"] = scope["return_call"]
    function_body_scope["return_call_common_list"] = scope["return_call_common_list"]
    function_body_scope["return_call_common_not_list"] = scope["return_call_common_not_list"]

    # set scope as backend scope
    function_body_scope["step"] = "backend"

    # setup function arguments
    for function_argument in arguments:
        debug(f"__fn__():  backend - function_argument: {function_argument}")

        if len(function_argument) == 2:
            mutdecl = "const"
            argument_type = function_argument[1]

        elif len(function_argument) == 3 and function_argument[1] == "mut":
            mutdecl = "mut"
            argument_type = function_argument[2]

        argument_list = [function_argument[0], mutdecl, argument_type, None]
        function_body_scope["names"].append(argument_list)

    # debug(f"__fn__():  backend - function_body_scope: {function_body_scope}")

    functions_stack.append([uname, function_body_scope, arguments])

    # sort out body IR
    function_body_scope["function_depth"] += 1
    result = eval.eval(body, function_body_scope)
    function_body_scope["function_depth"] -= 1

    functions_stack.pop()

    # if len(result) == 0:
    body = ["\tstart:"]
    # body = ["br label %start", "start:"]
    # else:

    if len(result) > 0:
        body.append(result)

    debug(f"__fn__():  backend - body: {body}")

    serialized_body = _serialize_body(body)

    debug(f"__fn__():  backend - serialized_body: {serialized_body}")

    if "ret" not in serialized_body[len(serialized_body) - 1]:
        serialized_body.append([f"\t\tret {return_type}"])

    # declaration, definition = _write_fn(uname, args, return_type, body
    function_global = "\n".join(function_global_stack)
    debug(f"__fn__():  backend - function_global: {function_global}")

    retv = _write_fn(uname, args, return_type, serialized_body)

    if len(function_global) > 0:
        retv.insert(0, function_global)

    debug(f"__fn__():  backend - retv: {retv}")

    function_global_stack = []

    return retv


def _validate_fn(node, scope):
    import frontend.compiletime as compiletime

    # fn, args, ret_type, body = node
    if len(node) == 4:
        fn_, name, args, body = node
    elif len(node) == 5:
        fn_, name, args, ret_type, body = node

    debug(f"_validate_fn():  args: {args}")

    # types = [t[0] for t in scope["names"] if t[2] == "type"]

    # check if types of the arguments are valid
    # split_args = compiletime.split_function_arguments(args)
    # debug(f"_validate_fn():  split_args: {split_args}")

    for arg in args:
        debug(f"_validate_fn():  backend - arg: {arg} args: {args}")

        if len(arg) == 2:
            name, type_ = arg
            mutdecl = "const"

        elif len(arg) == 3 and arg[1] == "mut":
            name, mutdecl, type_ = arg

        debug(f"_validate_fn():  backend - name: {name} type_: {type_}")

        # check for composite type
        if isinstance(type_, list):

            if type_[0] == "mut":
                search_type = type_[1]

            else:
                search_type = type_[0]

        # check for simple type
        else:
            search_type = type_

        # name_value = eval.get_name_value(type_, scope)
        # debug(f"_validate_fn():  backend - name_value: {name_value}")
        debug(f"_validate_fn():  backend - search_type: {search_type}")

        if not _validate_type(search_type, scope):  # name_value == [] or (name_value != [] and name_value[2] != "type"):
            raise Exception(f"Function argument has invalid type: {type_} {node}")

    # check if the return type is valid
    if len(node) == 5:  # and ret_type not in types:

        if not _validate_type(ret_type, scope):  # name_value == [] or (name_value != [] and name_value[2] != "type"):
            raise Exception(f"Function return type has invalid type: {ret_type} {node}")


functions_stack = []
function_global_stack = []


def __def__(node, scope):
    global function_global_stack

    debug(f"__def__():  backend {node}")

    # compile-time validation
    import frontend.compiletime as ct
    ct.__def__(node, scope)

    # debug(f"\nscope: {scope}\n\n")

    # back-end validation
    _validate_def(node, scope)

    names = scope["names"]
    def_, mutdecl, name, data = node

    debug(f"__def__():  data: {data}")

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

    debug(f"__def__():  type_: {type_}")

    tmp_name = None

    if isinstance(type_, list):
        if type_[0] == "Array":
            pass
        elif type_[0] == "ptr":
            pass

    elif len(functions_stack) > 0:  # and mutdecl == "mut":
        function_name = functions_stack[len(functions_stack) - 1][0]
        if len(data) == 1:
            _increment_NAME(function_name, name)

        tmp_name = _get_NAME(function_name, name)
        _increment_NAME(function_name, name)

    else:
        # print(f"YAY: {name}")
        pass

    debug(f"__def__():  tmp_name: {tmp_name}")

    # check if name value is a struct reference
    if data[1][0] == "ref_member":
        debug(f"__def__():  is struct member reference")
        retv = __get_struct_member__(node, scope)

    elif data[1][0] == "ref_array_member":
        debug(f"__def__():  is array member reference")
        retv = __get_array_member__(node, scope)

    else:

        if type_ == "Str":
            str_, size = _converted_str(data[1])

            if mutdecl == "const":
                function_name = functions_stack[len(functions_stack) - 1][0]
                function_global_stack.append(f"""@{function_name}_{name} = constant [{size} x i8] c"{str_}" """)
                retv = f"""
\t\t%{tmp_name} = alloca %struct.Str, align 8
"""

            elif mutdecl == "mut":
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

        elif type_ in ["int", "uint", "float", "bool", "byte"]:
            debug("__def__():  backend - type_ is int uint float or bool or byte")

            t = _convert_type(type_)

            if len(data) == 1:
                value = data[0]
                # _increment_NAME(function_name, name)
                # tmp_name = _get_NAME(function_name, name)

            elif len(data) == 2:
                value = data[1]

            if type_ in ["int", "uint", "byte"]:
                if value[:2] == "0x":
                    value = int(value, base=16)

            debug(f"__def__():  backend - value: {value}")

            if isinstance(value, list):
                debug(f"__def__():  backend - calling return_call()")
                value, stack = return_call(value, scope, [])
                debug(f"__def__():  backend - value: {value} stack: {stack}")

                if mutdecl == "const":
                    stack.append(f"\t\t%{name} = {value}")

                elif mutdecl == "mut":
                    stack.append(f"\t\t%{tmp_name} = {value}")

                retv = "\n".join(stack)
                debug(f"__def__():  backend - retv: {retv}")

                # clean stack from return_call
                stack = []

            else:
                # check if it's at global backend scope
                if scope["parent"] is None:
                    debug(F"__def__():  backend - global scope")
                    retv = f"@{name} = global {t} {value}"

                # not global backend scope
                else:
                    debug(f"__def__():  backend - not global scope")

                # handle constants
                if mutdecl == "const":

                    if len(functions_stack) == 0:
                        retv = f"@{name} = constant {t} {value}"

                    else:
                        debug(f"functions_stack: {functions_stack}")

                        fn_name = functions_stack[0][0]

                        function_global_stack.append(f"@{fn_name}_{name} = constant {t} {value}")

                        # if is an integer read the pointer
                        if type_ in ["int", "uint", "byte"]:
                            retv = f"""\t\t; load value of constant "{name}"
\t\t%{name} = load {t}, {t}* @{fn_name}_{name}
"""

                        else:
                            retv = ""

                # handle mutable values
                elif mutdecl == "mut":
                    # allocate space in stack and set value
                    retv = f"""\t\t%{name}_stack = alloca {t}
\t\tstore {t} {value}, {t}* %{name}_stack
\t\t%{tmp_name} = load {t}, {t}* %{name}_stack
"""
            debug(f"__def__():  backend - retv: {retv}")

        elif type_ == "struct":
            #        if len(data) == 1:
            #            value = data[0]
            #            retv = "; STRUCT DEF"
            #
            #        elif len(data) == 2:
            if len(data) == 2:
                value = data[1]

                debug(f"__def__():  struct - value: {value}")

                converted_members = []
                for member in value:
                    debug(f"__def__():  struct - member: {member}")

                    # check if type is struct
                    # member_type_name_value = eval.get_name_value(member[1], scope)
                    # debug(f"__def__():  struct - member_type_name_value: {member_type_name_value}")

                    # if member_type_name_value != [] and member_type_name_value[2] == "struct":
                    #    converted_member_type = f"%{member[1]}*"
                    # else:
                    converted_member_type = _convert_type(member[1], scope)

                    debug(f"__def__():  converted_member_type: {converted_member_type}")

                    converted_members.append(converted_member_type)

                joined_members = ", ".join(converted_members)

                retv = f"""; "{name}" struct definition
%{name} = type {{{joined_members}}}"""

            else:
                raise Exception("Invalid size of struct")

        # test for composite types
        elif isinstance(type_, list):
            debug(f"__def__():  backend - type_: {type_}")

            type_value = eval.get_name_value(type_[0], scope)
            debug(f"__def__():  backend - type_value: {type_value}")

            # check for arrays
            # print(type_value)
            if type_value[0] == "Array":
                debug(f"__def__():  backend - Array found! data: {data} name_candidate: {name_candidate}")

                # check if array is already def
                retv = None
                if name_candidate != []:
                    member_index = 0
                    array_size = 64

                    retv = _set_array_member(type_value, member_index, type_, data[0], name[0], array_size)

                else:
                    retv = _def_array(type_value, type_, data, name)

            # check for pointers
            elif type_value[0] == "ptr":
                debug(f"__def__():  backend - ptr found! data: {data} name_candidate: {name_candidate}")

                retv = "RETV_PTR"

            else:
                raise Exception(f"Unknown composite type {type_}")

        else:

            # check for structs
            type_name_value = eval.get_name_value(type_, scope)
            found_struct = type_name_value != [] and type_name_value[2] == "struct"

            if found_struct:
                debug(f"__def__():  backend - found_struct - type_name_value: {type_name_value} data: {data}")

                converted_members = []
                for member_index, member in enumerate(type_name_value[3][0]):
                    debug(f"__def__():  backend - struct member: {member}")

                    member_value = data[1][member_index]

                    member_value_name_value = eval.get_name_value(member_value, scope)
                    debug(f"__def__():  backend - member_value_name_value: {member_value_name_value}")

                    if member_value_name_value != []:

                        struct_candidate_name = member_value_name_value[2]
                        struct_candidate_name_value = eval.get_name_value(struct_candidate_name, scope)
                        if struct_candidate_name_value[2] == "struct":
                            member_value = f"%{member_value}"

                    converted_member_type = _convert_type(member[1], scope)

                    # converted_members.append(converted_member_type)
                    converted_members.append(f"""
\t\t; setting "{name}.{member[0]}" to {member_value}
\t\t%{name}_{member[0]} = getelementptr %{type_}, %{type_}* %{name}, i32 0, i32 {member_index}
\t\tstore {converted_member_type} {member_value}, {converted_member_type}* %{name}_{member[0]}""")

                debug(f"__def__():  backend - converted_members: {converted_members}")

                converted_members_text = "\n".join(converted_members)

                retv = f"""\t\t; "{name}" of type struct "{type_}" definition
\t\t%{name} = alloca %{type_}

{converted_members_text}
"""

            else:
                raise Exception(f"Unknown type: {type_}")

    debug(f"__def__():  backend - exiting __def__()")

    return retv


def _def_array(type_value, type_, data, name):
    unset = False
    end = len(type_)
    if end == 2:
        array_size = len(data[1])

    elif end == 3:
        end -= 1
        array_size = int(type_[2])
        unset = True

    array_struct_name = type_value[0]  # "_".join([type_value[0]] + type_[1:end])
    array_members_type = _convert_type(type_[1])

    debug(f"_def_array():  end: {end} array_size: {array_size} array_struct_name: {array_struct_name} array_members_type: {array_members_type} data: {data}")

    if not unset and not isinstance(data[1], list) and type_[1] == "byte":
        converted_str = _converted_str(data[1])
        array_size = converted_str[1]

    # setup stack with start of array initialization
    stack = [f"""\t\t; start of initialization of "{name}" Array
\t\t; allocate stack for "{name}" Array
\t\t%{name} = alloca %{array_struct_name}

\t\t; allocate stack for Array members
\t\t%{name}_members = alloca [{array_size} x {array_members_type}]
"""]

    if not _already_declared(functions_stack[0][0], f"{name}_members_ptr"):
        _declare_name(functions_stack[0][0], f"{name}_members_ptr")
        stack.append(f"""\t\t; setup members pointer in Array
\t\t%{name}_members_ptr = getelementptr %{array_struct_name}, %{array_struct_name}* %{name}, i64 0
""")

    stack.append(f"""\t\tstore [{array_size} x {array_members_type}]* %{name}_members, [{array_size} x {array_members_type}]* %{name}_members_ptr
""")

    if not unset:
        # initialize array members

        # check for array of bytes
        if not isinstance(data[1], list) and type_[1] == "byte":
            value_to_store = f"c\"{converted_str[0]}\""

#            stack.append(f"""\t\t; member {member_index} initialization
# \t\t%{name}_member_{member_index}_ptr = getelementptr [{array_size} x {array_members_type}], [{array_size} x {array_members_type}]* %{name}_Array_members, i32 0, i32 {member_index}
# \t\tstore {array_members_type} {value_to_store}, {array_members_type}* %{name}_member_{member_index}_ptr
# """)

        else:

            array_ir_buffer = []
            for member_index in range(0, array_size):
                array_ir_buffer.append(f"{array_members_type} {data[1][member_index]}")

            value_to_store = f"""[{",".join(array_ir_buffer)}]"""

        stack.append(f"""\t\t; init stack for "{name}" Array members
\t\tstore [{array_size} x {array_members_type}] {value_to_store}, [{array_size} x {array_members_type}]* %{name}_members
""")

    # end of array initialization
    stack.append(f"""\t\t; setup "{name}" Array size as {array_size}
\t\t%{name}_size_ptr = getelementptr %{array_struct_name}, %{array_struct_name}* %{name}, i32 0, i32 1
\t\tstore i64 {array_size}, i64* %{name}_size_ptr
\t\t; end of initialization of "{name}" Array
""")

    retv = "\n".join(stack)
    return retv


def _set_array_member(type_value, member_index, type_, data, name, array_size):
    array_members_type = _convert_type(type_[1])

    value = data

    retv = f"""\t\t%{name}_member_{member_index}_ptr = getelementptr [{array_size} x {array_members_type}], [{array_size} x {array_members_type}]* %{name}, i32 0, i32 {member_index}
\t\tstore {array_members_type} %{value}, {array_members_type}* %{name}_member_{member_index}_ptr
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


def _validate_def(node, scope):
    debug(f"_validate_def():  backend - node: {node}")

    import eval

    def_, mutdecl, name, data = node

    if len(data) == 1:
        debug(f"_validate_def():  backend - len(data) == 1 - name: {name}")

        if isinstance(name, list):
            name_to_get = name[0]

        else:
            name_to_get = name

        name_candidate = eval.get_name_value(name_to_get, scope)
        if name_candidate == []:
            raise Exception(f"Reassigning not assigned name: {name} {data}")

        debug(f"_validate_def():  backend - name_candidate: {name_candidate}")

        type_ = name_candidate[2]
        debug(f"_validate_def():  backend - type_: {type_}")

    elif len(data) == 2:
        debug(f"_validate_def():  backend - len(data) == 2")

        type_ = data[0]
        # value = data[1]

        if isinstance(type_, list):
            debug(f"_vadidate_def():  backend - type_ is list")

            if len(type_) < 2 or len(type_) > 3:
                raise Exception("Constant assignment has invalid type - type_: {type_}")

            if type_[0] == "Array":
                debug(f"_validate_def():  backend - type is Array: {type_}")

                # validate generic type
                valid_member_type = _validate_members_type(type_[1], scope)
                if not valid_member_type:
                    raise Exception("Constant assignment has invalid type - type_[1]: {type_[1]}")

                debug(f"_validate_def():  backend - valid member type")

                # check for array size and undef
                if len(type_) == 3:
                    debug(f"_validate_def():  backend - len of type_ is 3")

                    array_size = type_[2]
                    try:
                        int(array_size)
                    except BaseException:
                        raise Exception("Constant assignment of Array with invalid size - array_size: {array_size}")

                    if data[1] != "unset":
                        raise Exception("Constant assignment of sized Array for value other than \"unset\" - value: {data[1]}")

                type_ = type_[0]

    # validate type
    if not _validate_type(type_, scope):
        raise Exception(f"Constant assignment has invalid type - type_: {type_} - node: {node}")

    debug(f"_validate_def():  backend - node OK: {node}")

    return


def _validate_members_type(members_type, scope):
    debug(f"_validate_members_type():  members_type: {members_type}")

    valid = True

    if not isinstance(members_type, list):
        return _validate_type(members_type, scope)

    def iter(type_):
        debug(f"iter():  type_: {type_}")

        for child in type_:
            if isinstance(child, list):
                iter(child)

    iter(members_types)

    return valid


def _unoverload(name, function_arguments):
    debug(f"_unoverload():  name: {name} function_arguments: {function_arguments} ")

    arg_types = []
    for arg in function_arguments:
        debug(f"_unoverload():  arg: {arg}")
        arg_types.append(arg[1])

    unamel = [name]
    if len(arg_types) > 0:

        buffer = []
        for arg_type in arg_types:
            debug(f"_unoverload():  arg_type: {arg_type}")

            if isinstance(arg_type, list):
                # buffer.append("_".join(arg_type))

                list_arg_type_buffer = []

                def _serialize(li):
                    for child in li:
                        if isinstance(child, list):
                            _serialize(child)
                        else:
                            list_arg_type_buffer.append(child)
                _serialize(arg_type)
                buffer.append("_".join(list_arg_type_buffer))

            else:
                buffer.append(arg_type)

        unamel += ["__", "_".join(buffer)]
    uname = "".join(unamel)
    # print(f"uname: {uname}")

    return uname


def _convert_type(type_, scope=None):
    debug(f"_convert_type():  type_: {type_}")

    converted_type = None

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

    elif scope is not None:
        # convert structs
        type_name_value = eval.get_name_value(type_, scope)
        if type_name_value != [] and type_name_value[2] == "struct":
            converted_type = f"%{type_}*"

    # else:
    #    raise Exception(f"NYAA ${type_}")
    #    #converted_type = f"%{type_}*"

    debug(f"_convert_type():  converted_type: {converted_type}")

    return converted_type


def _validate_type(type_, scope):
    DEBUG = False

    # get types and structs from scope and parent scopes
    all_types = []
    all_structs = []

    def iterup(scope, all_types, all_structs):
        # print(f"\n!! iterup - scope: {scope}\n")

        parent_scope = scope["parent"]
        children_scopes = scope["children"]

        if parent_scope is not None:
            iterup(parent_scope, all_types, all_structs)

        types = [t[0] for t in scope["names"] if t[2] == "type" and t[0] not in all_types]
        all_types += types
        # print(f"types: {types}")

        structs = [s[0] for s in scope["names"] if s[2] == "struct" and s[0] not in all_structs]
        all_structs += structs
        # print(f"structs: {structs}")

    iterup(scope, all_types, all_structs)
    exceptions = ["fn"]
    valid_types = (all_types + all_structs + exceptions)

    def loop(current_type):
        for each_type in current_type:
            debug(f"loop():  each_type: {each_type}")

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
    debug(f"_serialize_body():  {body}")

    serialized = []

    def iter(li):
        debug(f"iter():  li: {li}")

        for child in li:
            debug(f"\niter():  child: {child}")
            if isinstance(child, list):
                debug(f"iter():  gonna iter over {child}")
                iter(child)
            else:
                debug(f"iter():  appending {child}")
                serialized.append(child)

        debug(f"\niter():  exiting {li}\n\n -> serialized: {serialized}\n")

    iter(body)

    debug(f"_serialize_body():  - exiting -> serialized: {serialized}\n")

    return serialized


def __set__(node, scope):
    debug(f"__set__():  backend")

    import eval
    import list as list_

    _validate_set(node, scope)

    name = node[1]
    value = node[2]

    name_value = eval.get_name_value(name, scope)
    debug(f"__set__():  backend - name: {name} name_value: {name_value} value: {value} {type(value)}")

    type_ = _convert_type(name_value[2])

    template = []

    if isinstance(value, list):
        debug(f"__set__():  backend - value is list, going to return_call() it - value: {value}")

        tmp_name = _get_NAME(functions_stack[0][0], name)
        _increment_NAME(functions_stack[0][0], name)

        printed_list = list_.list_print(value)

        evaluated_value = return_call(value, scope)

        template.append(evaluated_value[1])
        template.append(f"""\t\t; set "{name}" value as result of "{printed_list}"
\t\t%{tmp_name} = {evaluated_value[0]}
\t\tstore {type_} %{tmp_name}, {type_}* %{name}_stack""")

    else:

        template.append(f"""\t\t; set "{name}" value as "{value}"
\t\tstore {type_} {value}, {type_}* %{name}_stack""")

    debug(f"__set__():  backend - template: {template}")

    return template


def _validate_set(node, scope):

    debug(f"_validate_set():  backend - node: {node}")

    # validate name mutability
    name = None
    if isinstance(node[1], list):
        name = node[1][0]

    else:
        name = node[1]

    name_value = eval.get_name_value(name, scope)
    debug(f"_validate_set():  backend - name_value: {name_value}")

    # useful for checking set inside functions that couldn't be checked at frontend phase
    if name_value[1] == "const":
        raise Exception(f"Resetting constant name: {node} {name_value}")

# ARRAY INTERNALS
#


def __set_array_member__(node, scope):
    _validate_set_array_member(node, scope)

    node, name, indexes, value = node

    name_value = eval.get_name_value(name, scope)

    type_ = name_value[2]
    converted_type = _convert_type(type_)
    if converted_type[-1] == "*":
        converted_type = converted_type[0:-1]

    import list as list_

    # iter over indexes
    template = []
    index = None
    lp_reference = list_.list_print(indexes)

    debug(f"__set_array_member__():  backend - indexes: {indexes}")
    for i in indexes:
        debug(f"__set_array_member__():  backend - i: {i}")
        # test if they're int-able
        int_index = True
        try:
            int(i)
        except BaseException:
            int_index = False

        debug(f"__set_array_member__():  backend - int_index: {int_index}")

        # not int-able
        if int_index:
            index = i

        else:
            # try to solve variable name
            index_name_value = eval.get_name_value(i, scope)
            i_name, i_mutdecl, i_type, i_value = index_name_value

            index = f"%{i_name}"

            debug(f"__set_array_member__():  backend - index: {index} index_name_value: {index_name_value}")

        # index is set
        template.append(f"""\t\t; set "{name}" member "{lp_reference}"
""")

        if not _already_declared(functions_stack[0][0], f"{name}_members_ptr"):
            _declare_name(functions_stack[0][0], f"{name}_members_ptr")
            template.append(f"""\t\t; get members pointer
\t\t%{name}_members_ptr = getelementptr i8*, i8** %{name}
""")

        template.append(f"""\t\t%{name}_members_ptr_ = load i8*, i8* %{name}_members_ptr

\t\t; get specific member pointer
\t\t%{name}_member_ptr = getelementptr i8, i8** %{name}_members_ptr_, i64 {index}
""")

        # TODO: multidimensional arrays
        # break at first index
        break

    debug(f"__set_array_member__():  backend - index: {index}")

    infered_value = eval._infer_type(value)
    debug(f"__set_array_member__():  backend - value: {value} infered_value: {infered_value}")

    if infered_value is not None:
        converted_infered_type = _convert_type(infered_value[0])
        debug(f"__set_array_member__():  backend - converted_infered_type: {converted_infered_type}")

        if infered_value[0] in ["int", "uint"] and value[:2] == "0x":
            mangled_value = int(value, base=16)
        else:
            mangled_value = value

        template.append(f"""\t\t; store "{value}" value at member pointer
\t\tstore {converted_infered_type} {mangled_value}, i8** %{name}_member_ptr
""")

    else:

        name_value_ = eval.get_name_value(value, scope)
        function_name = functions_stack[0][0]

        if name_value_[1] == "const":
            template.append(f"""\t\tstore {converted_type} %{name_value_[0]}, i8** %{name}_member_ptr
""")

        elif name_value[1] == "mut":
            tmp_name_value = _get_NAME(function_name, value)
            _increment_NAME(function_name, value)

            template.append(f"""\t\t%{tmp_name_value} = load {converted_type}, {converted_type}* %{value}_stack
\t\t; store value at member pointer
\t\tstore {converted_type} %{tmp_name_value}, i8** %{name}_member_ptr
""")

    return template


def _validate_set_array_member(node, scope):
    import frontend.compiletime as ct
    ct.validate_set_array_member(node, scope)


def __get_array_member__(node, scope):
    debug(f"__get_array_member__():  node: {node} scope: {hex(id(scope))}")

    # _validate_get_array_member(node, scope)

    def_, mutdecl, name, data = node
    debug(f"__get_array_member__():  data: {data}")

    ref_array_member_, array_name, array_index = data[1]

    type_ = data[0]
    converted_type = _convert_type(type_)
    if converted_type[-1] == "*":
        converted_type = converted_type[0:-1]

    function_name = functions_stack[0][0]
    # tmp_name = _get_NAME(function_name, name)
    # _increment_NAME(function_name, name)

    array_size_tmp_name = _get_NAME(function_name, f"{array_name}_size")
    _increment_NAME(function_name, f"{array_name}_size")

    array_inbounds_tmp_name = _get_NAME(function_name, f"{array_name}_inbounds")
    _increment_NAME(function_name, f"{array_name}_inbounds")

    template = f"""\t\t; check array index bound
\t\t; load array size
\t\t%{array_size_tmp_name} = load i64, i64* %{array_name}_size_ptr
\t\t; compare array size and index
\t\t%{array_inbounds_tmp_name} = icmp ult i64 {array_index}, %{array_size_tmp_name}
\t\t; branch
\t\tbr i1 %{array_inbounds_tmp_name}, label %{array_inbounds_tmp_name}_ok, label %{array_inbounds_tmp_name}_err
\t{array_inbounds_tmp_name}_err:
\t\t; TODO: write to stderr
\t\t; exit
\t\tcall void @linux_exit(i64 -1)
\t\tunreachable
\t{array_inbounds_tmp_name}_ok:
\t\t; get array member
\t\t%{array_name}_{array_index}_ptr = getelementptr {converted_type}, {converted_type}* %{array_name}_members, i32 {array_index}
\t\t%{name} = load {converted_type}, {converted_type}* %{array_name}_{array_index}_ptr
"""

    return template


def _validate_get_array_member(node, scope):
    import frontend.compiletime as ct
    ct.validate_get_array_member(node, scope)
#
#

# STRUCT INTERNALS
#


def __set_struct_member__(node, scope):
    _validate_set_struct_member(node, scope)

    set_struct_member_, struct_name, struct_member, value = node

    struct_name_value = eval.get_name_value(struct_name, scope)
    debug(f"__set_struct_member__():  struct_name_value: {struct_name_value}")

    structdef_name = struct_name_value[2]
    structdef_name_value = eval.get_name_value(struct_name_value[2], scope)

    members = structdef_name_value[3]
    debug(f"__set_struct_member__():  members: {members}")

    member_type = ""
    for member_index, member in enumerate(members):
        debug(f"__set_struct_member__():  member: {member}")

        if member[1] == struct_member:
            member_type = _convert_type(member[0])
            break

    stack = []

    if not _already_declared(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr"):
        _declare_name(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr")
        stack.append(f"""\t\t; get struct "{structdef_name}" "{struct_name}" member "{struct_member}" pointer
\t\t%{struct_name}_{struct_member}_member_ptr = getelementptr {member_type}, %{structdef_name}* %{struct_name}, i64 {member_index}
""")

    stack.append(f"""\t\t; set struct "{structdef_name}" "{struct_name}" member "{struct_member}"
\t\tstore {member_type} {value}, {member_type}* %{struct_name}_{struct_member}_member_ptr
""")

    return "\n".join(stack)


def _validate_set_struct_member(node, scope):
    import frontend.compiletime as ct
    ct.validate_set_struct_member(node, scope)


def __get_struct_member__(node, scope):
    #    _validate_get_struct_member(node, scope)

    debug(f"__get_struct_member__():  node: {node}")

    def_, mutdecl, name, data = node
    debug(f"__get_struct_member__():  data: {data}")

    stack = []

    def loop(data, lvl):
        debug(f"__get_struct_member__():  loop():  data: {data}")

        child_is_ref_member = isinstance(data[1], list) and data[1][0] == "ref_member"
        debug(f"__get_struct_member__():  loop():  child_is_ref_member: {child_is_ref_member}")

        ref_member_, struct_name, struct_member = data

        if child_is_ref_member:
            struct_name = loop(data[1], lvl + 1)
            debug(f"__get_struct_member__():  loop():  new struct_name: {struct_name}")

        debug(f"__get_struct_member__():  loop():  struct_name: {struct_name} struct_member: {struct_member} data: {data}")

        struct_name_value = eval.get_name_value(struct_name, scope)
        debug(f"__get_struct_member__():  loop():  struct_name_value: {struct_name_value}")

        structdef_name = struct_name_value[2]
        structdef_name_value = eval.get_name_value(struct_name_value[2], scope)

        members = structdef_name_value[3][0]
        debug(f"__get_struct_member__():  loop():  members: {members}")

        member_type = ""
        for member_index, member in enumerate(members):
            debug(f"__get_struct_member__():  loop():  member: {member}")

            # check if member is struct
            # member_name_value = eval.get_name_value(member[1], scope)
            # if member_name_value != [] and member_name_value[2] == "struct":
            #    member_type = f"%{member[1]}*"

            if member[0] == struct_member:
                member_type = _convert_type(member[1], scope)
                break

        if not _already_declared(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr"):
            _declare_name(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr")
            stack.append(f"""\t\t%{struct_name}_{struct_member}_member_ptr = getelementptr {member_type}, %{structdef_name}* %{struct_name}, i64 {member_index}""")

        debug(f"__get_struct_member__():  loop():  new stack: {stack}")

        if lvl > 0:
            return struct_name_value[3][member_index]

        else:
            return [member_type, struct_name, struct_member]

    x = loop(data[1], 0)
    member_type, struct_name, struct_member = x
    debug(f"__get_struct_member__():  x: {x}")

    debug(f"__get_struct_member__():  stack: {stack}")

#    get_struct_member_, struct_name, struct_member = data[1]
#
#    debug(f"__get_struct_member__():  struct_name: {struct_name} struct_member: {struct_member}")
#
#    struct_name_value = eval.get_name_value(struct_name, scope)
#    debug(f"__get_struct_member__():  struct_name_value: {struct_name_value}")
#
#    structdef_name = struct_name_value[2]
#    structdef_name_value = eval.get_name_value(struct_name_value[2], scope)
#
#    members = structdef_name_value[3][0]
#    debug(f"__get_struct_member__():  members: {members}")
#
#    member_type = ""
#    for member_index, member in enumerate(members):
#        debug(f"__get_struct_member__():  member: {member}")
#
#        if member[0] == struct_member:
#            member_type = _convert_type(member[1])
#            break
#
#    stack = []
#
#    if not _already_declared(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr"):
#        _declare_name(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr")
#        stack.append(f"""\t\t%{struct_name}_{struct_member}_member_ptr = getelementptr {member_type}, %{structdef_name}* %{struct_name}, i64 {member_index}""")

    _declare_name(functions_stack[0][0], f"{name}")
    stack.append(f"""\t\t; get struct member
\t\t%{name} = load {member_type}, {member_type}* %{struct_name}_{struct_member}_member_ptr
""")

    return "\n".join(stack)


# def _validate_get_struct_member(node, scope):
#    # Removed because backend must handle struct member access differently
#    #import frontend.compiletime as ct
#    #ct.validate_get_struct_member(node, scope)
#
#    ref_member_node = node[3][1]

#
#


def __ref_member__(node, scope):
    debug(f"__ref_member__():  node: {node} scope: {hex(id(scope))}")

    return ["yaya"]

#    return __get_struct_member__(node, scope)

#    # TODO: add validation for members existence
#
#    # get struct
#    ref_member, struct_name, struct_member = node
#
#    struct = eval.get_name_value(struct_name, scope)
#    debug(f"__ref_member__():  struct: {struct}")
#
#    struct_def_name = struct[2]
#    debug(f"__ref_member__():  struct_def_name: {struct_def_name}")
#
#    struct_def_name_value = eval.get_name_value(struct_def_name, scope)
#    debug(f"__ref_member__():  struct_def_name_value: {struct_def_name_value}")
#
#    # get struct member
#    found_member = None
#    found_member_index = None
#    for member_index, member in enumerate(struct_def_name_value[3][0]):
#        debug(f"__ref_member__():  member: {member}")
#        if member[0] == struct_member:
#            found_member = member
#            found_member_index = member_index
#            break
#
#    debug(f"__ref_member__():  found_member: {found_member} found_member_index: {found_member_index}")
#
#    # get struct member type
#    member_type = found_member[1]
#    debug(f"__ref_member__():  member_type: {member_type}")
#
#    converted_member_type = _convert_type(member_type)
#    debug(f"__ref_member__():  converted_member_type: {converted_member_type}")
#
#    stack = []
#
#    debug(f"__ref_member__():  functions_stack: {functions_stack[0]}")
#
#    if not _already_declared(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr"):
#        _declare_name(functions_stack[0][0], f"{struct_name}_{struct_member}_member_ptr")
#        stack.append(f"""\t\t%{struct_name}_{struct_member}_member_ptr = getelementptr {member_type}, %{struct_def_name}* %{struct_name}, i64 {member_index}""")
#
#    stack.append(f"""\t\t; get struct "{struct_def_name}" "{struct_name}" member "{struct_member}"
# \t\tload {member_type}, {member_type}* %{struct_name}_{struct_member}_member_ptr
# """)
#
#    retv = "\n".join(stack)
#
#    debug(f"__ref_member__():  retv: {retv}")
#
#    return retv


def __ref_array_member__(node, scope):
    debug(f"__ref_array_member__():  node: {node} scope: {hex(id(scope))}")
    return ['yaya']


def __macro__(node, scope):
    return []


def __if__(node, scope):
    _validate_if(node, scope)

    debug(f"__if__():  backend - node: {node}")

    import eval

    stack = ["\t; if start"]

    # extract elifs from node
    elifs = [child for child in node[3:] if isinstance(child, list) and len(child) > 0 and child[0] == "elif"]
    debug(f"__if__():  backend - elifs: {elifs}")

    # extract else from node
    else_ = [child for child in node[2:] if isinstance(child, list) and len(child) > 0 and child[0] == "else"]
    debug(f"__if__():  backend - !!!! else_: {else_}")

    if len(else_) > 0:
        else_ = else_[0]
    else:
        else_ = None

    debug(f"__if__():  backend - else_: {else_}")

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
    debug(f"__if__():  backend - then_code: {then_code}")

    stack += [f"\t\t; if - then code block\n\t{then_label}:"] + then_code + [f"\t\tbr label %{end_label}\n"]

    x_size = len(node[3:])
    debug(f"__if__():  backend - x_size: {x_size}")

    for else_index in range(0, 0 + x_size):
        item = node[else_index + 3]
        debug(f"__if__():  backend - else_index: {else_index} item: {item}")

        # handle elif
        if len(item) > 0 and item[0] == "elif":
            debug("__if__():  backend - elif")

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
            debug(f"__if__():  backend - elif_condition_ir: {elif_condition_ir}")

            stack += [elif_condition_ir]

            # get elif code
            elif_code = eval.eval(item[2], scope)
            debug(f"__if__():  backend - elif_code: {elif_code}")

            stack += [f"\t\t; if - elif code block\n\t{elif_label}:"]
            stack += elif_code
            stack += [f"""\t\tbr label %{end_label}\n"""]

        else:
            debug(f"__if__():  backend - else - item: {item}")

            if len(item) == 0:
                continue

            else_code = eval.eval(item[1], scope)
            debug(f"__if__():  backend - else_code: {else_code}")

            stack += [f"\t\t; if - else code block\n\t{else_label}:"] + else_code + [f"""
\t\tbr label %{end_label}\n"""]

    stack += [f"""\t\t; if - end block
\t{end_label}:
\t; if end
"""]

    debug(f"__if__():  backend - stack: {stack}")

    S = _serialize_body(stack)
    # print(f"S: {S}")

    result = "\n".join(S)
    # result = "\n".join(stack)
    debug(f"__if__():  backend - result: {result}")

    return result


def _validate_if(node, scope):
    pass


def _get_condition_ir(node, scope, then_label, x_label):
    debug(f"_get_condition_ir():  node: {node} scope: {hex(id(scope))} then_label: {then_label} x_label: {x_label}")

    import eval
    condition_name = _get_var_name("if", "condition_")

    if isinstance(node[1], list):
        condition_function = eval.get_name_value(node[1], scope)
        condition_call, stack = return_call(node[1], scope, [])
        debug(f"_get_condition_ir():  backend - condition_call: {condition_call}")

        retv = stack + [f"""\t\t%{condition_name}  = {condition_call}
\t\tbr i1 %{condition_name}, label %{then_label}, label %{x_label}\n"""]
        return "\n".join(retv)

    else:
        # try to infer type
        infered_type_value = eval._infer_type(node[1])
        debug(f"infered_type_value: {infered_type_value}")

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
            debug(f"_get_condition_ir():  backend - name_value: {name_value}")

            if len(name_value) == 0:
                raise Exception(f"Unassigned name: {node[1]}")

            if name_value[2] != "bool":
                raise Exception("Invalid value for if test: {node}")

            value = "1" if name_value[3] == "true" else "0"

        return f"\t\tbr i1 {value}, label %{then_label}, label %{x_label}\n"


def __elif__(node, scope):
    debug(f"__elif__():  backend - node: {node}")


def __data__(node, scope):
    return node[1:]


def __write_ptr__(node, scope):
    return []


def __read_ptr__(node, scope):
    return []


def __get_ptr__(node, scope):
    debug(f"__get_ptr__():  backend - node: {node}")

    import frontend.compiletime as ct
    ct.validate_get_ptr(node, scope)

    get_ptr, name = node

    name_value = eval.get_name_value(name, scope)
    debug(f"__get__ptr__():  backend - name_value: {name_value}")
    type_ = _convert_type(name[2])

    template = f"\t\t%{name}_ptr = getelementptr {type_}, {type_}* %{name}"

    debug(f"__get_ptr__():  backend - template: {template}")

    return template


def __size_of__(node, scope):
    return []


def __unsafe__(node, scope):
    return []


def __linux_write__(node, scope):
    debug(f"__linux_write__():  node: {node}")

    _validate_linux_write(node, scope)

    # convert fd
    from eval import eval, get_name_value, is_global_name

    # fd = eval([node[1]], scope)
    # debug(f"__linux_write__():  fd: {fd}")
    # fd[0] = _convert_type(fd[0])
    # fd_arg = " ".join(fd)

    name_value = get_name_value(node[1], scope)
    debug(f"__linux_write__():  name_value: {name_value}")

    is_global = is_global_name(name_value, scope)
    debug(f"__linux_write__():  is_global: {is_global}")
    if is_global and name_value[1] == "const":
        converted_type = _convert_type(name_value[2])
        fd_arg = f"{converted_type}* @{node[1]}"

    else:
        debug(f"__linux_write__(): other!")

    text = node[2]

    template = f"""
\t\t%str_addr_ptr = getelementptr i8*, %struct.Str* %text, i64 0
\t\t%str_size_ptr = getelementptr i64, %struct.Str* %text, i64 1

\t\t%fd = load i64, {fd_arg}
\t\t%addr = load i8*, i8** %str_addr_ptr
\t\t%size = load i64, i64* %str_size_ptr

\t\tcall void @linux_write(i64 %fd, i8* %addr, i64 %size)
"""

    return template.split("\n")


def _validate_linux_write(node, scope):
    if len(node) != 3:
        raise Exception(f"Wrong number of arguments for linux_write: {node}")


def return_call(node, scope, stack=[]):
    debug(f"return_call():  node: {node} scope: {hex(id(scope))} stack: {stack}")

    li_name = node[0]

    value = eval.get_name_value(li_name, scope)
    debug(f"return_call():  value: {value}")

    if value == []:
        raise Exception(f"No name matches for name: {li_name}")

    if value[2] == "fn":
        debug(f"return_call():  calling a function")

        method, solved_arguments = eval.find_function_method(node, value, scope)
        debug(f"return_call():  method: {method}")

        function_arguments = method[0][0]
        debug(f"return_call():  function_arguments: {function_arguments}")

        function_name = _unoverload(li_name, function_arguments)
        debug(f"return_call():  function_name: {function_name}")

        # find out arguments
        converted_arguments = []
        for argument_index, argument in enumerate(function_arguments):
            debug(f"return_call():  argument: {argument}")

            if len(argument) == 2:
                name, type_ = argument
            elif len(argument) == 3 and argument[1] == "mut":
                name, mutdecl, type_ = argument

            converted_type = _convert_type(type_)

            # fulfill llvm requirement to convert float values types to doubles
            if converted_type == "float":
                converted_type = "double"

            argument_value = node[argument_index + 1]
            debug(f"return_call():  argument_value: {argument_value}")

            if isinstance(argument_value, list):
                debug(f"return_call():  argument_value is list - argument_value: {argument_value}")

                scope_argument_value = eval.get_name_value(argument_value[0], scope)

                debug(f"return_call():  before return_call() call - stack: {stack}\n")

                result, stack = return_call(argument_value, scope, stack.copy())

                debug(f"return_call():  after return_call() call - result: {result} stack_: {stack}")

                var_name_function = functions_stack[0][0]

                tmp = _get_var_name(var_name_function, "tmp_")
                call_ = f"\t\t%{tmp} = {result}"

                debug(f"return_call():  appending call_ {call_} to stack")

                stack.append(call_)

                debug(f"return_call():  stack after append: {stack}")

                argument_value = f"%{tmp}"

            else:
                debug(f"return_call():  argument_value isn't list - argument_value: {argument_value}")

                scope_argument_value = eval.get_name_value(argument_value, scope)
                debug(f"return_call():  scope_argument_value: {scope_argument_value}")

                if scope_argument_value != []:
                    argument_name = False
                    if len(functions_stack) > 0:
                        debug(f"return_call():  len(functions_stack) > 0")

                        arguments_matches = [arg for arg in functions_stack[len(functions_stack) - 1][2] if argument_value == arg[0]]
                        # print(f"arguments_matches: {arguments_matches}")

                        if len(arguments_matches) > 0:
                            argument_value = f"%{argument_value}"
                            argument_name = True

                    if not argument_name:
                        debug(f"return_call():  not argument_name")

                        # check for generic types
                        if isinstance(scope_argument_value[2], list):
                            debug(f"return_call():  scope_arguent_value[2] is list")

                            if scope_argument_value[2][0] == "Array":
                                argument_value = f"%{argument_value}"

                        # not generic types
                        else:
                            debug(f"return_call():  scope_arguent_value[2] isn't list")

                            if scope_argument_value[1] == 'const':
                                debug(f"return_call():  scope_argument_value is const - argument_value: {argument_value}")

                                if scope_argument_value[2] in ["int", "uint", "byte"]:
                                    debug(f"return_call():  scope_argument_value is int")
                                    argument_value = f"%{argument_value}"

                                else:
                                    debug(f"return_call():  scope_argument_value isn't int")
                                    cur_function_name = functions_stack[0][0]  # "main_"
                                    argument_value = f"@{cur_function_name}{argument_value}"
                                    converted_type += "*"

                            elif scope_argument_value[1] == 'mut':
                                debug(f"return_call():  scope_argument_value is mut")
                                NAME = _get_NAME(function_name, argument_value)
                                argument_value = f"%{NAME}"

                    # print(f"argument_value: {argument_value}")

            converted_argument = f"{converted_type} {argument_value}"

            debug(f"return_call():  converted_argument: {converted_argument}")

            converted_arguments.append(converted_argument)

        converted_function_arguments = ", ".join(converted_arguments)

        # find out return type
        if len(method) == 2:
            function_return_type = "void"

        elif len(method) == 3:
            function_return_type = _convert_type(method[1])

        ret_value = f"call {function_return_type} @{function_name}({converted_function_arguments})"

    elif value[2] == "internal":
        debug(f"return_call():  calling an internal")

        ret_value = value[3](node, scope)

    debug(f"return_call():  exiting return_call():  value: {value} ret_value: {ret_value} stack: {stack}\n")

    return ret_value, stack


_var_names = {}


def _get_var_name(function_name, prefix):
    debug(f"_get_var_name():  function_name: {function_name} prefix: {prefix}")

    # initialize key in _var_names for function_name
    if function_name not in _var_names.keys():
        _var_names[function_name] = 0

    # get name
    var_name = f"{prefix}{_var_names[function_name]}"

    # increment counter
    _var_names[function_name] += 1

    debug(f"_get_var_name():  var_name: {var_name}")

    return var_name


_names_storage = {}


def _get_NAME(function_name, name):
    debug(f"_get_NAME():  function_name: {function_name} name: {name}")

    # initialize key in _names_storage for function_name
    if function_name not in _names_storage.keys():
        _names_storage[function_name] = {}

    # initialize key in _names_storage[function_name] for name
    if name not in _names_storage[function_name].keys():
        _names_storage[function_name][name] = 0

    NAME = f"{name}_{_names_storage[function_name][name]}"

    debug(f"_get_NAME():  NAME: {name}")

    return NAME  # _names_storage[function_name][name]


def _increment_NAME(function_name, name):
    debug(f"_increment_NAME():  function_name: {function_name} name: {name}")
    _names_storage[function_name][name] += 1


_declared_names = {}


def _declare_name(function_name, name):
    if function_name not in _declared_names.keys():
        _declared_names[function_name] = []

    _declared_names[function_name].append(name)


def _already_declared(function_name, name):
    return function_name in _declared_names.keys() and name in _declared_names[function_name]


# SCOPE HOOKS
#
def return_call_common_list(evaled, name_match, scope):
    debug(f"return_call_common_list():  evaled: {evaled} name_match: {name_match}")

    # check if is returning a name storing a struct member value
    if name_match[3][0] == "ref_member" or name_match[3][0] == "ref_array_member":
        name_match_type = name_match[2]
        type_return_call = _convert_type(name_match_type)
        name_return_call = f"%{name_match[0]}"

    else:
        evaled_fn = eval.get_name_value(evaled[0], scope)
        method, solved_arguments = eval.find_function_method(evaled, evaled_fn, scope)
        method_type = method[1]

        if name_match[2] != method_type:
            raise Exception(f"Name and evaluated value types are different - name_match type: {name_match[2]} - method_type: {method_type}")

        debug(f"_return_call_common():  new method_type: {method_type}")

        # TODO: get correct return type and result name

        # get type
        type_return_call = "i64"

        # get var name
        name_return_call = "%result"

    li = [f"\t\tret {type_return_call} {name_return_call}"]

    return li


def return_call_common_not_list(name_match, scope):
    debug(f"""_eval_handle_common():  backend scope - function_depth: {scope["function_depth"]} - is_last: {scope["is_last"]}""")

    if scope["is_last"] and scope["function_depth"] == 1:
        converted_type = _convert_type(name_match[2])
        li = [f"\t\tret {converted_type} %{name_match[0]}"]

    else:
        li = ["\t\t; NOT IMPLEMENTED"]

    return li
#
#


scope = copy.deepcopy(eval.default_scope)


def _setup_scope():
    from . import bool as bool_
    from . import uint as uint
    from . import int as int_
    from . import float as float_
    from . import byte as byte

    names = [
    ["fn", "mut", "internal", __fn__],
    ["def", "mut", "internal", __def__],
    ["set", "mut", "internal", __set__],
    ["set_array_member", "mut", "internal", __set_array_member__],
    ["get_array_member", "mut", "internal", __get_array_member__],
    ["set_struct_member", "mut", "internal", __set_struct_member__],
    ["get_struct_member", "mut", "internal", __get_struct_member__],
    ["ref_member", "mut", "internal", __ref_member__],
    ["ref_array_member", "mut", "internal", __ref_array_member__],
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

    ["add_byte_byte", "const", "internal", byte.__add_byte_byte__],

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
        scope["names"].append(name)

    scope["return_call"] = return_call
    scope["return_call_common_list"] = return_call_common_list
    scope["return_call_common_not_list"] = return_call_common_not_list
    scope["step"] = "backend"


_setup_scope()
