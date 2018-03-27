import sys

from pprint import pprint

from factoring.interfaces import factor

_PY2 = sys.version_info.major == 2
if _PY2:
    input = raw_input


def sanitised_input(description, variable, range_):
    start = range_[0]
    stop = range_[-1]

    while True:
        ui = input("Input {:15}({:2} <= {:1} <= {:2}): ".format(description, start, variable, stop))

        try:
            ui = int(ui)
        except ValueError:
            print("Input type must be int")
            continue

        if ui not in range_:
            print("Input must be between {} and {}".format(start, stop))
            continue

        return ui


if __name__ == '__main__':
    # get input from user
    print("Enter a number to be factored:")
    P = sanitised_input("product", "P", range(2**6))

    # send problem to QPU
    print("Running on QPU")
    output = factor(P)

    # output results
    pprint(output)
