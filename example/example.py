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


# Map colouring problem
bc = Region("bc")
ab = Region("ab")
ma = Region("ma")
csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

# One colour
for r in [bc, ab, ma]:
    csp.add_constraint(select_one, {r.red, r.green, r.blue, r.yellow})

# No colour sharing
for x, y in [(bc, ab), (ab, ma)]:
    csp.add_constraint(not_both, {x.red, y.red})
    csp.add_constraint(not_both, {x.green, y.green})
    csp.add_constraint(not_both, {x.blue, y.blue})
    csp.add_constraint(not_both, {x.yellow, y.yellow})

bqm = dwavebinarycsp.stitch(csp)

solution = KerberosSampler().sample(bqm, max_iter=10, convergence=3)
