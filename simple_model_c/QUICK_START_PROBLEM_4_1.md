# Problem 4.1 - Quick Start Guide

## Installation

```bash
# Install dependencies
pip install pyomo numpy highspy

# Navigate to simple_model directory
cd simple_model
```

## Run Example (3 orders, 2 lines)

```bash
python problem_4_1_example.py
```

## Run Tests

```bash
python test_problem_4_1.py
```

## Basic Usage

```python
from packing_model_problem_4_1 import PackingScheduleModelProblem41
import numpy as np

# Minimal example data
data = {
    'n_orders': 2,
    'n_lines': 1,
    'n_timeslots': 10,
    'n_workers': 2,
    'processing_time': np.array([[3], [2]]),
    'initial_inventory': np.array([0, 0]),
    'reserved_capacity': 0.1,
    'due_date': np.array([5, 8]),
    'priority': np.array([1, 1]),
    'objective_weights': {'beta': 1.0, 'gamma': 0.5, 'delta': 0.3}
}

# Solve
model = PackingScheduleModelProblem41(data)
results = model.solve()

# View results
if results['objective_value']:
    model.print_solution_summary()
```

## Key Files

- **[README_PROBLEM_4_1.md](README_PROBLEM_4_1.md)**: Full documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**: Implementation details
- **[problem_4_1_example.py](problem_4_1_example.py)**: Working example
- **[test_problem_4_1.py](test_problem_4_1.py)**: Test suite

## Problem Formulation

Based on Problem_4_1.pdf with:
- Assignment: `x(i,j,t)` - order i starts on line j at time t
- Production: `prod(i,t)` - units produced
- Workforce: `workersused(t)`, `workersmax`, `workersmin`
- Inventory: `inv(i,t)`, `ship(i,t)`
- Objective: Minimize WIP + workforce variability + unutilized capacity

## Solver Options

```python
# HiGHS (free, recommended)
results = model.solve(solver_name='appsi_highs', tee=True, time_limit=300)

# GLPK (free)
results = model.solve(solver_name='glpk', tee=True)

# Gurobi (commercial, faster)
results = model.solve(solver_name='gurobi', tee=True, mip_rel_gap=0.01)
```

## Directory Structure

```
simple_model/
├── packing_model_problem_4_1/    # Implementation package
│   ├── model.py                  # Main model class
│   ├── parameters.py             # Parameters/sets
│   ├── variables.py              # Decision variables
│   ├── objective.py              # Objective function
│   └── constraints/              # Constraint modules
├── problem_4_1_example.py        # Example script
├── test_problem_4_1.py           # Test script
└── README_PROBLEM_4_1.md         # Full documentation
```

## Troubleshooting

**Model is infeasible?**
- Increase `n_timeslots`
- Reduce `reserved_capacity`
- Check due dates are achievable

**Too slow?**
- Reduce problem size
- Increase `mip_rel_gap` (e.g., 0.05)
- Use commercial solver (Gurobi/CPLEX)

**Import errors?**
- Ensure you're in `simple_model` directory
- Check dependencies installed: `pip list | grep -E "pyomo|numpy"`

## Next Steps

1. Review [README_PROBLEM_4_1.md](README_PROBLEM_4_1.md) for detailed documentation
2. Modify [problem_4_1_example.py](problem_4_1_example.py) for your data
3. Compare with `packing_model_simple` for advanced features
