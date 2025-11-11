# Quick Reference Guide

## File Structure

```
packing-schedule-example/
├── packing_model/              # Main model package (NEW MODULAR STRUCTURE)
│   ├── __init__.py
│   ├── model.py                # Main coordinator
│   ├── parameters.py           # Input parameters
│   ├── variables.py            # Decision variables
│   ├── objective.py            # Objective function
│   └── constraints/            # Constraints by category
│       ├── __init__.py
│       ├── assignment.py
│       ├── capacity.py
│       ├── worker.py
│       ├── otif.py
│       ├── wip.py
│       └── workforce.py
├── packing_schedule_model.py   # Old monolithic version (kept for reference)
├── example.py                  # Usage examples
├── requirements.txt            # Python dependencies
├── README.md                   # General documentation
├── ARCHITECTURE.md             # Detailed architecture docs
├── FIXES_APPLIED.md            # Bug fixes documentation
└── QUICK_REFERENCE.md          # This file
```

## Quick Start (5 Minutes)

```bash
# 1. Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run example
python example.py
```

## Basic Usage

```python
from packing_model import PackingScheduleModel

# 1. Prepare data
data = {
    'n_orders': 5,
    'n_lines': 3,
    'n_timeslots': 20,
    'n_workers': 4,
    # ... other required fields ...
}

# 2. Create model
model = PackingScheduleModel(data)

# 3. Solve
results = model.solve(solver_name='appsi_highs', tee=False)

# 4. Get solution
solution = model.get_solution()

# 5. Display summary
model.print_solution_summary()
```

## Required Data Fields

### Dimensions
- `n_orders`: Number of orders (int)
- `n_lines`: Number of production lines (int)
- `n_timeslots`: Number of time periods (int)
- `n_workers`: Number of workers (int)

### Arrays/Matrices
- `processing_time`: [n_orders x n_lines] array
- `setup_time`: [n_orders x n_orders x n_lines] array
- `worker_availability`: [n_workers x n_timeslots] binary array
- `initial_inventory`: [n_orders] array
- `shipping_schedule`: [n_orders x n_timeslots] binary array
- `due_date`: [n_orders] array
- `demand`: [n_orders] array
- `priority`: [n_orders] array

### Scalars
- `reserved_capacity`: float (0-1), e.g., 0.1 = 10% reserved
- `workforce_target`: int, target number of workers

### Weights
- `objective_weights`: dict with keys:
  - `'alpha'`: OTIF weight
  - `'beta'`: WIP weight
  - `'gamma'`: Workforce weight
  - `'delta'`: Line utilization weight

## Adding New Components

### Add a Parameter

**File**: `packing_model/parameters.py`

```python
# In ParameterManager class:
def _define_my_category_parameters(self):
    model = self.model
    data = self.data

    model.my_param = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: data['my_param'][i-1],
        doc="My parameter description"
    )

# Don't forget to call it:
def define_all_parameters(self):
    # ... existing ...
    self._define_my_category_parameters()
```

### Add a Variable

**File**: `packing_model/variables.py`

```python
# In VariableManager class:
def _define_my_category_variables(self):
    model = self.model

    model.my_var = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.Binary,
        doc="My variable description"
    )

# Don't forget to call it:
def define_all_variables(self):
    # ... existing ...
    self._define_my_category_variables()
```

### Add a Constraint

**File**: `packing_model/constraints/my_constraint.py`

```python
import pyomo.environ as pyo

def add_my_constraints(model, data):
    """Add my custom constraints."""

    def my_rule(m, i):
        """Constraint description."""
        return m.my_var[i] <= some_expression

    model.my_constraint = pyo.Constraint(
        model.ORDERS,
        rule=my_rule,
        doc="Constraint description"
    )
```

**File**: `packing_model/constraints/__init__.py`

```python
from .my_constraint import add_my_constraints

def add_all_constraints(model, data):
    # ... existing ...
    add_my_constraints(model, data)
```

### Add an Objective Term

**File**: `packing_model/objective.py`

```python
# In ObjectiveManager class:
def _my_objective_term(self, m):
    """Calculate my objective component."""
    return sum(m.my_var[i] for i in m.ORDERS)

# Add to combined objective:
def objective_rule(m):
    return (
        self.weights['alpha'] * self._otif_term(m) +
        self.weights['beta'] * self._wip_term(m) +
        self.weights['gamma'] * self._workforce_term(m) +
        self.weights['delta'] * self._line_utilization_term(m) +
        self.weights['epsilon'] * self._my_objective_term(m)  # NEW
    )
```

## Common Solver Options

```python
# Time limit (seconds)
model.solve(solver_name='appsi_highs', time_limit=300)

# MIP gap tolerance (1% = 0.01)
model.solve(solver_name='appsi_highs', mip_rel_gap=0.01)

# Number of threads
model.solve(solver_name='appsi_highs', threads=4)

# Show solver output
model.solve(solver_name='appsi_highs', tee=True)

# Combined
model.solve(
    solver_name='appsi_highs',
    tee=True,
    time_limit=600,
    mip_rel_gap=0.01,
    threads=4
)
```

## Solution Access

```python
solution = model.get_solution()

# Access assignments
for assignment in solution['assignments']:
    print(f"Order {assignment['order']} on Line {assignment['line']}")

# Access OTIF metrics
for order_id, metrics in solution['otif_metrics'].items():
    if metrics['late']:
        print(f"Order {order_id} is late by {metrics['lateness']} units")

# Access workforce metrics
for time, metrics in solution['workforce_metrics'].items():
    print(f"Time {time}: {metrics['workers_used']} workers")

# Access WIP metrics
for time, metrics in solution['wip_metrics'].items():
    print(f"Time {time}: {metrics['wip_count']} orders in progress")

# Access line usage
for line_info in solution['line_usage']:
    if line_info['used']:
        print(f"Line {line_info['line']} is being used")
```

## Export Solution

```python
# Export detailed solution to file
model.export_solution('my_solution.txt')

# Print formatted summary to console
model.print_solution_summary()
```

## Module Locations

| Component | File | Key Class/Function |
|-----------|------|-------------------|
| Main Model | `model.py` | `PackingScheduleModel` |
| Parameters | `parameters.py` | `ParameterManager` |
| Variables | `variables.py` | `VariableManager` |
| Objective | `objective.py` | `ObjectiveManager` |
| Constraints | `constraints/*.py` | `add_*_constraints()` |

## Constraint Categories

| Category | File | Purpose |
|----------|------|---------|
| Assignment | `assignment.py` | Order assignment rules |
| Capacity | `capacity.py` | Line capacity limits |
| Worker | `worker.py` | Worker availability |
| OTIF | `otif.py` | On-time delivery tracking |
| WIP | `wip.py` | Work-in-progress tracking |
| Workforce | `workforce.py` | Workforce management |

## Troubleshooting

### Model won't solve
- Check that all required data fields are present
- Verify array dimensions match declared sizes
- Ensure processing times fit within time horizon
- Check that workers are available when needed

### Infeasible model
- Reduce `reserved_capacity` (try 0.05 instead of 0.1)
- Increase `n_timeslots`
- Check that due dates are achievable
- Verify worker availability covers required times

### Slow solving
- Reduce problem size (fewer orders/timeslots)
- Set time limit: `time_limit=300`
- Accept near-optimal: `mip_rel_gap=0.05`
- Use more threads: `threads=4`

### Import errors
```python
# Wrong (old monolithic)
from packing_schedule_model import PackingScheduleModel

# Correct (new modular)
from packing_model import PackingScheduleModel
```

## Performance Tips

1. **Start small**: Test with 2-3 orders before scaling up
2. **Use realistic time slots**: Don't make time horizon too large
3. **Set solver limits**: Always use `time_limit` for production
4. **Accept good solutions**: Use `mip_rel_gap=0.01` (1% from optimal)
5. **Profile your data**: Large processing times → need more timeslots

## Testing Changes

```bash
# Run example to verify everything works
python example.py

# Check specific module (interactive Python)
python
>>> from packing_model import PackingScheduleModel
>>> from packing_model.parameters import ParameterManager
>>> from packing_model.constraints import add_all_constraints
>>> # Test your imports work
```

## Getting Help

1. **README.md**: General overview and installation
2. **ARCHITECTURE.md**: Detailed architecture documentation
3. **Code comments**: Every function has docstrings
4. **example.py**: Working code examples
5. **FIXES_APPLIED.md**: Known issues and solutions

## Key Pyomo Concepts

### Parameter vs Variable
- **Parameter**: Input data (fixed values)
- **Variable**: Decision to be optimized

### Domains
- `pyo.Binary`: 0 or 1
- `pyo.NonNegativeIntegers`: 0, 1, 2, 3, ...
- `pyo.NonNegativeReals`: Any value >= 0
- `pyo.Reals`: Any value

### Constraints
- Use `==` for equality
- Use `<=` or `>=` for inequality
- Return `pyo.Constraint.Skip` to conditionally skip

### Objective
- `sense=pyo.minimize`: Find minimum value
- `sense=pyo.maximize`: Find maximum value

## Common Patterns

### Summing over subset
```python
# Sum only when condition is true
expr = sum(m.x[i,j,t,w]
          for i in m.ORDERS
          for j in m.LINES
          if some_condition(i, j))
```

### Conditional constraint
```python
def my_rule(m, i):
    if i == 1:
        return pyo.Constraint.Skip  # Don't create for i=1
    return m.var[i] <= m.var[i-1]
```

### Big-M constraint
```python
# Force x <= M when indicator = 1
return m.x[i] <= m.indicator[i] * BIG_M
```

---

**Last Updated**: 2025
**Version**: 1.0.0
