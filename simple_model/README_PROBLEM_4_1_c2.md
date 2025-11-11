# Problem 4.1 c2 - Packing Schedule Optimization Model

## Overview

This implementation provides a Mixed-Integer Linear Programming (MILP) model for packing schedule optimization based on the formulation in `Problem_4_1_c2.pdf`. The model schedules production orders on multiple lines while minimizing work-in-progress (WIP) inventory, workforce variability, and resource underutilization.

## Problem Formulation

### Indices

- **u = 1, U**: Unique packing types (product families)
- **i = 1, I**: Production orders (decisions to produce products)
- **d = 1, D**: Demands (shipping requirements)
- **j = 1, J**: Production line numbers
- **e ∈ E**: Events (start and completion times)

### Decision Variables

#### Core Assignment Variables
- **x(i,j)**: Binary variable - order i is assigned to line j
- **s(i)**: Real variable - start time of order i
- **c(i)**: Real variable - completion time of order i

#### Workforce Tracking Variables
- **started(i,e)**: Binary - order i has started before event e
- **notcomplete(i,e)**: Binary - order i is not complete before event e
- **active(i,e)**: Binary - order i is active at event e
- **workersused(e)**: Real - total workers working at event e
- **workersmax**: Real - maximum workers used across all events
- **workersmin**: Real - minimum workers used across all events
- **workforcerange**: Real - workforce range (max - min)

#### WIP Tracking Variables
- **prodbefore(u,d)**: Integer - units of type u produced before demand d ships
- **prodorder(i,d)**: Binary - order i produced before demand d ships
- **inv(u,d)**: Integer - inventory of type u after fulfilling demand d
- **ship(d)**: Real - shipping time of demand d

### Input Parameters

- **p(u,j)**: Processing time for item type u on line j
- **s(u,v)**: Setup time for changing from type u to type v
- **inv0(u)**: Initial inventory for packing type u
- **T_max**: Planning horizon
- **type(i)**: Unit type of order i
- **due(d)**: Due date for demand d
- **prodtype(d)**: Unit type for demand d
- **qty(d)**: Quantity for demand d
- **priority(i)**: Priority weight for order i

### Constraints

1. **One Assignment**: Each order assigned to at most one line
   ```
   ∑_j x(i,j) ≤ 1  ∀i
   ```

2. **Processing Time**: Completion time equals start time plus processing
   ```
   c(i) = s(i) + ∑_j p(type(i), j) * x(i,j)  ∀i
   ```

3. **Line Capacity**: No overlap of orders on the same line with setup times
   ```
   s(k) ≥ c(i) + s(type(i), type(k)) - T_max * (3 - x(i,j) - x(k,j) - y(i,k))  ∀i<k ∀j
   s(i) ≥ c(k) + s(type(k), type(i)) - T_max * (2 - x(i,j) - x(k,j) + y(i,k))  ∀i<k ∀j
   ```

4. **Demand Tracking**: Track which orders complete before each demand ships
   ```
   prodbefore(u,d) = ∑_{i:type(i)=u} prodorder(i,d)
   [prodorder(i,d) = 1] ⇒ [c(i) ≤ ship(d)]
   [prodorder(i,d) = 0] ⇒ [c(i) ≥ ship(d) + ε]
   ```

5. **Shipping Constraints**:
   ```
   ship(d) ≤ T_max  ∀d
   ship(d) ≥ due(d)  ∀d
   ```

6. **Inventory Balance**:
   ```
   inv(u,d) = inv0(u) + prodbefore(u,d) - ∑_{d':prodtype(d')=u, d'≤d} qty(d')  ∀u ∀d
   ```

7. **Workforce Tracking**: Event-based active worker counting
   ```
   active(i,e) = started(i,e) ∧ notcomplete(i,e)
   workersused(e) = ∑_i active(i,e)  ∀e
   workersmax ≥ workersused(e)  ∀e
   workersused(e) ≥ workersmin  ∀e
   workforcerange = workersmax - workersmin
   ```

### Objective Function

Minimize a weighted sum of three terms:

```
f = β * wip_obj + γ * workforce + δ * total_not_utilized
```

where:
- **wip_obj**: Total inventory across all types and demands
- **workforce**: Workforce range (max - min workers)
- **total_not_utilized**: Unassigned orders or unused capacity

## Installation & Setup

### Prerequisites

```bash
pip install pyomo numpy
pip install highspy  # For HiGHS solver (recommended)
```

### Directory Structure

```
simple_model/
├── packing_model_problem_4_1_c2/
│   ├── __init__.py
│   ├── model.py                    # Main model class
│   ├── parameters.py               # Parameter definitions
│   ├── variables.py                # Variable definitions
│   ├── objective.py                # Objective function
│   └── constraints/
│       ├── __init__.py
│       ├── assignment.py           # Assignment constraints
│       ├── capacity.py             # Line capacity constraints
│       ├── shipping.py             # Shipping/demand constraints
│       ├── wip.py                  # WIP inventory constraints
│       └── workforce.py            # Workforce tracking constraints
├── problem_4_1_c2_example.py       # Example usage
└── README_PROBLEM_4_1_c2.md        # This file
```

## Usage

### Basic Example

```python
import numpy as np
from packing_model_problem_4_1_c2 import PackingScheduleModelProblem4_1_c2

# Define problem data
data = {
    'n_unique_types': 3,
    'n_orders': 6,
    'n_demands': 4,
    'n_lines': 2,
    'T_max': 100.0,
    'processing_time': np.array([[10.0, 12.0], [15.0, 13.0], [8.0, 10.0]]),
    'setup_time': np.array([[0.0, 5.0, 4.0], [5.0, 0.0, 3.0], [4.0, 3.0, 0.0]]),
    'initial_inventory': np.array([2, 1, 0]),
    'order_type': np.array([1, 1, 2, 2, 3, 3]),
    'due_date': np.array([30.0, 50.0, 70.0, 90.0]),
    'demand_type': np.array([1, 2, 1, 3]),
    'demand_qty': np.array([3, 2, 2, 1]),
    'priority': np.array([10, 10, 15, 15, 5, 5]),
    'objective_weights': {'beta': 1.0, 'gamma': 2.0, 'delta': 0.5}
}

# Create and solve model
model = PackingScheduleModelProblem4_1_c2(data)
results = model.solve(solver_name='appsi_highs', time_limit=300)

# Print results
if results['objective_value'] is not None:
    model.print_solution_summary()
```

### Running the Example

```bash
cd simple_model
python problem_4_1_c2_example.py
```

## Data Format

### Required Input Dictionary Keys

| Key | Type | Description |
|-----|------|-------------|
| `n_unique_types` | int | Number of unique product types (U) |
| `n_orders` | int | Number of production orders (I) |
| `n_demands` | int | Number of shipping demands (D) |
| `n_lines` | int | Number of production lines (J) |
| `T_max` | float | Planning horizon |
| `processing_time` | array[U×J] | Processing times by type and line |
| `setup_time` | array[U×U] | Setup times between types |
| `initial_inventory` | array[U] | Initial inventory by type |
| `order_type` | array[I] | Type of each order (1-indexed) |
| `due_date` | array[D] | Due date for each demand |
| `demand_type` | array[D] | Type for each demand (1-indexed) |
| `demand_qty` | array[D] | Quantity for each demand |
| `priority` | array[I] | Priority weight for each order |
| `objective_weights` | dict | Weights: `beta`, `gamma`, `delta` |

### Array Indexing Note

All arrays use 0-based indexing in Python, but internally the model uses 1-based indexing for Pyomo sets.

## Key Features

### 1. Event-Based Workforce Tracking

Unlike time-discretized formulations, this model uses events (E = {s₁, ..., sₙ, c₁, ..., cₙ}) to track workforce utilization. This provides:
- More accurate workforce counting
- Fewer binary variables than discretized time
- Natural handling of continuous time

### 2. Setup Time Modeling

Setup times are explicitly modeled between different product types:
- Zero setup when same type follows itself
- Non-zero setup when switching types
- Setup time depends on both previous and next type

### 3. Demand-Driven Scheduling

Orders are linked to demands:
- Track which orders complete before each demand ships
- Inventory balance equations ensure feasibility
- Ship no earlier than due date constraint

### 4. Flexible Objective Function

Three-term objective allows balancing:
- **WIP minimization** (β): Reduce inventory costs
- **Workforce stability** (γ): Minimize staffing variability
- **Resource utilization** (δ): Reduce idle capacity

## Solution Information

### Output Dictionary Structure

```python
solution = model.get_solution()
# Returns:
{
    'assignments': [
        {'order': 1, 'line': 1, 'type': 1, 'start': 0.0, 'completion': 10.0, 'duration': 10.0},
        ...
    ],
    'demands': [
        {'demand': 1, 'type': 1, 'quantity': 3, 'due_date': 30.0, 'ship_time': 28.5},
        ...
    ],
    'inventory': {
        1: {1: 2, 2: 1, ...},  # Type 1 inventory after each demand
        ...
    },
    'workforce_events': {
        1: 2.5,  # Workers at event 1
        ...
    },
    'workforce_summary': {
        'max': 3.0,
        'min': 1.0,
        'range': 2.0
    },
    'event_times': {
        1: 0.0,   # Time of event 1 (start of order 1)
        ...
    }
}
```

## Performance Considerations

### Model Size

For a problem with:
- I orders
- J lines
- D demands
- U types

The model has approximately:
- **Binary variables**: O(I·J + I·D + I²·J + I·E)
- **Continuous variables**: O(I + D + U·D + E)
- **Constraints**: O(I·J·I + I·D + U·D + I·E)

where E = 2·I (number of events)

### Scaling Tips

1. **For large problems** (>50 orders):
   - Use commercial solvers (Gurobi, CPLEX)
   - Set appropriate time limits and MIP gaps
   - Consider decomposition methods

2. **For faster solve times**:
   - Reduce planning horizon if possible
   - Use tighter bounds on variables
   - Enable solver preprocessing
   - Use warmstart with previous solutions

3. **For numerical stability**:
   - Scale time units appropriately
   - Use reasonable Big-M values
   - Check for infeasibility if solver struggles

## Solver Options

### HiGHS (Default, Free)
```python
results = model.solve(
    solver_name='appsi_highs',
    time_limit=300,      # seconds
    mip_rel_gap=0.01     # 1% optimality gap
)
```

### Gurobi (Commercial)
```python
results = model.solve(
    solver_name='gurobi',
    time_limit=300,
    mip_rel_gap=0.01
)
```

### CPLEX (Commercial)
```python
results = model.solve(
    solver_name='cplex',
    time_limit=300,
    mip_rel_gap=0.01
)
```

## Troubleshooting

### Common Issues

1. **Model is infeasible**
   - Check if T_max is large enough
   - Verify initial inventory can satisfy demands
   - Ensure processing times are reasonable
   - Check due dates are achievable

2. **Solver takes too long**
   - Reduce problem size or time horizon
   - Increase MIP gap tolerance
   - Use commercial solver
   - Add valid inequalities or cuts

3. **Unexpected results**
   - Verify input data (especially 1-based indexing for types)
   - Check objective weights are appropriate
   - Review constraint formulations
   - Validate solution manually

## References

- Problem formulation: `Problem_4_1_c2.pdf`
- Pyomo documentation: https://pyomo.readthedocs.io/
- HiGHS solver: https://highs.dev/

## License

This implementation is provided as-is for educational and research purposes.

## Contact

For questions or issues, please refer to the problem specification document or consult with the project maintainers.
