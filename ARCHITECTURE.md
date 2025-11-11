# Packing Schedule Model - Architecture Documentation

This document describes the modular architecture of the packing schedule optimization model.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Module Descriptions](#module-descriptions)
- [Extending the Model](#extending-the-model)
- [Design Principles](#design-principles)

---

## Overview

The packing schedule optimization model has been refactored into a modular architecture with clear separation of concerns. Each component (parameters, variables, constraints, objective) is defined in its own module, making the code:

- **Easy to understand**: Each module has a single responsibility
- **Easy to extend**: Add new components without touching existing code
- **Easy to maintain**: Changes are localized to specific modules
- **Easy to test**: Each module can be tested independently

---

## Package Structure

```
packing_model/
├── __init__.py                 # Package initialization, exports PackingScheduleModel
├── model.py                    # Main model class that coordinates everything
├── parameters.py               # Input parameter definitions
├── variables.py                # Decision variable definitions
├── objective.py                # Objective function definition
└── constraints/                # Constraint definitions organized by category
    ├── __init__.py             # Exports add_all_constraints()
    ├── assignment.py           # Order assignment constraints
    ├── capacity.py             # Line capacity constraints
    ├── worker.py               # Worker availability constraints
    ├── otif.py                 # OTIF tracking constraints
    ├── wip.py                  # WIP tracking constraints
    └── workforce.py            # Workforce management constraints
```

### Old vs New Structure

**Before (Monolithic):**
```
packing_schedule_model.py       # Single 750+ line file with everything
```

**After (Modular):**
```
packing_model/                  # Package with clear organization
├── model.py                    # 250 lines - coordination logic
├── parameters.py               # 100 lines - parameter definitions
├── variables.py                # 200 lines - variable definitions
├── objective.py                # 150 lines - objective function
└── constraints/                # 600 lines total across 6 files
    ├── assignment.py           # 40 lines
    ├── capacity.py             # 120 lines
    ├── worker.py               # 80 lines
    ├── otif.py                 # 160 lines
    ├── wip.py                  # 130 lines
    └── workforce.py            # 120 lines
```

---

## Module Descriptions

### 1. `model.py` - Main Model Coordinator

**Purpose**: Ties all components together and provides the main user interface.

**Key Class**: `PackingScheduleModel`

**Responsibilities**:
- Initialize the Pyomo ConcreteModel
- Define index sets (ORDERS, LINES, TIME, WORKERS)
- Coordinate module initialization in correct order
- Provide solve() method
- Provide solution extraction and display methods

**Usage**:
```python
from packing_model import PackingScheduleModel

model = PackingScheduleModel(data)
results = model.solve()
solution = model.get_solution()
```

**Methods**:
- `__init__(data)`: Create and build complete model
- `_define_sets()`: Define index sets
- `solve(solver_name, **options)`: Solve the model
- `get_solution()`: Extract solution as dictionary
- `print_solution_summary()`: Display formatted summary
- `export_solution(filename)`: Export detailed solution to file

---

### 2. `parameters.py` - Input Parameters

**Purpose**: Define all input parameters for the model.

**Key Class**: `ParameterManager`

**Responsibilities**:
- Define processing and setup time parameters
- Define resource availability parameters
- Define inventory and shipping parameters
- Define OTIF parameters (due dates, priorities)
- Define workforce parameters

**Categories**:
1. **Processing Parameters**: `p[i,j]`, `s[i,k,j]`
2. **Resource Parameters**: `a[w,t]`, `alpha`
3. **Inventory Parameters**: `inv0[i]`, `ship[i,t]`
4. **OTIF Parameters**: `due[i]`, `demand[i]`, `priority[i]`
5. **Workforce Parameters**: `workforce_target`

**Adding New Parameters**:
```python
def _define_new_category_parameters(self):
    """Define new category of parameters."""
    model = self.model
    data = self.data

    model.new_param = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: data['new_param_data'][i-1],
        doc="Description of new parameter"
    )
```

Then call in `define_all_parameters()`:
```python
def define_all_parameters(self):
    self._define_processing_parameters()
    self._define_resource_parameters()
    # ... existing categories ...
    self._define_new_category_parameters()  # Add new category
```

---

### 3. `variables.py` - Decision Variables

**Purpose**: Define all decision variables for the model.

**Key Class**: `VariableManager`

**Responsibilities**:
- Define primary scheduling variables
- Define OTIF tracking variables
- Define workforce tracking variables
- Define WIP tracking variables

**Categories**:
1. **Primary Variables**: `x[i,j,t,w]`, `y[i,k,j]`, `b[i,k]`, etc.
2. **OTIF Variables**: `late[i]`, `lateness[i]`, `early[i]`
3. **Workforce Variables**: `workers_used[t]`, `workers_max`, etc.
4. **WIP Variables**: `time_start[i]`, `time_completion[i]`, `wip[t]`

**Adding New Variables**:
```python
def _define_new_category_variables(self):
    """Define new category of variables."""
    model = self.model

    model.new_var = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.Binary,  # or NonNegativeIntegers, Reals, etc.
        doc="Description of new variable"
    )
```

Then call in `define_all_variables()`:
```python
def define_all_variables(self):
    self._define_primary_variables()
    self._define_otif_variables()
    # ... existing categories ...
    self._define_new_category_variables()  # Add new category
```

---

### 4. `objective.py` - Objective Function

**Purpose**: Define the objective function to be minimized/maximized.

**Key Class**: `ObjectiveManager`

**Responsibilities**:
- Combine multiple objective terms with weights
- Define OTIF objective component
- Define WIP objective component
- Define workforce objective component
- Define line utilization objective component

**Structure**:
```python
objective = alpha * OTIF + beta * WIP + gamma * Workforce + delta * LineUtil
```

**Objective Terms**:
1. **OTIF Term**: `sum(priority[i] * (7*late[i] + 3*lateness[i]))`
2. **WIP Term**: `4*sum(wip[t]) + 6*sum(time_flow[i])`
3. **Workforce Term**: `5*range + 3*deviation + 2*changes`
4. **Line Utilization**: `sum(u[j])`

**Adding New Objective Terms**:
```python
def _new_objective_term(self, m):
    """
    New objective term description.

    Args:
        m: Model instance

    Returns:
        Pyomo expression
    """
    return sum(m.new_var[i] for i in m.ORDERS)
```

Then add to combined objective:
```python
def objective_rule(m):
    return (
        self.weights['alpha'] * self._otif_term(m) +
        self.weights['beta'] * self._wip_term(m) +
        self.weights['gamma'] * self._workforce_term(m) +
        self.weights['delta'] * self._line_utilization_term(m) +
        self.weights['epsilon'] * self._new_objective_term(m)  # New term
    )
```

---

### 5. `constraints/` - Constraint Modules

**Purpose**: Organize constraints by logical category.

#### `constraints/__init__.py`

Main entry point that calls all constraint modules:
```python
def add_all_constraints(model, data):
    add_assignment_constraints(model, data)
    add_capacity_constraints(model, data)
    add_worker_constraints(model, data)
    add_otif_constraints(model, data)
    add_wip_constraints(model, data)
    add_workforce_constraints(model, data)
```

#### `constraints/assignment.py`

**Constraints**: Order assignment rules
- `one_assignment`: Each order assigned exactly once

#### `constraints/capacity.py`

**Constraints**: Line capacity management
- `line_capacity`: No overlapping orders on same line
- `reserved_line_capacity`: Reserve capacity fraction
- `line_in_use`: Link line usage indicator to assignments

#### `constraints/worker.py`

**Constraints**: Worker availability and assignment
- `worker_working`: Link worker indicator to assignments
- `worker_availability`: Workers only work when available
- `reserved_worker_capacity`: Reserve worker capacity fraction

#### `constraints/otif.py`

**Constraints**: On-Time In-Full tracking
- `start_time`: Calculate order start times
- `completion_time`: Calculate order completion times
- `lateness_*`: Calculate and bound lateness
- `early_*`: Calculate and bound earliness
- `late_indicator_*`: Force late indicator based on completion

#### `constraints/wip.py`

**Constraints**: Work-In-Progress tracking
- `flow_time`: Calculate time from start to shipping
- `production`: Determine when production completes
- `inventory_balance`: Track inventory over time
- `wip_indicator`: Determine if order is WIP
- `wip_count`: Count total WIP at each time

#### `constraints/workforce.py`

**Constraints**: Workforce management
- `workers_used_calc`: Count active workers
- `workers_max_calc`: Track maximum workforce
- `workers_min_calc`: Track minimum workforce
- `workforce_deviation`: Calculate deviation from target
- `workforce_change_*`: Track workforce changes over time

**Adding New Constraint Module**:

1. Create new file `constraints/new_category.py`:
```python
"""
New Category Constraints

Description of what this category handles.
"""

import pyomo.environ as pyo


def add_new_category_constraints(model, data):
    """
    Add new category constraints.

    Args:
        model: Pyomo ConcreteModel
        data: Problem data dictionary
    """

    def new_constraint_rule(m, i):
        """Constraint description."""
        return m.new_var[i] <= some_expression

    model.new_constraint = pyo.Constraint(
        model.ORDERS,
        rule=new_constraint_rule,
        doc="Constraint description"
    )
```

2. Add to `constraints/__init__.py`:
```python
from .new_category import add_new_category_constraints

def add_all_constraints(model, data):
    # ... existing categories ...
    add_new_category_constraints(model, data)  # Add new category
```

---

## Extending the Model

### Example: Adding a Resource Constraint

Let's say you want to add a constraint limiting total energy consumption.

**Step 1**: Add energy parameter to `parameters.py`:
```python
def _define_resource_parameters(self):
    # ... existing parameters ...

    model.energy_per_order = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: data['energy'][i-1],
        doc="Energy consumed by order i"
    )

    model.max_energy = pyo.Param(
        initialize=data['max_energy'],
        doc="Maximum total energy available"
    )
```

**Step 2**: Create new constraint file `constraints/energy.py`:
```python
import pyomo.environ as pyo

def add_energy_constraints(model, data):
    """Limit total energy consumption."""

    def energy_limit_rule(m):
        return sum(
            m.x[i, j, t, w] * m.energy_per_order[i]
            for i in m.ORDERS
            for j in m.LINES
            for t in m.TIME
            for w in m.WORKERS
        ) <= m.max_energy

    model.energy_limit = pyo.Constraint(
        rule=energy_limit_rule,
        doc="Total energy consumption limit"
    )
```

**Step 3**: Add to `constraints/__init__.py`:
```python
from .energy import add_energy_constraints

def add_all_constraints(model, data):
    # ... existing ...
    add_energy_constraints(model, data)
```

**Step 4**: Add data to your input dictionary:
```python
data = {
    # ... existing data ...
    'energy': np.array([10, 15, 8, 20, 12]),  # Energy per order
    'max_energy': 100  # Maximum total energy
}
```

That's it! The new constraint is integrated without modifying existing code.

---

## Design Principles

### 1. Separation of Concerns

Each module has a single, well-defined responsibility:
- **Parameters**: Input data only
- **Variables**: Decision variables only
- **Constraints**: Feasibility rules only
- **Objective**: Optimization goal only
- **Model**: Coordination and interface only

### 2. Open/Closed Principle

The model is:
- **Open for extension**: Easy to add new components
- **Closed for modification**: Don't need to change existing code

### 3. DRY (Don't Repeat Yourself)

Common patterns are extracted into reusable functions:
- `add_parameters(model, data)`
- `add_variables(model, data)`
- `add_all_constraints(model, data)`
- `add_objective(model, data)`

### 4. Single Entry Point

Users only need to import one class:
```python
from packing_model import PackingScheduleModel
```

Everything else is internal implementation.

### 5. Clear Documentation

Every module, class, and function has:
- Docstring explaining purpose
- Parameter descriptions
- Return value descriptions
- Usage examples where helpful

### 6. Consistent Patterns

All modules follow the same pattern:
1. Import Pyomo
2. Define manager class (or functions)
3. Organize by category with private methods
4. Provide public entry point function

---

## Benefits of Modular Architecture

### For Development
- **Parallel work**: Multiple developers can work on different modules
- **Easier debugging**: Issues localized to specific modules
- **Faster testing**: Test individual components independently

### For Maintenance
- **Clear navigation**: Find code quickly by category
- **Safer changes**: Modifications contained to one module
- **Better versioning**: Git diffs show meaningful changes

### For Users
- **Easier learning**: Understand one piece at a time
- **Flexible customization**: Override specific components
- **Better examples**: Show extensions without full model

### For Performance
- **Lazy loading**: Only import what you need (future optimization)
- **Parallel building**: Could parallelize constraint generation (future)
- **Selective optimization**: Profile and optimize specific modules

---

## Migration from Monolithic Model

If you have code using the old `packing_schedule_model.py`:

**Old Code**:
```python
from packing_schedule_model import PackingScheduleModel
```

**New Code**:
```python
from packing_model import PackingScheduleModel
```

Everything else works the same! The API is identical.

---

## Future Enhancements

Potential improvements to the architecture:

1. **Configuration Files**: Load objective weights from YAML/JSON
2. **Constraint Registry**: Dynamic constraint activation/deactivation
3. **Plugin System**: Load custom constraints from external files
4. **Validation Layer**: Validate input data before model building
5. **Caching**: Cache model builds for faster repeated solves
6. **Parallel Processing**: Build constraints in parallel for large problems
7. **Model Reduction**: Automatically remove unused variables/constraints
8. **Sensitivity Analysis**: Built-in parameter sensitivity analysis

---

## Questions?

For questions or suggestions about the architecture:
1. Review the code in each module
2. Check inline documentation
3. Look at example.py for usage patterns
4. See README.md for general documentation

The modular design makes it easy to understand and extend - dive in!
