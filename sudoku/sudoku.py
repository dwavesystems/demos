from dimod.generators.constraints import combinations
import dimod


def get_label(row, col, digit):
    return "{row},{col}_{digit}".format(**locals())


n_rows = 9
n_cols = 9
digits = range(1, 10)

bqm = dimod.BinaryQuadraticModel()

# Each node can only select one value
for row in range(n_rows):
    for col in range(n_cols):
        node_digits = [get_label(row, col, digit) for digit in digits]
        one_digit_bqm = combinations(len(digits), 1, node_digits)
        bqm.update(one_digit_bqm)

# Each row cannot have duplicate values
for row in range(n_rows):
    for digit in digits:
        row_nodes = [get_label(row, col, digit) for col in range(1, n_cols+1)]

        # For each digit, only select one column in that row
        row_bqm = combinations(n_cols, 1, row_nodes)
        bqm.update(row_bqm)

# Each column cannot have duplicate values
for col in range(n_cols):
    for digit in digits:
        col_nodes = [get_label(row, col, digit) for row in range(1, n_rows+1)]
        col_bqm = combinations(n_rows, 1, col_nodes)
        bqm.update(col_bqm)
