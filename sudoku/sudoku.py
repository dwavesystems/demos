from dimod.generators.constraints import combinations
import dimod


def get_label(row, col, digit):
    return "{row},{col}_{digit}".format(**locals())


n_rows = 9
n_cols = 9
digits = range(1, 10)

bqm = dimod.BinaryQuadraticModel()

# Constraint: Each node can only select one digit
for row in range(n_rows):
    for col in range(n_cols):
        node_digits = [get_label(row, col, digit) for digit in digits]
        one_digit_bqm = combinations(len(digits), 1, node_digits)
        bqm.update(one_digit_bqm)

# Constraint: Each row of nodes cannot have duplicate digits
for row in range(n_rows):
    for digit in digits:
        row_nodes = [get_label(row, col, digit) for col in range(1, n_cols+1)]
        row_bqm = combinations(n_cols, 1, row_nodes)
        bqm.update(row_bqm)

# Constraint: Each column of nodes cannot have duplicate digits
for col in range(n_cols):
    for digit in digits:
        col_nodes = [get_label(row, col, digit) for row in range(1, n_rows+1)]
        col_bqm = combinations(n_rows, 1, col_nodes)
        bqm.update(col_bqm)

# Constraint: Each sub-square cannot have duplicates
# Build sub-square
base_array = [(row, col) for row in range(3) for col in range(3)]

# Build full sudoku array
for r_scalar in range(3):
    for c_scalar in range(3):
        for digit in digits:
            subsquare = [get_label(row + r_scalar*3, col + c_scalar*3, digit)
                         for row, col in base_array]
            subsquare_bqm = combinations(len(digits), 1, subsquare)
            bqm.update(subsquare_bqm)

# Fix values

# Solve BQM
#solution = KerberosSampler().sample(bqm, max_iter=10, convergence=3)
#best_solution = solution.first.sample
#print(best_solution)
#
## Verify
#is_correct = csp.check(best_solution)
#print("Does solution satisfy our constraints? {}".format(is_correct))

