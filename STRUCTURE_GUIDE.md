# Project Structure Guide

## Overview

This repository contains two independent projects with proper separation of source code and examples.

## Directory Structure

```
packing-schedule-example/
├── project1/                    # First project (Packing Schedule Model)
│   ├── src/
│   │   ├── project1/           # Project 1 package (placeholder)
│   │   └── packing_model/      # Main packing model implementation
│   │       ├── __init__.py
│   │       ├── model.py        # Core model class
│   │       ├── parameters.py   # Parameter definitions
│   │       ├── variables.py    # Decision variables
│   │       ├── objective.py    # Objective function
│   │       └── constraints/    # Constraint modules
│   │           ├── assignment.py
│   │           ├── capacity.py
│   │           ├── otif.py
│   │           ├── shipping.py
│   │           ├── wip.py
│   │           ├── worker.py
│   │           └── workforce.py
│   ├── examples/               # Example scripts
│   │   ├── setup_batching_example.py
│   │   ├── line_selection_example.py
│   │   ├── parallel_processing_example.py
│   │   ├── constrained_capacity_example.py
│   │   ├── configurable_scenario_example.py
│   │   └── large_scale_weekly_production.py
│   ├── tests/                  # Test files
│   │   └── test_basic.py
│   ├── setup.py               # Package installation config
│   └── README.md              # Project documentation
│
├── project2/                   # Second project (Simple Packing Model - Problem 4.1.c2)
│   ├── src/
│   │   └── simple_packing_model/  # Simple packing model implementation
│   │       ├── __init__.py
│   │       ├── model.py        # Core model class
│   │       ├── parameters.py   # Parameter definitions
│   │       ├── variables.py    # Decision variables
│   │       ├── objective.py    # Objective function
│   │       └── constraints/    # Constraint modules
│   │           ├── assignment.py
│   │           ├── capacity.py
│   │           ├── otif.py
│   │           ├── shipping.py
│   │           ├── wip.py
│   │           └── workforce.py
│   ├── examples/               # Example scripts
│   │   ├── problem_3_example.py
│   │   ├── problem_3_configurable_example.py
│   │   └── problem_3_inventory_example.py
│   ├── tests/                  # Test files
│   │   └── test_basic.py
│   ├── setup.py               # Package installation config
│   └── README.md              # Project documentation
│
├── README.md                   # Main repository README
├── requirements.txt            # Shared dependencies
└── .gitignore                 # Git ignore patterns
```

## How to Use

### Running Examples

All example scripts have been fixed to properly import the `packing_model` module. You can run them directly:

```bash
# From the repository root
cd project1/examples
python setup_batching_example.py
python line_selection_example.py
python parallel_processing_example.py
# ... etc
```

### Import Fix Applied

All example scripts now use the correct import path:

```python
# Add src directory to path to import packing_model
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from packing_model import PackingScheduleModel
```

This ensures Python can find the `packing_model` module located in `project1/src/packing_model/`.

### Installing as a Package (Optional)

You can install the project as a package for easier imports:

```bash
# From repository root
pip install -e project1/
```

Then you can import from anywhere:

```python
from packing_model import PackingScheduleModel
```

## Available Examples

### 1. Setup Batching Example
**File**: `setup_batching_example.py`

Demonstrates setup time optimization and order batching by product families.
- 10 orders in 3 product families
- Sequence-dependent setup times
- Batching efficiency analysis

### 2. Line Selection Example
**File**: `line_selection_example.py`

Shows how the optimizer chooses between multiple production lines.
- 2 production lines with different speeds
- 5 orders with varying processing times
- Single vs. multi-line optimization

### 3. Parallel Processing Example
**File**: `parallel_processing_example.py`

Demonstrates parallel processing with multiple lines and workers.
- 2 production lines
- 2 workers
- Parallel execution analysis

### 4. Constrained Capacity Example
**File**: `constrained_capacity_example.py`

Shows behavior under tight capacity constraints.
- Limited production capacity
- Tight due dates
- Trade-offs analysis

### 5. Configurable Scenario Example
**File**: `configurable_scenario_example.py`

Flexible example with configurable parameters.
- Adjustable problem size
- Customizable constraints
- Experimentation framework

### 6. Large Scale Weekly Production
**File**: `large_scale_weekly_production.py`

Industrial-scale scheduling demonstration.
- 48 production lines
- 1700 orders
- 7-day planning horizon
- Computational performance testing

## Project 2 Examples

### 1. Problem 3 Example
**File**: `project2/examples/problem_3_example.py`

Basic demonstration of the simple packing model (Problem 4.1.c2).
- 2 product types
- 4 production orders
- 2 shipping demands
- Product type assignments
- Setup time optimization
- Inventory management

### 2. Problem 3 Configurable Example
**File**: `project2/examples/problem_3_configurable_example.py`

Flexible scenario generator for the simple packing model.
- Configurable problem dimensions
- Automatic data generation
- Easy parameter adjustment
- Multiple scenario testing

### 3. Problem 3 Inventory Example
**File**: `project2/examples/problem_3_inventory_example.py`

Demonstrates inventory-first fulfillment on a single production line.
- 1 production line (sequential processing)
- Initial inventory: 3 units Type 1, 2 units Type 2
- 3 shipping demands
- Shows when inventory vs. production is used
- Clear visualization of inventory depletion
- Inventory-first fulfillment strategy

## Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

Key dependencies:
- pyomo (optimization modeling)
- numpy (numerical computing)
- highspy (solver)
- pandas (data processing)
- matplotlib (visualization)

## Next Steps

1. **For Project 1**: Add your custom modules to `project1/src/packing_model/`
2. **For Project 2**: Implement your second project in `project2/src/project2/`
3. **Examples**: Create new examples in the respective `examples/` folders
4. **Tests**: Add tests in the respective `tests/` folders

## Troubleshooting

### ModuleNotFoundError: No module named 'packing_model'

If you see this error, verify:
1. You're running from the `project1/examples/` directory
2. The import path fix is in place (should be automatic now)
3. The `project1/src/packing_model/` directory exists

All examples have been updated with the correct import paths, so this error should no longer occur.
