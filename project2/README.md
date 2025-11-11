# Project 2 - Simple Packing Schedule Optimization (Problem 4.1.c2)

## Overview

This project implements a simplified packing schedule optimization model (Problem 4.1.c2 variant) focused on production scheduling with product types, setup times, and inventory management.

## Key Features

- **Product Types**: Multiple unique packing types with type-specific processing
- **Setup Times**: Sequence-dependent changeover times between product types
- **Inventory Management**: Track WIP inventory between production and shipping
- **Demand Fulfillment**: Match production to shipping demands with due dates
- **Multi-Line Production**: Assign orders to different production lines
- **Continuous Time**: Flexible start/completion times (no discrete time slots)

## Structure

```
project2/
├── src/
│   └── simple_packing_model/     # Main package
│       ├── __init__.py
│       ├── model.py              # Core model class
│       ├── parameters.py         # Parameter definitions
│       ├── variables.py          # Decision variables
│       ├── objective.py          # Objective function
│       └── constraints/          # Constraint modules
│           ├── assignment.py
│           ├── capacity.py
│           ├── otif.py
│           ├── shipping.py
│           ├── wip.py
│           └── workforce.py
├── examples/                      # Example scripts
│   ├── problem_3_example.py      # Basic usage example
│   └── problem_3_configurable_example.py  # Configurable scenarios
├── tests/                        # Unit and integration tests
└── README.md                     # This file
```

## Installation

From the repository root:

```bash
# Install in development mode
pip install -e project2/
```

Or add to PYTHONPATH:

```bash
# From repository root
export PYTHONPATH="${PYTHONPATH}:$(pwd)/project2/src"
```

## Usage

### Running Examples

```bash
cd project2/examples

# Basic example with sample data
python problem_3_example.py

# Configurable example (adjust parameters in the file)
python problem_3_configurable_example.py
```

### Importing in Code

```python
from simple_packing_model import PackingScheduleModelProblem4_1_c2
```

### Example Usage

```python
import numpy as np
from simple_packing_model import PackingScheduleModelProblem4_1_c2

# Define problem data
data = {
    'n_unique_types': 2,
    'n_orders': 4,
    'n_demands': 2,
    'n_lines': 2,
    'T_max': 60.0,
    'processing_time': np.array([[10.0, 12.0], [15.0, 13.0]]),
    'setup_time': np.array([[0.0, 5.0], [5.0, 0.0]]),
    'initial_inventory': np.array([0, 0]),
    'order_type': np.array([1, 1, 2, 2]),
    'due_date': np.array([20.0, 40.0]),
    'demand_type': np.array([1, 2]),
    'demand_qty': np.array([2, 2]),
    'priority': np.array([10, 10, 10, 10]),
    'objective_weights': {
        'alpha': 1.0,
        'beta': 1.0,
        'gamma': 2.0,
        'delta': 0.5
    }
}

# Build and solve model
model = PackingScheduleModelProblem4_1_c2(data)
results = model.solve(solver_name='appsi_highs', time_limit=300)

# Print results
model.print_solution_summary()
```

## Model Parameters

### Required Input Data

- `n_unique_types`: Number of unique product types
- `n_orders`: Number of production orders
- `n_demands`: Number of shipping demands
- `n_lines`: Number of production lines
- `T_max`: Planning horizon (time units)
- `processing_time[u,j]`: Processing time for type u on line j
- `setup_time[u,v]`: Setup time to change from type u to type v
- `initial_inventory[u]`: Initial inventory for type u
- `order_type[i]`: Product type for order i
- `due_date[d]`: Due date for demand d
- `demand_type[d]`: Product type for demand d
- `demand_qty[d]`: Quantity for demand d
- `priority[i]`: Priority weight for order i
- `objective_weights`: Dict with alpha, beta, gamma, delta weights

## Available Examples

### 1. Basic Example (problem_3_example.py)
Simple demonstration with:
- 2 product types
- 4 production orders
- 2 shipping demands
- 2 production lines
- Clear output and solution summary

### 2. Configurable Example (problem_3_configurable_example.py)
Flexible scenario generator allowing you to easily test different problem sizes by modifying configuration parameters at the top of the file.

## Development

### Adding Constraints

Place new constraint modules in `src/simple_packing_model/constraints/`:

```python
def add_my_constraint(model, params):
    """Add custom constraint."""
    # Implementation
    pass
```

### Adding Examples

Create example scripts in `examples/`:
- Follow the pattern in `problem_3_example.py`
- Include proper import path setup
- Document the scenario clearly

### Adding Tests

Place test files in `tests/`:
- `tests/test_model.py`
- `tests/test_constraints.py`

## Testing

```bash
cd project2
python -m pytest tests/
```

## Troubleshooting

If you encounter `ModuleNotFoundError: No module named 'simple_packing_model'`:
1. Ensure you're running from `project2/examples/` directory
2. Verify the import path setup is correct in the script
3. Check that `project2/src/simple_packing_model/` exists

All examples have been updated with correct import paths.
