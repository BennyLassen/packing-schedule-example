# Problem 4.1 Implementation

This directory contains a complete implementation of the MILP packing schedule optimization problem as specified in `Problem_4_1.pdf`.

## Directory Structure

```
simple_model/
├── packing_model_problem_4_1/     # Main package
│   ├── __init__.py                # Package initialization
│   ├── model.py                   # Main model class
│   ├── parameters.py              # Parameter and set definitions
│   ├── variables.py               # Decision variable definitions
│   ├── objective.py               # Objective function
│   └── constraints/               # Constraint modules
│       ├── __init__.py
│       ├── assignment.py          # One assignment constraint
│       ├── capacity.py            # Line capacity constraints
│       ├── shipping.py            # Shipping constraints
│       ├── otif.py                # OTIF constraints (placeholder)
│       ├── wip.py                 # WIP/inventory constraints
│       └── workforce.py           # Workforce tracking constraints
├── problem_4_1_example.py         # Example usage script
├── test_problem_4_1.py            # Test suite
└── README_PROBLEM_4_1.md          # This file
```

## Problem Formulation

Based on `Problem_4_1.pdf`, the model includes:

### Indices
- `i = 1..n`: Packing orders
- `j = 1..m`: Line numbers
- `t = 1..T`: Time slots (base interval ΔT, e.g., 15 minutes)

### Decision Variables
- `x(i,j,t)`: Binary - packing order i starts on line j at time t
- `prod(i,t)`: Positive integer - number of units produced at time t
- `workersused(t)`: Integer [0,W] - total workers working at time t
- `workersmax`: Integer [0,W] - maximal workers used in any time slot
- `workersmin`: Integer [0,W] - minimum workers used in any time slot
- `inv(i,t)`: Positive integer - number of packing order i in stock
- `ship(i,t)`: Binary - packing order i is shipped at time t

### Input Parameters
- `p(i,j)`: Processing time for order i on line j
- `inv0(i)`: Initial inventory stock for order i
- `due(i)`: Due date for order i
- `priority(i)`: Priority weight for order i
- `alpha`: Reserved capacity fraction

### Constraints
1. **One Assignment**: Each order assigned to exactly one line, one time
   ```
   ∑_j ∑_t x(i,j,t) = 1  ∀i
   ```

2. **Line Capacity**: No overlap of orders on the same line
   ```
   ∑_i ∑_{t≤τ<t+p(i,j)} x(i,j,t) ≤ 1  ∀j, ∀τ
   ```

3. **Reserved Capacity**: Keep alpha fraction reserved
   ```
   ∑_i ∑_j ∑_τ ∑_{t≤τ<t+p(i,j)} x(i,j,t) ≤ (1-α) * m * T
   ```

4. **Ship Exactly Once**: Each order ships exactly once
   ```
   ∑_t ship(i,t) = 1  ∀i
   ```

5. **Ship After Due**: Ship no earlier than due time
   ```
   ship(i) ≥ due(i)
   ```

6. **Production Tracking**: Production at completion time
   ```
   prod(i,t) = ∑_j x(i, j, t - p(i,j))
   ```

7. **Inventory Balance**: Standard inventory flow equation
   ```
   inv(i,t) = inv(i,t-1) + prod(i,t) - ship(i,t)  ∀i, ∀t > 0
   inv(i,0) = inv0(i)  ∀i
   ```

8. **Workforce Tracking**: Count active workers
   ```
   workersused(τ) = ∑_i ∑_j ∑_{t≤τ<t+p(i,j)} x(i,j,t)  ∀τ
   workersmax ≥ workersused(t)  ∀t
   workersused(t) ≥ workersmin  ∀t
   workforce_range = workersmax - workersmin
   ```

### Objective Function
Minimization objective (3-term):
```
f = β * wip_obj + γ * workforce + δ * total_not_utilized
```

Where:
- `wip_obj = ∑_t inv(t)`: Total inventory across time
- `workforce = workersrange`: Workforce variability (max - min)
- `total_not_utilized`: Unused capacity (interpreted as unused worker capacity)

## Usage

### Basic Example

```python
import numpy as np
from packing_model_problem_4_1 import PackingScheduleModelProblem41

# Define problem data
data = {
    'n_orders': 3,
    'n_lines': 2,
    'n_timeslots': 20,
    'n_workers': 5,
    'processing_time': np.array([[4, 5], [3, 4], [5, 3]]),
    'initial_inventory': np.array([0, 0, 0]),
    'reserved_capacity': 0.1,
    'due_date': np.array([10, 12, 15]),
    'priority': np.array([1, 1, 1]),
    'objective_weights': {
        'beta': 1.0,    # WIP weight
        'gamma': 0.5,   # Workforce weight
        'delta': 0.3    # Unutilized weight
    }
}

# Create and solve model
model = PackingScheduleModelProblem41(data)
results = model.solve(solver_name='appsi_highs', tee=True)

# Print solution
if results['objective_value'] is not None:
    model.print_solution_summary()
    solution = model.get_solution()
```

### Running the Example

```bash
cd simple_model
python problem_4_1_example.py
```

### Running Tests

```bash
cd simple_model
python test_problem_4_1.py
```

## Requirements

- Python 3.8+
- Pyomo
- NumPy
- HiGHS solver (or other MILP solver like Gurobi, CPLEX, GLPK)

Install dependencies:
```bash
pip install pyomo numpy highspy
```

## Model Structure

The implementation follows the same modular structure as `packing_model_simple`:

1. **parameters.py**: Defines sets and parameters
2. **variables.py**: Defines all decision variables
3. **constraints/**: Modular constraint definitions
   - Each constraint type in separate file
   - Easy to modify or extend
4. **objective.py**: Objective function with customizable weights
5. **model.py**: Main model class that ties everything together

## Key Differences from Problem_4

Compared to the `packing_model_simple` implementation (Problem_4):

1. **No Setup Times**: Problem_4_1 omits setup time parameters `s(i,k,j)`
2. **No Batch Variables**: No batch indicator `b(i,k)` or setup sequencing `y(i,k,j)`
3. **Simpler Objective**: 3-term objective (no OTIF term, no line utilization term as separate)
4. **Simplified WIP**: Direct production-inventory tracking without complex completion logic

## Notes

- **OTIF Constraint**: Problem_4_1.pdf Page 6 appears blank, so OTIF handling is minimal
- **Total Not Utilized**: The third objective term is not clearly defined in the PDF; implemented as unused worker capacity
- **Ship After Due**: Interpreted as ship time ≥ due date (allows late shipping)

## Troubleshooting

### Model is infeasible
- Check that `n_timeslots` is large enough for all processing times
- Verify `reserved_capacity` isn't too restrictive
- Ensure due dates are achievable given processing times

### Solver takes too long
- Reduce problem size (fewer orders/lines/timeslots)
- Increase `mip_rel_gap` for faster but less optimal solutions
- Use a commercial solver like Gurobi for better performance

## License

This implementation is part of the packing schedule optimization project.
