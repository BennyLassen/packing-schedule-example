# Examples

This folder contains example scripts demonstrating different use cases and scenarios for the packing schedule optimization model.

## Available Examples

### 1. Constrained Capacity Example
**File**: `constrained_capacity_example.py`

**Purpose**: Demonstrates trade-off analysis under tight resource constraints where not all deadlines can be met.

**Scenario**:
- 1 production line (no parallel processing)
- 1 worker (no concurrent labor)
- 5 orders with conflicting due dates
- 100% capacity utilization
- Priority-based scheduling

**Key Learning Points**:
- How the optimizer prioritizes when resources are limited
- Trade-offs between on-time delivery and other objectives
- Priority-weighted lateness minimization
- Realistic production planning constraints

**Expected Results**:
- 3 orders delivered on-time (60%)
- 2 orders delivered late (40%)
- High-priority orders scheduled earlier
- Visual timeline showing sequential processing

**Usage**:
```bash
python examples/constrained_capacity_example.py
```

**What to Try**:
- Modify priority weights to change scheduling decisions
- Adjust due dates to make the problem more/less constrained
- Add a second production line to improve on-time performance
- Change objective function weights to emphasize different goals

---

### 2. Setup Time and Batching Example
**File**: `setup_batching_example.py`

**Purpose**: Demonstrates how sequence-dependent setup times and product family batching affect production scheduling and efficiency.

**Scenario**:
- 1 production line (sequential processing)
- 1 worker (limited labor)
- 10 orders in 3 product families (A, B, C)
- Significant setup times between families (2 time units)
- Zero setup times within families (batching benefit)
- Due dates create tension between batching and urgency

**Key Learning Points**:
- How setup times affect scheduling decisions
- The value of batching similar orders together
- Trade-offs between setup reduction and on-time delivery
- Sequence-dependent setup time optimization
- Product family grouping strategies

**Expected Results**:
- All 10 orders delivered on-time (100%)
- Orders grouped by product family
- Setup time: 4 time units (perfect batching = 2 transitions)
- 100% batching efficiency (vs. 18 time units worst case)
- 14 time units saved through intelligent sequencing

**Usage**:
```bash
python examples/setup_batching_example.py
```

**What to Try**:
- **Increase setup times** to 4 units to see stronger batching incentive
- **Make all due dates tight** (e.g., all due by t=15) to see batching break down
- **Add more product families** (4-5 families) for complex sequencing
- **Reduce OTIF weight** (alpha=1.0) to favor batching over deadlines
- **Add a second line** to enable parallel family processing
- **Change family sizes** (e.g., 2 orders in A, 5 in B, 3 in C) for unbalanced batching

---

### 3. Line Selection Example
**File**: `line_selection_example.py`

**Purpose**: Demonstrates line selection optimization when multiple production lines are available with different processing characteristics.

**Scenario**:
- 2 production lines (different speeds per order)
- 1 worker (can only work one line at a time)
- 5 orders that CAN all complete on Line 1 alone
- Lines have different processing times for different orders
- Optimizer must choose between single-line vs. multi-line strategy

**Key Learning Points**:
- How the optimizer selects between available lines
- Impact of line utilization cost (delta weight) on strategy
- Trade-offs between using fewer lines vs. minimizing processing time
- Optimal line assignment based on processing time variations

**Expected Results**:
- All 5 orders delivered on-time (100%)
- 2 lines activated (with moderate delta weight)
- Each order assigned to its faster line
- 6 units of processing time saved through optimal line selection

**Usage**:
```bash
python examples/line_selection_example.py
```

**What to Try**:
- Set `delta=10.0` to force single-line strategy (higher line activation cost)
- Set `delta=0.1` to encourage multi-line usage (lower activation cost)
- Modify processing times to make one line clearly superior for all orders
- Add a second worker to enable true parallel processing on both lines
- Increase processing time differences to amplify line selection benefits

---

### 4. Parallel Processing Example
**File**: `parallel_processing_example.py`

**Purpose**: Demonstrates the capability for parallel processing with multiple workers, and how the optimizer balances parallel execution against other objectives.

**Scenario**:
- 2 production lines (different speeds per order)
- 2 workers (CAN work simultaneously on different lines)
- 5 orders with same data as line selection example
- Compares single-worker vs. multi-worker performance

**Key Learning Points**:
- How multiple workers enable potential parallel processing
- Trade-offs between parallel execution and other objectives (WIP, workforce variability)
- Worker load balancing and task distribution
- Speedup calculation from additional labor capacity
- Why the optimizer may choose sequential over parallel execution

**Expected Results**:
- All 5 orders delivered on-time (100%)
- Completion time: ~9 time units (vs ~17 with 1 worker sequential)
- Significant speedup (~1.9x) through parallel processing
- 4 time slots with simultaneous work on both lines
- Workers 1 and 2 operating different lines at the same time

**Important Understanding - Objective Function Trade-offs**:
The optimizer balances multiple objectives, not just completion time:
- **OTIF (On-Time In-Full)**: Meeting due dates
- **WIP (Work-In-Progress)**: Minimizing inventory and flow time
- **Workforce Variability**: Keeping workforce levels stable
- **Line Utilization**: Minimizing number of active lines

**When WIP and workforce penalties are HIGH**, the optimizer may prefer sequential execution even with multiple workers available, because parallel processing:
1. Increases WIP (more orders in process simultaneously)
2. Increases workforce variability (more workers active at once)

**When due dates are TIGHT and OTIF weight is HIGH**, the optimizer will parallelize to meet deadlines. This example demonstrates true parallel processing by:
1. Using tighter due dates that require parallelization (orders 1&2 both due at t=6)
2. Increasing OTIF weight (alpha=10.0) to prioritize meeting deadlines
3. Decreasing WIP/workforce weights (beta=0.05, gamma=0.05) to reduce parallelization penalty

This realistic behavior shows that optimization is about **trade-offs**, not just "max utilization."

**Usage**:
```bash
python examples/parallel_processing_example.py
```

**What to Try**:
- **Increase WIP/workforce weights** (beta=0.3, gamma=0.2) to see sequential execution return
- **Loosen due dates** (e.g., all due at t=20) to see if optimizer reverts to sequential
- **Add a third worker** to see 3-way parallelization
- **Make all processing times equal** to see perfect load balancing
- **Compare with line_selection_example.py** (1 worker) to see single-worker behavior
- **Experiment with objective weights** to understand the trade-off space

---

### 5. Configurable Scenario Example
**File**: `configurable_scenario_example.py`

**Purpose**: Provides an easily configurable template for creating custom scenarios by simply changing parameters at the top of the script.

**Scenario** (Default Configuration):
- 2 production lines
- 2 workers
- 10 orders
- 2-day planning horizon
- 30-minute time slots (96 time slots total)
- 3 product families with setup times
- Automatically generated realistic data

**Key Learning Points**:
- How to quickly prototype different scenarios
- Impact of problem size on solving time
- Automatic generation of realistic input parameters
- Easy experimentation with different scales
- Understanding trade-offs between problem size and computational requirements

**Configuration Options** (edit CONFIG dictionary in script):
```python
CONFIG = {
    'n_lines': 2,              # Number of production lines
    'n_workers': 2,            # Number of workers
    'n_orders': 10,            # Number of orders
    'n_days': 2,               # Planning horizon (days)
    'time_slot_minutes': 30,   # Time slot duration
    'n_product_families': 3,   # Product families for setup
    # ... and many more options!
}
```

**Expected Results**:
- Fast solving (<1 minute for default configuration)
- 100% on-time delivery (with sufficient capacity)
- Clear analysis of resource utilization
- Scalable to larger problems by changing configuration

**Usage**:
```bash
python examples/configurable_scenario_example.py
```

**What to Try**:
- **Small test** (2 lines, 2 workers, 10 orders, 2 days) - Default, very fast
- **Medium test** (5 lines, 5 workers, 50 orders, 3 days) - Moderate, 1-5 min
- **Large test** (10 lines, 10 workers, 200 orders, 5 days) - Longer, 5-20 min
- **Worker shortage** (5 lines, 2 workers, 30 orders) - Test constraints
- **Line shortage** (2 lines, 5 workers, 30 orders) - Test capacity limits
- **Change time slots** (15-min vs 60-min) - See granularity impact
- **Adjust objective weights** - Explore multi-objective trade-offs

**Recommended Experiment Workflow**:
1. Start with default configuration (fast solving)
2. Gradually increase problem size
3. Observe impact on solving time and solution quality
4. Find the sweet spot for your hardware and requirements
5. Use as template for your own scenarios

---

### 6. Large-Scale Weekly Production Example
**File**: `large_scale_weekly_production.py`

**Purpose**: Demonstrates the scalability of the optimization model for industrial-scale production scheduling with realistic weekly volumes.

**Scenario**:
- 48 production lines (large manufacturing facility)
- 48 workers (flexible assignment across all lines)
- 1700 orders to schedule (realistic weekly volume)
- 7-day planning horizon (168 hours)
- 15-minute time slots (672 time slots total)
- 10 product families with setup times
- Distributed due dates across the week

**Key Learning Points**:
- Model scalability to industrial-scale problems
- Resource allocation at scale (48 lines, 48 workers)
- Weekly production planning strategies
- Capacity utilization in high-volume operations
- Computational performance with large problem sizes
- Line and worker utilization patterns

**Expected Results**:
- Feasible schedule if capacity is sufficient
- High OTIF performance (target: >90%)
- Efficient line utilization across 48 lines
- Balanced worker assignments
- Solution time: 10-60 minutes depending on hardware

**Computational Considerations**:
- **Model size**: ~55 million assignment variables
- **Memory**: 16GB+ RAM recommended
- **Solving time**: 10-60+ minutes (with 30-min time limit and 2% gap tolerance)
- **Hardware**: Powerful CPU recommended for faster solving
- This is a **large-scale MILP problem** - be patient!

**Usage**:
```bash
python examples/large_scale_weekly_production.py
```

**What to Try**:
- **Reduce problem size** for testing: 1000 orders, 24 lines, 3-day horizon
- **Adjust time limits**: Increase to 60+ minutes for better solutions
- **Tune MIP gap**: Use 5% gap for faster solving, 0.5% for better quality
- **Modify capacity**: Change reserved_capacity to test different utilization levels
- **Test different order distributions**: Change urgent/standard/flexible ratios
- **Benchmark hardware**: Compare solving times on different machines

**Scaling Recommendations**:
- For problems >2000 orders, consider rolling horizon planning
- Use warm starts from previous week's solutions
- Consider decomposition by product family or time period
- Monitor memory usage - may need 32GB+ RAM for larger problems

---

## Running Examples

All examples can be run from the project root directory:

```bash
# From project root
cd c:\Projects\packing-schedule-example\packing-schedule-example

# Run the constrained capacity example (trade-offs under tight constraints)
python examples/constrained_capacity_example.py

# Run the setup and batching example (product family sequencing)
python examples/setup_batching_example.py

# Run the line selection example (1 worker, 2 lines)
python examples/line_selection_example.py

# Run the parallel processing example (2 workers, 2 lines)
python examples/parallel_processing_example.py

# Run the configurable scenario example (easily customizable)
python examples/configurable_scenario_example.py

# Run the large-scale weekly production example (48 lines, 48 workers, 1700 orders)
python examples/large_scale_weekly_production.py
```

**Notes**:
- The configurable example is the easiest to customize - just edit the CONFIG dictionary!
- The large-scale example may take 10-60 minutes to solve and requires significant computational resources (16GB+ RAM recommended).

## Example Output

Each example provides:
1. **Problem Setup**: Clear description of the scenario and constraints
2. **Model Statistics**: Number of variables and constraints
3. **Solution Summary**: Order assignments, OTIF metrics, resource utilization
4. **Detailed Analysis**: Order-by-order breakdown with timing and status
5. **Visual Timeline**: ASCII-based Gantt chart showing the schedule
6. **Key Insights**: Interpretation of results and learning points
7. **Suggestions**: Ideas for modifying the example to explore further

## Creating Your Own Examples

To create a new example:

1. Copy an existing example as a template
2. Modify the data creation function (e.g., `create_constrained_capacity_data()`)
3. Adjust problem dimensions, processing times, due dates, and priorities
4. Update the documentation at the top of the file
5. Add analysis functions as needed
6. Document the example in this README

### Example Template Structure

```python
"""
Example Title - Brief Description

SCENARIO SETUP:
- Describe the scenario
- List key constraints
- Explain what makes this interesting

EXPECTED BEHAVIOR:
- What should happen
- Key metrics to watch

This example is useful for:
- Use case 1
- Use case 2
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from packing_model import PackingScheduleModel

def create_example_data():
    """Create problem data."""
    # ... data creation ...
    return data

def analyze_results(model, data):
    """Analyze and explain results."""
    # ... custom analysis ...
    pass

def main():
    """Run the example."""
    # ... main execution flow ...
    pass

if __name__ == "__main__":
    main()
```

## Common Scenarios to Explore

Here are some interesting scenarios you could create examples for:

### Resource Constraints
- **Limited workers**: More orders than workers, forcing scheduling decisions
- **Limited lines**: Orders competing for production capacity
- **Worker unavailability**: Time windows where workers are unavailable
- **Line specialization**: Different lines have different processing times

### Temporal Constraints
- **Rush orders**: High-priority orders with very tight deadlines
- **Batching opportunities**: Orders that can be batched to save setup time
- **Setup time optimization**: Minimizing setup changes between orders
- **Time window constraints**: Orders that must start within specific windows

### Inventory Scenarios
- **Initial inventory**: Starting with partial inventory for some orders
- **Inventory carrying costs**: Trade-off between early production and inventory
- **Just-in-time**: Minimizing inventory by timing production close to shipping

### Multi-Objective Trade-offs
- **OTIF vs WIP**: Balancing on-time delivery with work-in-progress
- **Workforce stability**: Minimizing changes in workforce levels
- **Line utilization**: Balancing line usage across multiple lines
- **Cost minimization**: Emphasizing different cost components

### Realistic Production Scenarios
- **Product families**: Orders with similar characteristics that batch well
- **Sequence-dependent setups**: Setup times that depend on order sequence
- **Preventive maintenance**: Reserved capacity for maintenance windows
- **Demand uncertainty**: Multiple scenarios with different priorities

## Tips for Effective Examples

1. **Clear Documentation**: Explain the scenario and what makes it interesting
2. **Realistic Data**: Use plausible processing times, due dates, and priorities
3. **Visual Output**: Include timeline visualizations and formatted summaries
4. **Analysis**: Interpret the results and explain optimizer decisions
5. **Exploration**: Suggest modifications users can try
6. **Edge Cases**: Demonstrate both feasible and infeasible scenarios

## Need Help?

- Check the main [README.md](../README.md) for general usage
- See [ARCHITECTURE.md](../ARCHITECTURE.md) for code structure
- Review [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for common patterns
- Look at existing examples for implementation patterns
