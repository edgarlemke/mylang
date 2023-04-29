def parse(token_list):
    token_list = _listfy_par_groups(token_list)
    token_list = _listfy_blocks(token_list)
    return token_list


def _listfy_par_groups(token_list):
    token_list_copy = token_list.copy()
    tc2 = token_list.copy()

    found = True
    while found:
        # print(f"\n\nw tc2: {tc2}")
        found = False
        # import time
        # time.sleep(1)

        par_opens = []
        par_closes = []

        all_pars = []

        for index, token in enumerate(tc2):
            if len(token) == 0:
                continue
            if token[1] not in ["PAR_OPEN", "PAR_CLOSE"]:
                continue

            if token[1] == "PAR_OPEN":
                par_opens.append([index, token])
                all_pars.append([index, token])

            elif token[1] == "PAR_CLOSE":
                par_closes.append([index, token])
                all_pars.append([index, token])

        to_remove = []
        li = []
        for par_index, par in enumerate(all_pars.copy()):
            if par[1][1] != "PAR_CLOSE":
                continue

            for i in reversed(all_pars[0:par_index]):
                if i[1][1] != "PAR_OPEN":
                    continue

                to_remove.append(i)
                to_remove.append(all_pars[par_index])

                end = all_pars[par_index][0]
                start = i[0] + 1

                for j in range(start, end):
                    to_remove.append([j, tc2[j]])
                    li.append(tc2[j])

                found = True
                break

            for tr in to_remove:
                tc2.remove(tr[1])

            tc2.insert(to_remove[0][0], ["LIST", li])

            if found:
                break

    return tc2


def _listfy_blocks(token_list):
    token_list_copy = token_list.copy()

    block_buf = []
    for index, token in enumerate(token_list):
        if len(token) == 0 or token[0] != "TOKEN":
            continue

        if token[1] == "BLOCK_START":
            block_buf.append([index, token])

        elif token[1] == "BLOCK_END":
            block_end = token
            block_end_index = index

            block_start_index, block_start = block_buf.pop()
            content = token_list[block_start_index + 1: block_end_index]

            list_ = [block_start] + content + [block_end]
            for token_to_remove in list_:
                token_list_copy.remove(token_to_remove)

            token_list_copy.insert(block_start_index, ["BLOCK", content])

    return token_list_copy
