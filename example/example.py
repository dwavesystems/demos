import dwavebinarycsp
from hybrid.reference.kerberos import KerberosSampler

not_both = {(0, 1), (1, 0), (0, 0)}
select_one = {(0, 0, 0, 1),
              (0, 0, 1, 0),
              (0, 1, 0, 0),
              (1, 0, 0, 0)}


class Region:
    def __init__(self, name):
        self.red = name + "_r"
        self.green = name + "_g"
        self.blue = name + "_b"
        self.yellow = name + "_y"


# Set up provinces and neighbours
bc = Region("bc")   # British Columbia
ab = Region("ab")   # Alberta
sk = Region("sk")   # Saskatchewan
mb = Region("mb")   # Manitoba
on = Region("on")   # Ontario
qc = Region("qc")   # Quebec
nl = Region("nl")   # Newfoundland and Labrador
nb = Region("nb")   # New Brunswick
pe = Region("pe")   # Prince Edward Island
ns = Region("ns")   # Nova Scotia
yt = Region("yt")   # Yukon
nt = Region("nt")   # Northwest Territories
nu = Region("nu")   # Nunavut

provinces = [bc, ab, sk, mb, on, qc, nl, nb, pe, ns, yt, nt, nu]

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

# Set up constraint
csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

# Apply one colour
for p in provinces:
    csp.add_constraint(select_one, {p.red, p.green, p.blue, p.yellow})

# Apply no colour sharing between neighbours
for x, y in neighbours:
    csp.add_constraint(not_both, {x.red, y.red})
    csp.add_constraint(not_both, {x.green, y.green})
    csp.add_constraint(not_both, {x.blue, y.blue})
    csp.add_constraint(not_both, {x.yellow, y.yellow})

bqm = dwavebinarycsp.stitch(csp)

solution = KerberosSampler().sample(bqm, max_iter=10, convergence=3)
best_solution = solution.first.sample
print(best_solution)

# Verify
is_correct = csp.check(best_solution)
print("Does solution satisfy our constraints? {}".format(is_correct))
