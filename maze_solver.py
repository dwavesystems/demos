from __future__ import print_function

import dwavebinarycsp as dbc


def get_label(row, col, direction):
    return "".join([str(row), ",", str(col), direction])


def sum_to_two_or_zero(*args):
    sum_value = sum(args)
    return sum_value in [0, 2]


def maze_bqm(n_rows, n_cols, start, end, walls, verbose=False):
    # Make constraints
    csp = dbc.ConstraintSatisfactionProblem(dbc.BINARY)

    # Constraint: Each eNode's N,S,E,W must sum to zero or two
    for i in range(n_rows):
        for j in range(n_cols):
            directions = {get_label(i, j, 'n'), get_label(i, j, 'w'), get_label(i+1, j, 'n'), get_label(i, j+1, 'w')}
            csp.add_constraint(sum_to_two_or_zero, directions)

    # TODO: Have a way for user to easily set up walls, start and end
    # Constraint: Start and end locations
    csp.fix_variable(start, 1)  # start location
    csp.fix_variable(end, 1)  # end location

    # Constraint: No walking through boarders of the maze
    for j in range(n_cols):
        top_boarder = get_label(0, j, 'n')
        bottom_boarder = get_label(n_rows, j, 'n')

        try:
            csp.fix_variable(top_boarder, 0)
        except ValueError:
            if not top_boarder in [start, end]:
                raise ValueError

        try:
            csp.fix_variable(bottom_boarder, 0)
        except ValueError:
            if not bottom_boarder in [start, end]:
                raise ValueError

    for i in range(n_rows):
        left_boarder = get_label(i, 0, 'w')
        right_boarder = get_label(i, n_cols, 'w')

        try:
            csp.fix_variable(left_boarder, 0)
        except ValueError:
            if not left_boarder in [start, end]:
                raise ValueError

        try:
            csp.fix_variable(right_boarder, 0)
        except ValueError:
            if not right_boarder in [start, end]:
                raise ValueError

    # Constraint: Inner walls of the maze
    for wall in walls:
        csp.fix_variable(wall, 0)

    bqm = dbc.stitch(csp)

    if verbose:
        return bqm, csp

    return bqm



