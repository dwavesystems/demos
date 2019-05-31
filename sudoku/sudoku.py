import dimod
import math

from dimod.generators.constraints import combinations
from hybrid.reference import KerberosSampler


def get_label(row, col, digit):
    return "{row},{col}_{digit}".format(**locals())


def get_matrix(filename):
    try:
        with open(filename, "r") as f:
            content = f.readlines()
    except FileNotFoundError:
        raise

    lines = []
    for line in content:
        new_line = line.rstrip('\n').split(' ')
        new_line = list(map(int, new_line))
        lines.append(new_line)

    return lines


def is_correct(matrix):
    n = len(matrix)                 # number of rows; number of columns
    m = int(math.sqrt(n_rows))      # number of subsquare rows; number of subsquare columns
    solution = set(range(1, n+1))   # digits in a solution

    # Verifying rows
    for row in matrix:
        if set(row) != solution:
            return False

    # Verifying columns
    for j in range(n_rows):
        col = [matrix[i][j] for i in range(n)]
        if set(col) != solution:
            return False

    # Verifying subsquares
    subsquare_coords = [(i, j) for i in range(m) for j in range(m)]
    for r_scalar in range(m):
        for c_scalar in range(m):
            subsquare = [matrix[i + r_scalar * m][j + c_scalar * m] for i, j
                         in subsquare_coords]
            if set(subsquare) != solution:
                return False

    return True

#TODO: remove hardcoded loops
n_rows = 9
n_cols = 9
sudoku_filename = "problem.txt"
digits = range(1, 10)
# TODO: check that file exists

bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.SPIN)

# Constraint: Each node can only select one digit
for row in range(n_rows):
    for col in range(n_cols):
        node_digits = [get_label(row, col, digit) for digit in digits]
        one_digit_bqm = combinations(node_digits, 1)
        bqm.update(one_digit_bqm)

# Constraint: Each row of nodes cannot have duplicate digits
for row in range(n_rows):
    for digit in digits:
        row_nodes = [get_label(row, col, digit) for col in range(n_cols)]
        row_bqm = combinations(row_nodes, 1)
        bqm.update(row_bqm)

# Constraint: Each column of nodes cannot have duplicate digits
for col in range(n_cols):
    for digit in digits:
        col_nodes = [get_label(row, col, digit) for row in range(n_rows)]
        col_bqm = combinations(col_nodes, 1)
        bqm.update(col_bqm)

# Constraint: Each sub-square cannot have duplicates
# Build indices of a basic subsquare
base_array = [(row, col) for row in range(3) for col in range(3)]

# Build full sudoku array
for r_scalar in range(3):
    for c_scalar in range(3):
        for digit in digits:
            # Build the labels for a subsquare
            # Note: r_scalar*3 and c_scalar*3 are used to shift the subsquare
            subsquare = [get_label(row + r_scalar*3, col + c_scalar*3, digit)
                         for row, col in base_array]
            subsquare_bqm = combinations(subsquare, 1)
            bqm.update(subsquare_bqm)

# Constraint: Fix known values
matrix = get_matrix(sudoku_filename)

for row, line in enumerate(matrix):
    for col, value in enumerate(line):
        if value > 0:
            bqm.fix_variable(get_label(row, col, value), 1)

# Solve BQM
solution = KerberosSampler().sample(bqm, max_iter=10, convergence=3)
best_solution = solution.first.sample

# Print solution
solution_list = [k for k, v in best_solution.items() if v == 1]

for label in solution_list:
    coord, digit = label.split('_')
    row, col = map(int, coord.split(','))
    matrix[row][col] = int(digit)

for line in matrix:
    print(line)

# Verify
if is_correct(matrix):
    print("The solution is correct")
else:
    print("The solution is incorrect")

