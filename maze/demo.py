from maze import get_maze_bqm, Maze
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

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
sampler = EmbeddingComposite(DWaveSampler())
result = sampler.sample(bqm, num_reads=1000)
solution = [k for k, v in result.first.sample.items() if v==1]

# Visualize maze solution
m.visualize(solution)
print(result)
