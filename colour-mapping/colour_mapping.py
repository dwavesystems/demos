import dwavebinarycsp
from hybrid.reference.kerberos import KerberosSampler


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
print(best_solution)

# Verify
is_correct = csp.check(best_solution)
print("Does solution satisfy our constraints? {}".format(is_correct))


# Visualize
# Note: the following code is not necessary for the demo. It is purely for
#   visualizing the output
import networkx as nx
import matplotlib.pyplot as plt

# Set up graph
edges = [(u.name, v.name) for (u, v) in neighbours]
G = nx.Graph(edges)
G.add_node(pe.name)

# Colour nodes
node_colours = [k for k, v in best_solution.items() if v == 1]
for label in node_colours:
    name, colour = label.split("_")
    G.nodes[name]["colour"] = colour

# Get colour in same order as nodes
colour_map = [colour for name, colour in G.nodes(data="colour")]
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
nx.draw_networkx(G, pos=node_positions, with_labels=True, node_color=colour_map,
                 font_color="w", node_size=400)
plt.savefig("province_graph.png")
