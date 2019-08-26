from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import re

from maze import get_maze_bqm, Maze

# Create maze
n_rows = 2
n_cols = 2
start = '0,0n'
end = '1,0w'
walls = ['1,1n']

# Get BQM
m = Maze(n_rows, n_cols, start, end, walls)
bqm = m.get_bqm()

# Submit BQM to a D-Wave sampler
# Note: when grabbing the solution, we are only grabbing path segments that have
#   been "selected" (i.e. indicated with a 1).
# Note2: in order to get the BQM at the right energy levels, auxiliary variables
#   may have been included in the BQM. These auxiliary variables are no longer
#   useful once we have our result. Hence, we can just ignore them by filtering
#   them out with regex (i.e. re.match(r"^aux(\d+)$", k)])
sampler = EmbeddingComposite(DWaveSampler())
result = sampler.sample(bqm, num_reads=1000)
solution = [k for k, v in result.first.sample.items() if v==1
            and re.match(r"^aux(\d+)$", k)]

# Visualize maze solution
m.visualize(solution)
print("\n")
print(result)
