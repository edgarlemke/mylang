#!/usr/bin/python3


def load_pkgs(s_tree, src=None, loaded_pkg_files=None):
    import run

    use_decls = [node for node in s_tree if node[0] == "USE_DECL"]
    # print(use_decls)

    pkgs_to_load = []
    for i in use_decls:
        children = i[2]
        for ch in children:
            pkg_name = s_tree[ch][1]
            pkgs_to_load.append(pkg_name)

    # print(pkgs)

    path = [_get_mylang_dir(), _get_wd()]
    # print(path)

    all_files = []
    for p in path:
        _load_dir(p, all_files)
    # print(all_files)

    if loaded_pkg_files is None:
        loaded_pkg_files = []

    l_pkgs = {}
    for f in all_files:
        if f == src or f in loaded_pkg_files:
            continue

        for p in path:
            # print(p)
            # print(f[0:len(p)])

            if f[0:len(p)] == p:
                li = f[len(p) + 1:].split("/")
                last = li[-1:][0][:-7]
                li[len(li) - 1] = last

                final = " ".join(li)

                l_pkgs[final] = f

    # print(l_pkgs)
    # print(pkgs_to_load)

    loaded_pkgs = {}
    for pkg in pkgs_to_load:
        if pkg not in l_pkgs.keys():
            raise Exception(f"Package not found: {pkg}")

        path = l_pkgs[pkg]
        loaded_pkg_files.append(path)
        expr = run.read_file(path)
        loaded_pkgs[pkg] = run.run(
            expr, src=path, loaded_pkg_files=loaded_pkg_files)

    return loaded_pkgs


def _load_dir(path, all_files):
    import os

    for (root, dir_, files) in os.walk(path):
        for f in files:
            if f[-7:] != ".mylang":
                continue
            path = f"{root}/{f}"
            if path in all_files:
                continue
            all_files.append(path)


def _get_mylang_dir():
    import os
    d = os.path.dirname(os.path.realpath(__file__))
    return f"{d}/pkg"


def _get_wd():
    import os
    wd = os.getcwd()
    return wd


def get_pkg_name(src):
    import os
    from pathlib import Path

    path = os.path.realpath(src)
    dir_ = os.path.dirname(path)

    mylang_pkg_dir = _get_mylang_dir()
    is_local = False
    if mylang_pkg_dir == dir_[0:len(mylang_pkg_dir)]:
        project_dir = mylang_pkg_dir

    else:
        def _find_project_dir(dir_):
            if os.path.isfile(f"{dir_}/pkg"):
                return dir_

            parent = Path(dir_).parent

            # if found filesystem root return False
            if dir_ == parent:
                return False

            return _find_project_dir(parent)

        project_dir = _find_project_dir(dir_)
        if project_dir == False:
            raise Exception(
                f"No project file found going upwards in file tree: {src}")

        is_local = True

    splited = [i for i in src[len(project_dir):].split("/") if len(i) > 0]
    file_ = splited[len(splited) - 1][:-7]
    splited[len(splited) - 1] = file_

    pkg_name = " ".join(splited)
    if is_local:
        pkg_name = f".{pkg_name}"

    return pkg_name
