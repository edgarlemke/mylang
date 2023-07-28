def read_file(src):
    # create a file descriptor for the src file
    with open(src, "r") as fd:

        # read all content of the file into an variable
        code = fd.readlines()
        expr = "".join(code)

        return expr
