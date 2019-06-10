import dwavebinarycsp
from hybrid.reference.kerberos import KerberosSampler

from utilities import visualize_map


class Province:
    def __init__(self, name):
        self.name = name
        self.red = name + "_r"
        self.green = name + "_g"
        self.blue = name + "_b"
        self.yellow = name + "_y"


# Set up provinces
bc = Province("bc")   # British Columbia
ab = Province("ab")   # Alberta
sk = Province("sk")   # Saskatchewan
mb = Province("mb")   # Manitoba
on = Province("on")   # Ontario
qc = Province("qc")   # Quebec
nl = Province("nl")   # Newfoundland and Labrador
nb = Province("nb")   # New Brunswick
pe = Province("pe")   # Prince Edward Island
ns = Province("ns")   # Nova Scotia
yt = Province("yt")   # Yukon
nt = Province("nt")   # Northwest Territories
nu = Province("nu")   # Nunavut

provinces = [bc, ab, sk, mb, on, qc, nl, nb, pe, ns, yt, nt, nu]

# Set up province neighbours (i.e. shares a border)
neighbours = [(bc, ab),
              (bc, nt),
              (bc, yt),
              (ab, sk),
              (ab, nt),
              (sk, mb),
              (sk, nu),
              (sk, nt),
              (mb, on),
              (mb, nu),
              (on, qc),
              (qc, nb),
              (qc, nl),
              (nb, ns),
              (yt, nt),
              (nt, nu)]

# Initialize constraint satisfaction problem
csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)
not_both = {(0, 1), (1, 0), (0, 0)}
select_one = {(0, 0, 0, 1),
              (0, 0, 1, 0),
              (0, 1, 0, 0),
              (1, 0, 0, 0)}

# Apply one colour constraint
for p in provinces:
    csp.add_constraint(select_one, {p.red, p.green, p.blue, p.yellow})

# Apply no colour sharing between neighbours
for x, y in neighbours:
    csp.add_constraint(not_both, {x.red, y.red})
    csp.add_constraint(not_both, {x.green, y.green})
    csp.add_constraint(not_both, {x.blue, y.blue})
    csp.add_constraint(not_both, {x.yellow, y.yellow})

# Combine constraints to form a BQM
bqm = dwavebinarycsp.stitch(csp)

# Solve BQM
solution = KerberosSampler().sample(bqm, max_iter=10, convergence=3)
best_solution = solution.first.sample
print("Solution: ", best_solution)

# Verify
is_correct = csp.check(best_solution)
print("Does solution satisfy our constraints? {}".format(is_correct))


# Visualize the solution
# Note: The following is purely for visualizing the output and is not necessary
# for the demo.

# Hard code node positions to be reminiscent of the map of Canada
node_positions = {"bc": (0, 1),
                  "ab": (2, 1),
                  "sk": (4, 1),
                  "mb": (6, 1),
                  "on": (8, 1),
                  "qc": (10, 1),
                  "nb": (10, 0),
                  "ns": (12, 0),
                  "pe": (12, 1),
                  "nl": (12, 2),
                  "yt": (0, 3),
                  "nt": (2, 3),
                  "nu": (6, 3)}

nodes = [u.name for u in provinces]
edges = [(u.name, v.name) for u, v in neighbours]
visualize_map(nodes, edges, best_solution, node_positions=node_positions)

