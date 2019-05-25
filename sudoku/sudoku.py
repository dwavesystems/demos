import dimod
from dimod.generators.constraints import combinations
from hybrid.reference import KerberosSampler


def get_label(row, col, digit):
    return "{row},{col}_{digit}".format(**locals())


n_rows = 9
n_cols = 9
digits = range(1, 10)

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
        row_nodes = [get_label(row, col, digit) for col in range(1, n_cols+1)]
        row_bqm = combinations(row_nodes, 1)
        bqm.update(row_bqm)

# Constraint: Each column of nodes cannot have duplicate digits
for col in range(n_cols):
    for digit in digits:
        col_nodes = [get_label(row, col, digit) for row in range(1, n_rows+1)]
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

# Fix values

# Solve BQM
solution = KerberosSampler().sample(bqm, max_iter=30, convergence=3)
best_solution = solution.first.sample

# Print solution
solution_list = [k for k, v in best_solution.items() if v==1]
solution_list.sort()

for x in range(9):
    start = x*9
    line = solution_list[start:start+9]
    processed_line = []
    for item in line:
        processed_line.append(item.split("_")[1])

    print(processed_line)


# Verify
#is_correct = csp.check(best_solution)
#print("Does solution satisfy our constraints? {}".format(is_correct))

