#!/usr/bin/python3
from shared import debug


def parse(token_list):
    debug(f"parse():  token_list: {token_list}")

    listfied_par_groups_token_list = _listfy_par_groups(token_list)
    debug(f"parse():  listfied_par_groups_token_list: {listfied_par_groups_token_list}")

    joined_quoted_values_token_list = _join_quoted_values(listfied_par_groups_token_list)
    debug(f"parse():  joined_quoted_values_token_list: {joined_quoted_values_token_list}")

    return joined_quoted_values_token_list


def _listfy_par_groups(token_list):
    debug(f"_listfy_par_groups():  token_list: {token_list}")

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

        debug(f"_listfy_par_groups():  par_opens: {par_opens} length: {len(par_opens)}")
        debug(f"_listfy_par_groups():  par_closes: {par_closes} length: {len(par_closes)}")
        debug(f"_listfy_par_groups():  all_pars: {all_pars}\n")

        to_remove = []
        li = []

        # iter over a copy of all_pars, looking for PAR_CLOSEs
        for par_index, par in enumerate(all_pars.copy()):
            debug(f"_listfy_par_groups():  itering over all_pars copy - par_index: {par_index} par: {par}")

            if par[1][1] != "PAR_CLOSE":
                debug(f"_listfy_par_groups():  skipping - par[1][1] != PAR_CLOSE {par_index} {par}")
                continue

            debug(f"_listfy_par_groups():  found PAR_CLOSE: {par_index} {par}")

            for i in reversed(all_pars[0:par_index]):
                debug(f"_listfy_par_groups():  reverse itering over all_pars[0:par_index] - i: {i}")

                if i[1][1] != "PAR_OPEN":
                    debug(f"_listfy_par_groups():  i[1][1] != PAR_OPEN - i: {i}")
                    continue

                debug(f"_listfy_par_groups():  appending i to to_remove - i: {i}")
                to_remove.append(i)

                debug(f"_listfy_par_groups():  appending all_pars[par_index] to to_remove - all_pars[par_index]: {all_pars[par_index]}")
                to_remove.append(all_pars[par_index])

                end = all_pars[par_index][0]
                start = i[0] + 1
                debug(f"_listfy_par_groups():  start: {start}")
                debug(f"_listfy_par_groups():  end: {end}")

                for j in range(start, end):
                    debug(f"_listfy_par_groups():  j: {j} appending to to_remove: {[j, tc2[j]]} appending to li: {tc2[j]}")
                    to_remove.append([j, tc2[j]])
                    li.append(tc2[j])

                found = True
                break

            debug(f"_listfy_par_groups():  to_remove: {to_remove}")

            for tr in to_remove:
                debug(f"_listfy_par_groups():  tr: {tr}")
                tc2.remove(tr[1])

            to_insert = ["LIST", li]
            debug(f"_listfy_par_groups():  inserting at tc2 - to_remove[0][0]: {to_remove[0][0]}  list: {to_insert}")
            tc2.insert(to_remove[0][0], to_insert)

            if found:
                break

    debug(f"_listfy_par_groups():  tc2: {tc2}")

    return tc2


def _join_quoted_values(token_list):
    # print(f"_join_quoted_values - token_list: {token_list}")
    quotes = []

    # for
    return token_list
