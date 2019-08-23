# Copyright 2019 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import dwavebinarycsp
import re


def get_maze_bqm(n_rows, n_cols, start, end, walls, penalty_per_tile=0.5):
    """Returns a BQM that corresponds to a valid path through a maze. This maze is described by the parameters.

    Specifically, it uses the parameters to build a maze constraint satisfaction problem (CSP). This maze CSP is then
    converted into the returned BQM.

    Note: If penalty_per_tile is too large, the path will be too heavily penalized and the optimal solution might
    produce no path at all.

    Args:
        n_rows: Integer. The number of rows in the maze.
        n_cols: Integer. The number of cols in the maze.
        start: String. The location of the starting point of the maze. String follows the format of get_label(..).
        end: String. The location of the end point of the maze. String follows the format of get_label(..).
        walls: List of Strings. The list of inner wall locations. Locations follow the format of get_label(..).
        penalty_per_tile: A number. Penalty for each tile that is included in the path; encourages shorter paths.

    Returns:
        A dimod.BinaryQuadraticModel
    """
    maze = Maze(n_rows, n_cols, start, end, walls)
    return maze.get_bqm(penalty_per_tile)


def get_label(row, col, direction):
    """Provides a string that follows a standard format for naming constraint variables in Maze.
    Namely, "<row_index>,<column_index><north_or_west_direction>".

    Args:
        row: Integer. Index of the row.
        col: Integer. Index of the column.
        direction: String in the set {'n', 'w'}. 'n' indicates north and 'w' indicates west.
    """
    return "{row},{col}{direction}".format(**locals())


def assert_label_format_valid(label):
    """Checks that label conforms with the standard format for naming constraint variables in Maze.
    Namely, "<row_index>,<column_index><north_or_west_direction>".

    Args:
        label: String.
    """
    is_valid = bool(re.match(r'^(\d+),(\d+)[nw]$', label))
    assert is_valid, ("{label} is in the incorrect format. Format is <row_index>,<column_index><north_or_west>. "
                      "Example: '4,3w'").format(**locals())


def sum_to_two_or_zero(*args):
    """Checks to see if the args sum to either 0 or 2.
    """
    sum_value = sum(args)
    return sum_value in [0, 2]


class Maze:
    """An object that stores all the attributes necessary to represent a maze as a constraint satisfaction problem.

    Args:
        n_rows: Integer. The number of rows in the maze.
        n_cols: Integer. The number of cols in the maze.
        start: String. The location of the starting point of the maze. String follows the format of get_label(..).
        end: String. The location of the end point of the maze. String follows the format of get_label(..).
        walls: List of Strings. The list of inner wall locations. Locations follow the format of get_label(..).
    """
    def __init__(self, n_rows, n_cols, start, end, walls):
        assert isinstance(n_rows, int) and n_rows > 0, "'n_rows' is not a positive integer".format(n_rows)
        assert isinstance(n_cols, int) and n_cols > 0, "'n_cols' is not a positive integer".format(n_cols)
        assert start != end, "'start' cannot be the same as 'end'"

        # Check label format
        assert_label_format_valid(start)
        assert_label_format_valid(end)

        for wall in walls:
            assert_label_format_valid(wall)

        # Instantiate
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.start = start
        self.end = end
        self.walls = walls
        self.csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

    def _apply_valid_move_constraint(self):
        """Applies a sum to either 0 or 2 constraint on each tile of the maze.

        Note: This constraint ensures that a tile is either not entered at all (0), or is entered and exited (2).
        """
        # Grab the four directions of each maze tile and apply two-or-zero constraint
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                directions = {get_label(i, j, 'n'), get_label(i, j, 'w'), get_label(i+1, j, 'n'),
                              get_label(i, j+1, 'w')}
                self.csp.add_constraint(sum_to_two_or_zero, directions)

    def _set_start_and_end(self):
        """Sets the values of the start and end locations of the maze.
        """
        self.csp.fix_variable(self.start, 1)  # start location
        self.csp.fix_variable(self.end, 1)  # end location

    def _set_borders(self):
        """Sets the values of the outer border of the maze; prevents a path from forming over the border.
        """
        for j in range(self.n_cols):
            top_border = get_label(0, j, 'n')
            bottom_border = get_label(self.n_rows, j, 'n')

            try:
                self.csp.fix_variable(top_border, 0)
            except ValueError:
                if not top_border in [self.start, self.end]:
                    raise ValueError

            try:
                self.csp.fix_variable(bottom_border, 0)
            except ValueError:
                if not bottom_border in [self.start, self.end]:
                    raise ValueError

        for i in range(self.n_rows):
            left_border = get_label(i, 0, 'w')
            right_border = get_label(i, self.n_cols, 'w')

            try:
                self.csp.fix_variable(left_border, 0)
            except ValueError:
                if not left_border in [self.start, self.end]:
                    raise ValueError

            try:
                self.csp.fix_variable(right_border, 0)
            except ValueError:
                if not right_border in [self.start, self.end]:
                    raise ValueError

    def _set_inner_walls(self):
        """Sets the values of the inner walls of the maze; prevents a path from forming over an inner wall.
        """
        for wall in self.walls:
            self.csp.fix_variable(wall, 0)

    def get_bqm(self, penalty_per_tile=0.5):
        """Applies the constraints necessary to form a maze and returns a BQM that would correspond to a valid path
        through said maze.

        Note: If penalty_per_tile is too large, the path will be too heavily penalized and the optimal solution might
          no path at all.

        Args:
            penalty_per_tile: A number. Penalty for each tile that is included in the path; encourages shorter paths.

        Returns:
            A dimod.BinaryQuadraticModel
        """
        # Apply constraints onto self.csp
        self._apply_valid_move_constraint()
        self._set_start_and_end()
        self._set_borders()
        self._set_inner_walls()

        # Grab bqm constrained for valid solutions
        bqm = dwavebinarycsp.stitch(self.csp)

        # Edit bqm to favour optimal solutions
        for v in bqm.variables:
            # Ignore auxiliary variables
            if isinstance(v, str) and re.match(r'aux\d+$', v):
                continue

            # Add a penalty to every tile of the path
            bqm.add_variable(v, penalty_per_tile, dwavebinarycsp.BINARY)

        return bqm

    def visualize(self, solution=None):
        def get_visual_coords(coords):
            coord_pattern = "(\d+),(\d+)([nw])"
            row, col, dir = re.findall(coord_pattern, coords)[0]
            new_row, new_col = map(lambda x: int(x) * 2 + 1, [row, col])
            new_row, new_col = (new_row-1, new_col) if dir == "n" else (new_row, new_col-1)

            return new_row, new_col

        # Check parameters
        if solution is None:
            solution = []

        # Construct empty maze visual
        width = 2*self.n_cols + 1       # maze visual's width
        height = 2*self.n_rows + 1      # maze visual's height
        empty_row = [" "] * (width-2)
        empty_row = ["#"] + empty_row + ["#"]   # add left and right borders

        visual = [list(empty_row) for _ in range(height)]
        visual[0] = ["#"] * width      # top border
        visual[-1] = ["#"] * width     # bottom border

        # Add possible locations in maze visual
        for position_row in visual[1::2]:
            position_row[1::2] = ["."]*(self.n_cols - 1) + ["."]

        # Add maze start and end to visual
        start_row, start_col = get_visual_coords(self.start)
        end_row, end_col = get_visual_coords(self.end)
        visual[start_row][start_col] = "s"
        visual[end_row][end_col] = "e"

        # Add interior walls to visual
        for w in self.walls:
            row, col = get_visual_coords(w)
            visual[row][col] = "#"

        # Add solution path to visual
        for s in solution:
            row, col = get_visual_coords(s)
            visual[row][col] = "*"

        # Print solution
        for s in visual:
            print("".join(s))
