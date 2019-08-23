from maze import get_maze_bqm
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

# Create maze
n_rows = 2
n_cols = 2
start = '0,0n'
end = '1,0w'
walls = ['1,1n']

# Get BQM
bqm = get_maze_bqm(n_rows, n_cols, start, end, walls)

# Submit BQM to a D-Wave sampler
sampler = EmbeddingComposite(DWaveSampler())
result = sampler.sample(bqm, num_reads=1000)
print(result)
