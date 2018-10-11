from __future__ import print_function

import dwavebinarycsp as dbc



def get_grid(n_rows, n_cols):
    positions = []  # Positions in the maze
    directions = []  # Edge nodes; the four directions of each position
    for i in range(n_rows):
        for j in range(n_cols):
            curr = str(i) + "," + str(j)
            positions.append(curr)
    return positions


def equal(a, b):
    return a == b


def sum_to_two_or_zero(*args):
    sum_value = sum(args)
    return sum_value in [0, 2]


def maze_bqm(n_rows, n_cols, start, end, walls):
    positions = get_grid(n_rows, n_cols)

    # Make constraints
    csp = dbc.ConstraintSatisfactionProblem(dbc.BINARY)

    # Constraint: Enforce North/South, East/West rule
    # (ie Row above's south is row below's north. Likewise with east and west)
    for i in range(0, n_rows - 1):
        for j in range(n_cols):
            above_node = str(i) + "," + str(j) + "s"
            below_node = str(i + 1) + "," + str(j) + "n"
            csp.add_constraint(equal, [above_node, below_node])

    for i in range(n_rows):
        for j in range(0, n_cols - 1):
            left_node = str(i) + "," + str(j) + "e"
            right_node = str(i) + "," + str(j + 1) + "w"
            csp.add_constraint(equal, [left_node, right_node])

    # Constraint: Each eNode's N,S,E,W must sum to zero or two
    for pos in positions:
        directions = {pos + "n", pos + "s", pos + "e", pos + "w"}
        csp.add_constraint(sum_to_two_or_zero, directions)

    # TODO: Have a way for user to easily set up walls, start and end
    # Constraint: Start and end locations
    csp.fix_variable(start, 1)  # start location
    csp.fix_variable(end, 1)  # end location

    # Constraint: No walking through boarders of the maze
    for j in range(n_cols):
        top_boarder = "0," + str(j) + "n"
        bottom_boarder = str(n_rows - 1) + "," + str(j) + "s"

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
        left_boarder = str(i) + ",0" + "w"
        right_boarder = str(i) + "," + str(n_cols - 1) + "e"

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
    return bqm



