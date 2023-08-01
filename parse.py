def parse(token_list):
    token_list = _listfy_par_groups(token_list)

    token_list = _join_quoted_values(token_list)

    return token_list


def _listfy_par_groups(token_list):
    token_list_copy = token_list.copy()
    tc2 = token_list.copy()

    found = True
    while found:
        # print(f"\n while found - tc2:")
        # for we in tc2:
        #   print(f"  -> {we}")
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

        # print(f"par_opens: {par_opens} {len(par_opens)}")
        # print(f"par_closes: {par_closes} {len(par_closes)}")
        # print(f"all_pars: {all_pars}\n")

        to_remove = []
        li = []
        for par_index, par in enumerate(all_pars.copy()):
            # print(f"itering over par {par_index} {par}")
            if par[1][1] != "PAR_CLOSE":
                # print(f"par[1][1] != PAR_CLOSE {par_index} {par}")
                continue

            # print(f"found PAR_CLOSE: {par_index} {par}")

            for i in reversed(all_pars[0:par_index]):
                # print(f"itering over I {i}")
                if i[1][1] != "PAR_OPEN":
                    # print(f"i[i][i] != PAR_OPEN {i}")
                    continue

                to_remove.append(i)
                to_remove.append(all_pars[par_index])

                end = all_pars[par_index][0]
                start = i[0] + 1
                # print(f"start: {start}")
                # print(f"end: {end}")

                for j in range(start, end):
                    to_remove.append([j, tc2[j]])
                    li.append(tc2[j])

                found = True
                break

            for tr in to_remove:
                # print(f"tr: {tr}")
                tc2.remove(tr[1])

            tc2.insert(to_remove[0][0], ["LIST", li])

            if found:
                break

    return tc2


def _join_quoted_values(token_list):
    # print(f"_join_quoted_values - token_list: {token_list}")
    quotes = []

    # for
    return token_list
