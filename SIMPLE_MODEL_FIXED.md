# Simple Model (Problem 4.1) - Issue Resolution

## Problem
The `simple_model_example.py` script was failing with errors related to Pyomo constraint formulation.

## Issues Fixed

### 1. **Pyomo Variable in Boolean Context**
**Location**: `constraints/capacity.py`, `constraints/worker.py`, `constraints/wip.py`

**Problem**: Constraints were using Python `if` statements with Pyomo expressions containing variables, which isn't allowed.

**Solution**: Reformulated constraints to pre-compute valid indices using parameter values (`pyo.value()`), then build sums over those valid indices.

**Example**:
```python
# BEFORE (incorrect):
def line_capacity_rule(m, j, tau):
    return sum(m.x[i, j, t, w]
              for i in m.ORDERS
              for w in m.WORKERS
              for t in m.TIME
              if t <= tau < t + m.p[i, j]  # ERROR: can't evaluate m.p[i,j] in boolean context
              ) <= m.u[j]

# AFTER (correct):
def line_capacity_rule(m, j, tau):
    active_orders = []
    for i in m.ORDERS:
        for w in m.WORKERS:
            for t in m.TIME:
                if t <= tau and tau < t + pyo.value(m.p[i, j]):  # Use pyo.value()
                    active_orders.append(m.x[i, j, t, w])
    if active_orders:
        return sum(active_orders) <= m.u[j]
    else:
        return pyo.Constraint.Skip
```

### 2. **Strict Inequality in Constraints**
**Location**: `constraints/worker.py`, `constraints/otif.py`

**Problem**: Pyomo doesn't support strict inequalities (`<` or `>`). All constraints must use `<=`, `>=`, or `==`.

**Solution**: Changed `<` to `<=` and `>` to `>=` (with small epsilon where needed).

**Examples**:
```python
# BEFORE:
return sum(...) < (1 - m.alpha) * total  # ERROR: strict inequality

# AFTER:
return sum(...) <= (1 - m.alpha) * total  # OK

# For "greater than":
# BEFORE:
return m.time_completion[i] > m.due[i] - T * (1 - m.late[i])  # ERROR

# AFTER:
return m.time_completion[i] >= m.due[i] - T * (1 - m.late[i]) + 0.01  # OK
```

### 3. **Wrong Index Order**
**Location**: `constraints/worker.py` - `movement_balance_rule`

**Problem**: Variable `x` is indexed as `x[i, j, t, w]` but constraint was using `x[i, j, w, t]`.

**Solution**: Fixed index order to match variable definition.

```python
# BEFORE:
return m.m[w, t] >= sum(m.x[i, j, w, t] - m.x[i, j, w, t-1]  # ERROR: wrong order
                         for i in m.ORDERS)

# AFTER:
return m.m[w, t] >= sum(m.x[i, j, t, w] - m.x[i, j, t-1, w]  # CORRECT
                         for i in m.ORDERS)
```

### 4. **File Location**
**Problem**: `simple_model_example.py` was inside the `simple_model/` directory, causing import conflicts.

**Solution**: Moved to parent directory where it can properly import from `simple_model` package.

## Files Modified

1. [simple_model/constraints/capacity.py](simple_model/constraints/capacity.py) - Fixed 3 constraint rules
2. [simple_model/constraints/worker.py](simple_model/constraints/worker.py) - Fixed 2 constraint rules + index order
3. [simple_model/constraints/wip.py](simple_model/constraints/wip.py) - Fixed 2 constraint rules
4. [simple_model/constraints/otif.py](simple_model/constraints/otif.py) - Fixed strict inequality
5. [simple_model_example.py](simple_model_example.py) - Moved to correct location

## Test Results

After fixes, the example runs successfully:

```
================================================================================
Simple Packing Schedule Model - Problem 4.1 Example
================================================================================

Problem size: 3 orders, 2 lines, 20 time slots, 3 workers

Model built successfully!

Solving optimization problem...
Optimal solution found!
Objective value: 75.40

SOLUTION SUMMARY - Problem 4.1
================================================================================

--- ORDER ASSIGNMENTS ---
Order  1 -> Line  1 | Start: t=  7 | Complete: t= 10 | Worker:  2
Order  2 -> Line  1 | Start: t=  1 | Complete: t=  3 | Worker:  3
Order  3 -> Line  1 | Start: t=  7 | Complete: t=  7 | Worker:  3

--- OTIF PERFORMANCE ---
On-Time Rate: 100.0% (3/3 orders)
Late Orders: 0

--- WORKFORCE UTILIZATION ---
Average Workers: 0.5
Peak Workers: 1
Min Workers: 0

--- LINE UTILIZATION ---
Line  1: USED
Line  2: UNUSED
```

**Solve Time**: ~0.4 seconds
**Status**: Optimal solution found

## Key Learnings

### Pyomo Constraint Rules Best Practices

1. **Never use variables in Python conditionals**: Parameters can be evaluated with `pyo.value()`, but variables cannot.

2. **Pre-filter indices using parameters**: Build lists of valid terms before creating the sum expression.

3. **Use non-strict inequalities**: Always use `<=`, `>=`, or `==`, never `<` or `>`.

4. **Check variable index order**: Ensure indices match the variable definition exactly.

5. **Use `pyo.Constraint.Skip`**: When a constraint is not applicable for certain index combinations, return `Skip` rather than trying to create an empty constraint.

## Usage

To run the fixed example:

```bash
cd c:\Projects\packing-schedule-example\packing-schedule-example
python simple_model_example.py
```

The model will:
1. Create a 3-order, 2-line problem
2. Build the optimization model (all constraints from Problem_4_1.pdf)
3. Solve using HiGHS solver
4. Display solution summary
5. Export detailed solution to `simple_model_solution.txt`
6. Write LP file to `simple_model_example.lp`

## Status

✅ **RESOLVED** - The simple_model implementation is now fully functional and produces optimal solutions.
