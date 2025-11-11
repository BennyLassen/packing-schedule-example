# Packing Schedule Optimization

A Mixed Integer Linear Programming (MILP) model for optimizing packing order schedules across multiple production lines with worker assignments. This implementation uses Pyomo with the HiGHS solver.

**🎉 Now with Modular Architecture!** The codebase has been refactored into a clean, modular structure for easy extension and maintenance. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

**✨ Problem 2 Implementation:** This implementation now includes **flexible shipping decisions** where the optimizer decides when each order should ship (instead of using a fixed shipping schedule). See [PROBLEM_2_CHANGES.md](PROBLEM_2_CHANGES.md) for details on the differences from Problem 1.

**🚀 Problem 3 Implementation:** This implementation now includes a **worker movement penalty** that discourages workers from switching between production lines, which can help reduce setup time and improve production efficiency.

## Table of Contents

- [Problem Description](#problem-description)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Problem Formulation](#problem-formulation)
- [Code Structure](#code-structure)
- [Usage Guide](#usage-guide)
- [Extending the Model](#extending-the-model)

## Additional Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed modular architecture documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference guide for common tasks
- **[PROBLEM_2_CHANGES.md](PROBLEM_2_CHANGES.md)** - Problem 2 implementation details and changes
- **[PROBLEM_3_CHANGES.md](PROBLEM_3_CHANGES.md)** - Problem 3 worker movement penalty implementation
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - Documentation of bug fixes and solutions
- **[examples/](examples/)** - Example scripts demonstrating various scenarios and use cases

---

## Problem Description

The packing schedule optimization problem involves assigning packing orders to production lines with specific workers at specific times to minimize costs while meeting delivery deadlines and capacity constraints.

### Key Features

- **Multi-objective optimization**: Balances OTIF (On-Time In-Full) performance, WIP (Work-In-Progress), workforce utilization, and line utilization
- **Complex constraints**: Handles line capacity, worker availability, setup times, and inventory management
- **Flexible configuration**: Easy to extend with additional variables, constraints, and objective terms

### Use Cases

- Manufacturing scheduling
- Production line optimization
- Workforce planning
- Inventory management

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Create a Virtual Environment

#### On Windows:

```bash
# Navigate to the project directory
cd packing-schedule-example

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
# Navigate to the project directory
cd packing-schedule-example

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `pyomo>=6.0.0` - Optimization modeling framework
- `numpy>=1.20.0` - Numerical computing
- `highspy>=1.12.0` - HiGHS solver interface
- `pandas` - Data manipulation (optional, for data import/export)
- `matplotlib>=3.3.0` - Visualization (optional)

### Step 3: Verify Installation

```bash
python -c "import pyomo.environ as pyo; print('Pyomo installed successfully')"
python -c "import highspy; print('HiGHS installed successfully')"
```

---

## Quick Start

### Run the Basic Example

```bash
# Make sure virtual environment is activated
python example.py
```

This will:
1. Create sample problem data
2. Build the optimization model
3. Solve using HiGHS
4. Display the solution summary

### Explore More Examples

The `examples/` folder contains additional scenarios demonstrating different use cases:

```bash
# Run the constrained capacity example (trade-off analysis)
python examples/constrained_capacity_example.py

# Run the setup and batching example (product family sequencing - 10 orders)
python examples/setup_batching_example.py

# Run the line selection example (1 worker, 2 lines)
python examples/line_selection_example.py

# Run the parallel processing example (2 workers, 2 lines)
python examples/parallel_processing_example.py

# Run the large-scale weekly production example (48 lines, 48 workers, 1700 orders)
python examples/large_scale_weekly_production.py
```

**Note**: The large-scale example demonstrates industrial-scale scheduling (1700 orders, 48 lines, 7-day horizon) and may take 10-60 minutes to solve.

See [examples/README.md](examples/README.md) for a complete list of available examples and what each demonstrates.

### Expected Output

```
================================================================================
PACKING SCHEDULE OPTIMIZATION - EXAMPLE
================================================================================

[Step 1] Creating sample data...
  - Number of orders: 5
  - Number of lines: 3
  - Number of time slots: 20
  - Number of workers: 4

[Step 2] Building optimization model...
  - Model created successfully

[Step 3] Solving the optimization problem...
  - Using HiGHS solver
  - Solver status: ok
  - Termination condition: optimal
  - Objective value: 123.45

[Step 4] Extracting solution...

================================================================================
SOLUTION SUMMARY
================================================================================
...
```

---

## Problem Formulation

### Indices

| Index | Description | Range |
|-------|-------------|-------|
| `i` | Packing orders | `1, ..., n` |
| `j` | Production lines | `1, ..., m` |
| `t` | Time slots | `1, ..., T` |
| `w` | Workers | `1, ..., W` |

### Decision Variables

#### Primary Variables

| Variable | Type | Description |
|----------|------|-------------|
| `x[i,j,t,w]` | Binary | Order `i` starts on line `j` at time `t` with worker `w` |
| `y[i,k,j]` | Binary | Setup between orders `i` and `k` on line `j` |
| `b[i,k]` | Binary | Orders `i` and `k` batched together |
| `w_working[w,t]` | Binary | Worker `w` is working during time `t` |
| `m[w,t]` | Binary | Worker `w` moved to another line at time `t` |
| `prod[i,t]` | Integer | Units produced at time `t` |
| `inv[i,t]` | Integer | Inventory of order `i` at time `t` |
| `u[j]` | Binary | Line `j` is used |

#### OTIF (On-Time In-Full) Tracking

| Variable | Type | Description |
|----------|------|-------------|
| `late[i]` | Binary | Order `i` is late |
| `lateness[i]` | Integer | Amount of lateness for order `i` |
| `early[i]` | Integer | Amount of earliness for order `i` |

#### Workforce Tracking

| Variable | Type | Description |
|----------|------|-------------|
| `workers_used[t]` | Integer | Total workers active at time `t` |
| `workers_max` | Integer | Maximum workers used in any time slot |
| `workers_min` | Integer | Minimum workers used in any time slot |
| `deviation_above[t]` | Integer | Workers above target at time `t` |
| `deviation_below[t]` | Integer | Workers below target at time `t` |
| `workforce_change[t]` | Integer | Absolute change in workforce from `t-1` to `t` |
| `workforce_increase[t]` | Integer | Increase in workforce from `t-1` to `t` |
| `workforce_decrease[t]` | Integer | Decrease in workforce from `t-1` to `t` |

#### WIP (Work-In-Progress) Tracking

| Variable | Type | Description |
|----------|------|-------------|
| `time_start[i]` | Integer | Start time for order `i` |
| `time_completion[i]` | Integer | Completion time for order `i` |
| `time_flow[i]` | Integer | Flow time (start to completion) for order `i` |
| `wip_indicator[i,t]` | Binary | Order `i` is in process at time `t` |
| `wip[t]` | Integer | Number of orders in process at time `t` |
| `wip_weighted[t]` | Integer | Value-weighted WIP at time `t` |

### Parameters

#### Processing Parameters

| Parameter | Description |
|-----------|-------------|
| `p[i,j]` | Processing time for order `i` on line `j` |
| `s[i,k,j]` | Setup time between orders `i` and `k` on line `j` |

#### Resource Parameters

| Parameter | Description |
|-----------|-------------|
| `a[w,t]` | Worker `w` availability at time `t` (binary) |
| `alpha` | Reserved capacity fraction (e.g., 0.1 = 10%) |

#### Inventory Parameters

| Parameter | Description |
|-----------|-------------|
| `inv0[i]` | Initial inventory for order `i` |
| `ship[i,t]` | Shipping schedule for order `i` at time `t` |

#### OTIF Parameters

| Parameter | Description |
|-----------|-------------|
| `due[i]` | Due date for order `i` |
| `demand[i]` | Required quantity for order `i` |
| `priority[i]` | Priority weight for order `i` |

#### Workforce Parameters

| Parameter | Description |
|-----------|-------------|
| `workforce_target` | Ideal steady-state workforce level |

### Constraints

#### 1. Assignment Constraints

**One Assignment per Order:**
```
∑_j ∑_t ∑_w x[i,j,t,w] = 1    ∀i
```
Each order must be assigned to exactly one line, one time, and one worker.

#### 2. Capacity Constraints

**Line Capacity (No Overlap):**
```
∑_i ∑_w ∑_(t≤τ<t+p[i,j]+setup) x[i,j,t,w] ≤ u[j]    ∀j, ∀τ
```
Prevents multiple orders from overlapping on the same line.

**Reserved Line Capacity:**
```
∑_i ∑_j ∑_τ ∑_w ∑_(t≤τ<t+p[i,j]) x[i,j,t,w] ≤ (1-α) × m × T
```
Reserves a fraction `α` of total capacity.

**Reserved Worker Capacity:**
```
∑_w ∑_t w_working[w,t] ≤ (1-α) × ∑_w ∑_t a[w,t]
```
Reserves a fraction `α` of worker capacity.

#### 3. Worker Constraints

**Worker Working Indicator:**
```
∑_i ∑_j ∑_(t≤τ<t+p[i,j]) x[i,j,t,w] = w_working[w,τ]    ∀τ, ∀w
```
Links assignment variables to worker working status.

**Worker Availability:**
```
w_working[w,t] ≤ a[w,t]    ∀w, ∀t
```
Workers can only work when available.

**Worker Movement Tracking (Problem_3):**
```
m[w,t] ≥ ∑_i (x[i,j,w,t] - x[i,j,w,t-1])    ∀w, ∀j, ∀t>1
```
Tracks when a worker switches from one line to another between consecutive time periods. The movement indicator `m[w,t]` becomes 1 when worker `w` moves to a different line at time `t`.

#### 4. OTIF Constraints

**Start Time Calculation:**
```
time_start[i] = ∑_j ∑_w ∑_t t × x[i,j,t,w]    ∀i
```

**Completion Time Calculation:**
```
time_completion[i] = ∑_j ∑_w ∑_t (t + p[i,j]) × x[i,j,t,w]    ∀i
```

**Lateness Calculation:**
```
lateness[i] ≥ time_completion[i] - due[i]    ∀i
lateness[i] ≥ 0    ∀i
```

**Earliness Calculation:**
```
early[i] ≥ due[i] - time_completion[i]    ∀i
early[i] ≥ 0    ∀i
```

**Late Order Indicator:**
```
lateness[i] ≤ T × late[i]    ∀i
time_completion[i] ≥ due[i] - T(1 - late[i])    ∀i
```

#### 5. WIP Constraints

**Flow Time:**
```
time_flow[i] = ship[i] - time_start[i]    ∀i
```

**Production Calculation:**
```
prod[i,t] = ∑_j ∑_w x[i,j,t-p[i,j],w]    ∀i,∀t
```

**Inventory Balance:**
```
inv[i,t] = inv[i,t-1] + prod[i,t] - ship[i,t]    ∀i, ∀t>0
inv[i,0] = inv0[i]    ∀i
```

**WIP Count:**
```
wip[t] = ∑_i wip_indicator[i,t]    ∀t
```

#### 6. Workforce Constraints

**Active Workers:**
```
workers_used[t] = ∑_w w_working[w,t]    ∀t
```

**Min/Max Tracking:**
```
workers_max ≥ workers_used[t]    ∀t
workers_used[t] ≥ workers_min    ∀t
```

**Deviation from Target:**
```
workers_used[t] = workforce_target + deviation_above[t] - deviation_below[t]    ∀t
```

**Workforce Changes:**
```
workers_used[t] = workers_used[t-1] + workforce_increase[t] - workforce_decrease[t]    ∀t>1
workforce_change[t] = workforce_increase[t] + workforce_decrease[t]    ∀t>1
```

### Objective Function

The objective is to minimize a weighted sum of five terms:

```
minimize: α×OTIF + β×WIP + γ×Workforce + δ×LineUtil + ω×WorkerMove
```

**OTIF Term:**
```
OTIF = ∑_i priority[i] × (7×late[i] + 3×lateness[i])
```
Heavily penalizes late orders, with additional penalty proportional to lateness.

**WIP Term:**
```
WIP = 4×∑_t wip[t] + 6×∑_i time_flow[i]
```
Minimizes work-in-progress and flow times.

**Workforce Term:**
```
Workforce = 5×(workers_max - workers_min) + 3×∑_t(deviation_above[t] + deviation_below[t]) + 2×∑_t workforce_change[t]
```
Reduces worker variance, deviations from target, and changes between periods.

**Line Utilization Term:**
```
LineUtil = ∑_j u[j]
```
Minimizes the number of lines used.

**Worker Movement Term (Problem_3):**
```
WorkerMove = ∑_w ∑_t m[w,t]
```
Penalizes workers switching between production lines. This helps reduce setup overhead and improves production efficiency by encouraging workers to stay on the same line when possible.

---

## Code Structure

The implementation is organized into modular components for easy extension:

### File Organization

```
packing-schedule-example/
├── packing_model/                    # Main model package (MODULAR)
│   ├── __init__.py                  # Package initialization
│   ├── model.py                      # Main coordinator class
│   ├── parameters.py                 # Input parameter definitions
│   ├── variables.py                  # Decision variable definitions
│   ├── objective.py                  # Objective function
│   └── constraints/                  # Constraints by category
│       ├── __init__.py
│       ├── assignment.py             # Order assignment
│       ├── capacity.py               # Line capacity
│       ├── worker.py                 # Worker availability
│       ├── otif.py                   # OTIF tracking
│       ├── wip.py                    # WIP tracking
│       └── workforce.py              # Workforce management
├── packing_schedule_model.py         # Old monolithic version (deprecated)
├── example.py                        # Usage examples
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── ARCHITECTURE.md                   # Architecture documentation
├── QUICK_REFERENCE.md                # Quick reference guide
└── FIXES_APPLIED.md                  # Bug fix documentation
```

### Model Class Structure

```python
# Main entry point
from packing_model import PackingScheduleModel

class PackingScheduleModel:
    def __init__(self, data)           # Initialize complete model
    def solve()                        # Solve the model
    def get_solution()                 # Extract solution
    def print_solution_summary()       # Display results
    def export_solution(filename)      # Export detailed solution
```

### Modular Components

The model is organized into separate modules for easy extension:

| Component | Module | Purpose |
|-----------|--------|---------|
| Parameters | `parameters.py` | All input data definitions |
| Variables | `variables.py` | All decision variables |
| Objective | `objective.py` | Objective function components |
| Constraints | `constraints/*.py` | Constraints organized by category |

### How Constraints Map to Code

Each constraint group has its own module:

| Formulation Section | Module File | Key Constraints |
|---------------------|-------------|-----------------|
| One assignment | `constraints/assignment.py` | `one_assignment` |
| Line capacity | `constraints/capacity.py` | `line_capacity`, `reserved_line_capacity` |
| Worker availability | `constraints/worker.py` | `worker_working`, `worker_availability` |
| OTIF tracking | `constraints/otif.py` | `start_time`, `completion_time`, `lateness_*` |
| WIP tracking | `constraints/wip.py` | `production`, `inventory_balance`, `wip_count` |
| Workforce management | `constraints/workforce.py` | `workers_used_calc`, `workforce_deviation` |
| Objective function | `objective.py` | `_otif_term`, `_wip_term`, `_workforce_term` |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation on the modular structure.

---

## Usage Guide

### Basic Usage

```python
from packing_model import PackingScheduleModel
import numpy as np

# 1. Prepare your data
data = {
    'n_orders': 5,
    'n_lines': 3,
    'n_timeslots': 20,
    'n_workers': 4,
    'processing_time': np.array([[3, 4, 5], ...]),
    'setup_time': np.ones((5, 5, 3)),
    'worker_availability': np.ones((4, 20)),
    'initial_inventory': np.zeros(5),
    'shipping_schedule': np.zeros((5, 20)),
    'reserved_capacity': 0.1,
    'due_date': np.array([10, 12, 8, 15, 18]),
    'demand': np.array([100, 150, 80, 200, 120]),
    'priority': np.array([80, 90, 70, 95, 85]),
    'workforce_target': 2,
    'objective_weights': {
        'alpha': 1.0,
        'beta': 0.5,
        'gamma': 0.3,
        'delta': 0.2
    }
}

# 2. Create model
model = PackingScheduleModel(data)

# 3. Solve
results = model.solve(solver_name='appsi_highs', tee=False)

# 4. Get solution
if results['objective_value'] is not None:
    solution = model.get_solution()
    model.print_solution_summary()
```

### Customizing Solver Options

```python
# Solve with custom time limit and gap tolerance
results = model.solve(
    solver_name='appsi_highs',
    tee=True,  # Show solver output
    time_limit=600,  # 10 minutes
    mip_rel_gap=0.01  # 1% optimality gap
)
```

### Extracting Specific Solution Data

```python
solution = model.get_solution()

# Get order assignments
for assignment in solution['assignments']:
    print(f"Order {assignment['order']} on Line {assignment['line']}")

# Get OTIF metrics
for order_id, metrics in solution['otif_metrics'].items():
    if metrics['late']:
        print(f"Order {order_id} is late by {metrics['lateness']} time units")

# Get workforce usage over time
for time, metrics in solution['workforce_metrics'].items():
    print(f"Time {time}: {metrics['workers_used']} workers")
```

---

## Extending the Model

### Adding New Variables

To add a new decision variable:

1. **Define the variable** in `_define_variables()`:

```python
model.my_new_var = pyo.Var(model.ORDERS, model.TIME,
                           domain=pyo.Binary,
                           doc="Description of new variable")
```

2. **Add constraints** using the new variable in a new method:

```python
def _add_my_new_constraints(self):
    model = self.model

    def my_constraint_rule(m, i, t):
        return m.my_new_var[i, t] <= some_expression

    model.my_constraint = pyo.Constraint(model.ORDERS, model.TIME,
                                        rule=my_constraint_rule)
```

3. **Call the method** in `_define_constraints()`:

```python
def _define_constraints(self):
    # ... existing methods ...
    self._add_my_new_constraints()
```

### Adding New Parameters

To add a new input parameter:

1. **Add to data dictionary** in your script:

```python
data['my_parameter'] = np.array([...])
```

2. **Define in model** in `_define_parameters()`:

```python
model.my_param = pyo.Param(model.ORDERS,
                          initialize=lambda m, i: data['my_parameter'][i-1])
```

### Adding New Objective Terms

To add a new term to the objective:

1. **Define the expression** in `_define_objective()`:

```python
def my_new_objective_term(m):
    return sum(m.my_new_var[i, t] for i in m.ORDERS for t in m.TIME)
```

2. **Add to combined objective**:

```python
def objective_rule(m):
    return (weights['alpha'] * otif_expr(m) +
           weights['beta'] * wip_expr(m) +
           weights['gamma'] * workforce_expr(m) +
           weights['delta'] * line_util_expr(m) +
           weights['epsilon'] * my_new_objective_term(m))  # New term
```

3. **Add weight to data**:

```python
data['objective_weights']['epsilon'] = 0.1
```

### Adding New Constraints

Example: Add a constraint limiting total processing on a specific line:

```python
def _add_line_limit_constraints(self):
    model = self.model

    def line_1_limit_rule(m):
        return sum(m.x[i, 1, t, w] * m.p[i, 1]
                  for i in m.ORDERS
                  for t in m.TIME
                  for w in m.WORKERS) <= 50

    model.line_1_limit = pyo.Constraint(rule=line_1_limit_rule,
                                       doc="Limit line 1 usage")
```

---

## Troubleshooting

### Common Issues

**1. Solver not found error:**
```
ERROR: Solver (appsi_highs) is not available
```
**Solution:** Install HiGHS solver:
```bash
pip install highspy
```

**2. Infeasible model:**
```
Termination condition: infeasible
```
**Solution:** Check that:
- Processing times fit within time horizon
- Workers are available when needed
- Due dates are achievable
- Reserved capacity is not too high

**3. Memory errors with large problems:**
**Solution:**
- Reduce problem size (fewer orders/timeslots)
- Use time limit and accept near-optimal solution
- Consider problem decomposition

### Getting Help

- Check example.py for working code
- Review constraint formulations in this README
- Ensure data dimensions match (orders, lines, timeslots, workers)

---

## Performance Tips

1. **Start small**: Test with small problem instances first
2. **Set time limits**: Use `time_limit` parameter to avoid long solve times
3. **Accept good solutions**: Use `mip_rel_gap` to stop at near-optimal solutions
4. **Profile constraints**: Comment out constraint groups to identify bottlenecks
5. **Use sparse data**: Leverage numpy arrays efficiently

---

## References

- [Pyomo Documentation](https://pyomo.readthedocs.io/)
- [HiGHS Solver](https://highs.dev/)
- Problem formulation: See Problem_1.pdf

---

## License

This project is provided as-is for educational and commercial use.

---

## Authors

Generated for packing schedule optimization demonstration.

---

*Last updated: 2025*
