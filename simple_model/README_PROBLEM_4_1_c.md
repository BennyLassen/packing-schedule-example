# Problem 4.1_c Implementation (LP Relaxation)

This directory contains the **LP-relaxed** version of the Problem 4.1 MILP formulation as specified in `Problem_4_1_c.pdf`.

## Key Differences from Problem_4_1

The Problem_4_1_c formulation is an **LP relaxation** where several integer variables have been converted to continuous (real) variables:

### Variables Relaxed from Integer to Real

| Variable | Problem_4_1 (Original) | Problem_4_1_c (Relaxed) |
|----------|----------------------|------------------------|
| `prod(i,t)` | Positive Integer | **Non-negative Real** |
| `workersused(t)` | Integer [0,W] | **Real [0,W]** |
| `workersmax` | Integer [0,W] | **Real [0,W]** |
| `workersmin` | Integer [0,W] | **Real [0,W]** |
| `inv(i,t)` | Positive Integer | **Non-negative Real** |

Binary variables (`x(i,j,t)` and `ship(i,t)`) remain **unchanged**.

### Updated Shipping Constraint

The shipping constraint has been reformulated (Problem_4_1_c Page 7):

**Original (Problem_4_1):**
```
ship(i,t) = 0  for all t < due(i)
```

**New (Problem_4_1_c):**
```
∑_t t * ship(i,t) ≥ due(i)  ∀i
```

This new formulation is more flexible and works better with LP relaxation.

## Why LP Relaxation?

**Benefits:**
1. **Faster solving**: LP problems solve much faster than MILP
2. **Provides bounds**: LP relaxation gives a lower bound on the optimal MILP objective
3. **Large-scale problems**: Makes larger problem instances tractable
4. **Analysis**: Useful for understanding problem structure

**Trade-offs:**
- Non-integer solutions may not be directly implementable
- May need post-processing (rounding, fixing) for practical use
- Can be used as part of branch-and-bound or cutting plane algorithms

## Directory Structure

```
packing_model_problem_4_1_c/    # LP-relaxed implementation
├── __init__.py                  # Package exports
├── model.py                     # Main model class (PackingScheduleModelProblem41c)
├── parameters.py                # Parameters (unchanged from 4_1)
├── variables.py                 # Variables with RELAXED domains
├── objective.py                 # Objective function (unchanged)
└── constraints/                 # Constraint modules
    ├── __init__.py
    ├── assignment.py            # Same as 4_1
    ├── capacity.py              # Same as 4_1
    ├── shipping.py              # UPDATED shipping constraint
    ├── otif.py                  # Same as 4_1
    ├── wip.py                   # Same as 4_1
    └── workforce.py             # Same as 4_1
```

## Usage

```python
from packing_model_problem_4_1_c import PackingScheduleModelProblem41c
import numpy as np

# Define problem data (same format as Problem_4_1)
data = {
    'n_orders': 10,
    'n_lines': 2,
    'n_timeslots': 96,
    'n_workers': 5,
    'processing_time': np.array([[4, 5], [3, 4], ...]),
    'initial_inventory': np.array([0, 0, ...]),
    'reserved_capacity': 0.1,
    'due_date': np.array([10, 20, ...]),
    'priority': np.array([1, 1, ...]),
    'objective_weights': {'beta': 1.0, 'gamma': 0.5, 'delta': 0.3}
}

# Create and solve model (note the different class name)
model = PackingScheduleModelProblem41c(data)
results = model.solve(solver_name='appsi_highs')

# View results
if results['objective_value'] is not None:
    model.print_solution_summary()
```

## Comparison with Problem_4_1

| Aspect | Problem_4_1 | Problem_4_1_c |
|--------|------------|---------------|
| Problem Type | MILP | Mixed Integer LP (closer to LP) |
| Integer Variables | 5 types | 0 types (all relaxed) |
| Binary Variables | 2 types | 2 types (unchanged) |
| Shipping Constraint | Time-based | Weighted sum |
| Solution Time | Slower | **Faster** |
| Solution Nature | Integer | **May be fractional** |
| Use Case | Exact scheduling | Bounds, large-scale, analysis |

## Implementation Files

### Modified Files (from Problem_4_1)

1. **variables.py**: Changed variable domains from `pyo.NonNegativeIntegers` to `pyo.NonNegativeReals`
   ```python
   # Before (Problem_4_1):
   model.prod = pyo.Var(domain=pyo.NonNegativeIntegers)

   # After (Problem_4_1_c):
   model.prod = pyo.Var(domain=pyo.NonNegativeReals)
   ```

2. **constraints/shipping.py**: Updated shipping constraint formulation
   ```python
   # Before (Problem_4_1):
   if t < m.due[i]:
       return m.ship[i, t] == 0

   # After (Problem_4_1_c):
   return sum(t * m.ship[i, t] for t in m.TIME) >= m.due[i]
   ```

3. **model.py**: Updated class name and documentation

4. **__init__.py**: Updated export to use new class name

### Unchanged Files

- `parameters.py`: Same as Problem_4_1
- `objective.py`: Same as Problem_4_1
- `constraints/assignment.py`: Same as Problem_4_1
- `constraints/capacity.py`: Same as Problem_4_1
- `constraints/otif.py`: Same as Problem_4_1
- `constraints/wip.py`: Same as Problem_4_1
- `constraints/workforce.py`: Same as Problem_4_1

## When to Use Problem_4_1_c vs Problem_4_1

### Use Problem_4_1_c (LP Relaxation) when:
- You need **faster solve times** for large problems
- You want a **lower bound** on the optimal objective
- You're doing **sensitivity analysis** or parametric studies
- The problem is **too large** for exact MILP solution
- You'll round/post-process the solution anyway
- You're using it in a **decomposition algorithm**

### Use Problem_4_1 (Full MILP) when:
- You need **exact integer solutions**
- The problem size is **manageable** (< 10,000 variables)
- **Fractional values are not acceptable** in the solution
- You need the **true optimal** solution
- Implementation requires **precise quantities**

## Performance Expectations

For typical problem sizes:

| Problem Size | Problem_4_1 (MILP) | Problem_4_1_c (LP Relaxation) |
|--------------|-------------------|------------------------------|
| Small (10 orders, 2 lines, 96 slots) | < 1 minute | **< 10 seconds** |
| Medium (50 orders, 5 lines, 96 slots) | 5-15 minutes | **< 1 minute** |
| Large (200 orders, 10 lines, 96 slots) | 30+ minutes | **< 5 minutes** |

## Solution Interpretation

Since variables are relaxed to real:

- **prod(i,t)**: May be fractional (e.g., 2.5 units produced)
  - *Interpretation*: Partial completion of an order at time t

- **workersused(t)**: May be fractional (e.g., 3.7 workers)
  - *Interpretation*: Average worker utilization or fractional worker time

- **inv(i,t)**: May be fractional (e.g., 1.3 units in inventory)
  - *Interpretation*: Partial units in stock

### Post-Processing Options

1. **Rounding**: Round fractional values to nearest integer
2. **Fixing**: Fix binary variables and resolve as LP
3. **Branch-and-bound**: Use LP relaxation as bound in exact algorithm
4. **Feasibility repair**: Adjust rounded solution to satisfy constraints

## Notes

- The LP relaxation typically provides a **good approximation** of the MILP solution
- **Objective value** of LP relaxation is a **lower bound** for minimization problems
- If LP relaxation gives integer solution, it's **provably optimal** for the MILP
- **Integrality gap** = (MILP objective - LP objective) / LP objective

## References

- **Problem_4_1_c.pdf**: Full specification with LP relaxation
- **Problem_4_1.pdf**: Original MILP formulation
- **README_PROBLEM_4_1.md**: Documentation for original version

## License

Part of the packing schedule optimization project.
