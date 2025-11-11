# Quick Start Guide - Problem 4.1 c2

## Installation

```bash
# Install required packages
pip install pyomo numpy highspy
```

## Run the Example

```bash
# Navigate to the simple_model directory
cd simple_model

# Run the example
python problem_4_1_c2_example.py
```

## Minimal Example

```python
import numpy as np
from packing_model_problem_4_1_c2 import PackingScheduleModelProblem4_1_c2

# Define problem data
data = {
    # Dimensions
    'n_unique_types': 2,      # 2 product types
    'n_orders': 4,            # 4 production orders
    'n_demands': 2,           # 2 shipping demands
    'n_lines': 2,             # 2 production lines
    'T_max': 50.0,            # Planning horizon: 50 time units

    # Processing times [types × lines]
    'processing_time': np.array([
        [10.0, 12.0],  # Type 1: 10 on line 1, 12 on line 2
        [15.0, 13.0]   # Type 2: 15 on line 1, 13 on line 2
    ]),

    # Setup times [types × types]
    'setup_time': np.array([
        [0.0, 5.0],    # From type 1: no setup to 1, 5 to type 2
        [5.0, 0.0]     # From type 2: 5 to type 1, no setup to 2
    ]),

    # Initial inventory [types] - starting stock for each product type
    'initial_inventory': np.array([1, 0]),  # Type 1 has 1 unit in stock, Type 2 has 0

    # Order specifications
    'order_type': np.array([1, 1, 2, 2]),  # Orders 1,2 are type 1; 3,4 are type 2
    'priority': np.array([10, 10, 15, 15]),  # Priority weights

    # Demand specifications
    'due_date': np.array([25.0, 45.0]),      # Due dates
    'demand_type': np.array([1, 2]),          # Demand 1 for type 1, demand 2 for type 2
    'demand_qty': np.array([2, 2]),           # Quantities needed

    # Objective weights
    'objective_weights': {
        'beta': 1.0,    # WIP weight
        'gamma': 2.0,   # Workforce variability weight
        'delta': 0.5    # Underutilization weight
    }
}

# Create model
model = PackingScheduleModelProblem4_1_c2(data)

# Solve
results = model.solve(solver_name='appsi_highs', time_limit=60)

# Print results
print(f"Status: {results['status']}")
print(f"Objective: {results['objective_value']}")

if results['objective_value'] is not None:
    model.print_solution_summary()

    # Get detailed solution
    solution = model.get_solution()

    # Access specific results
    print("\nOrder Assignments:")
    for assignment in solution['assignments']:
        print(f"  Order {assignment['order']}: "
              f"Line {assignment['line']}, "
              f"Start {assignment['start']:.1f}, "
              f"Complete {assignment['completion']:.1f}")
```

## Data Structure Reference

### Required Keys

```python
data = {
    # Problem dimensions
    'n_unique_types': int,    # Number of product types (U)
    'n_orders': int,          # Number of production orders (I)
    'n_demands': int,         # Number of demands (D)
    'n_lines': int,           # Number of production lines (J)
    'T_max': float,           # Planning horizon

    # Processing parameters
    'processing_time': np.array(shape=[U, J]),  # p(u,j)
    'setup_time': np.array(shape=[U, U]),       # s(u,v)
    'initial_inventory': np.array(shape=[U]),   # inv0(u)

    # Order data
    'order_type': np.array(shape=[I]),     # type(i) - 1-indexed type
    'priority': np.array(shape=[I]),       # priority(i)

    # Demand data
    'due_date': np.array(shape=[D]),       # due(d)
    'demand_type': np.array(shape=[D]),    # prodtype(d) - 1-indexed type
    'demand_qty': np.array(shape=[D]),     # qty(d)

    # Objective weights (optional)
    'objective_weights': {
        'beta': float,    # WIP weight (default: 1.0)
        'gamma': float,   # Workforce weight (default: 1.0)
        'delta': float    # Underutilization weight (default: 0.0)
    }
}
```

### Array Shapes Summary

| Array | Shape | Description |
|-------|-------|-------------|
| `processing_time` | [U × J] | Processing time by type and line |
| `setup_time` | [U × U] | Setup between types |
| `initial_inventory` | [U] | Starting inventory per type |
| `order_type` | [I] | Type of each order |
| `priority` | [I] | Priority of each order |
| `due_date` | [D] | Due date of each demand |
| `demand_type` | [D] | Type of each demand |
| `demand_qty` | [D] | Quantity of each demand |

## Common Solver Options

### HiGHS (Free, Default)
```python
results = model.solve(
    solver_name='appsi_highs',
    tee=True,              # Show solver output
    time_limit=300,        # 5 minutes
    mip_rel_gap=0.01       # 1% optimality gap
)
```

### Gurobi (Commercial)
```python
results = model.solve(
    solver_name='gurobi',
    tee=True,
    time_limit=300,
    mip_rel_gap=0.01
)
```

## Solution Access

```python
# Get solution dictionary
solution = model.get_solution()

# Access components
assignments = solution['assignments']        # Order schedule
demands = solution['demands']                # Demand fulfillment
inventory = solution['inventory']            # Inventory levels
workforce = solution['workforce_summary']    # Worker statistics
events = solution['event_times']             # Event times

# Example: Find when order 3 starts
for assignment in assignments:
    if assignment['order'] == 3:
        print(f"Order 3 starts at time {assignment['start']}")
```

## Troubleshooting

### Problem is Infeasible
1. Check if T_max is large enough
2. Verify initial inventory + production can meet demands
3. Ensure due dates are achievable given processing times

### Solver is Slow
1. Reduce problem size (fewer orders/demands)
2. Increase MIP gap tolerance
3. Set a time limit
4. Consider using commercial solver

### Import Errors
```bash
# If import fails, ensure you're in the correct directory
cd simple_model
python -c "from packing_model_problem_4_1_c2 import PackingScheduleModelProblem4_1_c2; print('Success!')"
```

## Next Steps

- Read [README_PROBLEM_4_1_c2.md](README_PROBLEM_4_1_c2.md) for detailed documentation
- See [IMPLEMENTATION_SUMMARY_4_1_c2.md](IMPLEMENTATION_SUMMARY_4_1_c2.md) for implementation details
- Modify [problem_4_1_c2_example.py](problem_4_1_c2_example.py) for your use case

## File Locations

```
simple_model/
├── packing_model_problem_4_1_c2/       # Model implementation
│   ├── model.py                         # Main model class
│   ├── parameters.py                    # Parameter definitions
│   ├── variables.py                     # Variable definitions
│   ├── objective.py                     # Objective function
│   └── constraints/                     # Constraint modules
├── problem_4_1_c2_example.py           # Runnable example (start here!)
├── README_PROBLEM_4_1_c2.md            # Full documentation
├── IMPLEMENTATION_SUMMARY_4_1_c2.md    # Implementation details
└── QUICK_START_PROBLEM_4_1_c2.md       # This file
```
