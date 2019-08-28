# Copyright 2019 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import re

from maze import get_maze_bqm, Maze

# Create maze
n_rows = 3
n_cols = 4
start = '0,0n'              # maze entrance location
end = '2,4w'                # maze exit location
walls = ['1,1n', '2,2w']    # maze interior wall locations

# Construct BQM
m = Maze(n_rows, n_cols, start, end, walls)
bqm = m.get_bqm()

# Submit BQM to a D-Wave sampler
# Note: occasionally, multiple qubits are used to represent a single variable
#   (e.g. using multiple qubits to represent a single path segment in a maze).
#   The reason for this representation has to do with the way the quantum
#   computing hardware is structured. In order to get this set of qubits
#   - known as a chain - to each produce same result for the single variable,
#   we add weights to them such that this behaviour is becomes more likely.
#   Below, we have slightly increased the default chain strength in order to
#   help maintain the chain during sampling.
sampler = EmbeddingComposite(DWaveSampler())
result = sampler.sample(bqm, num_reads=1000, chain_strength=2)

# Interpret result
# Note: when grabbing the path, we are only grabbing path segments that have
#   been "selected" (i.e. indicated with a 1).
# Note2: in order construct the BQM such that the maze solution corresponds to
#   the ground energy, auxiliary variables
#   may have been included in the BQM. These auxiliary variables are no longer
#   useful once we have our result. Hence, we can just ignore them by filtering
#   them out with regex (i.e. re.match(r"^aux(\d+)$", k)])
path = [k for k, v in result.first.sample.items() if v==1
            and not re.match(r"^aux(\d+)$", k)]

# Visualize maze path
m.visualize(path)
print("\n")
print(result.first.sample)
