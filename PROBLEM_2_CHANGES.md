# Problem 2 Implementation - Changes Summary

This document describes the modifications made to convert the Problem 1 implementation to Problem 2.

## Overview

Problem 2 introduces **flexible shipping decisions** instead of the fixed shipping schedule from Problem 1. The key change is that `ship[i,t]` transitions from an input parameter to a **decision variable**, allowing the optimizer to decide when each order should ship.

---

## Key Differences Between Problem 1 and Problem 2

### Parameters (Removed)
1. **`ship[i,t]`** - No longer a fixed parameter; now a decision variable
2. **`demand[i]`** - Removed (not needed in Problem 2)

### Decision Variables (Added)
1. **`ship[i,t]`** - Binary decision: order i ships at time t
2. **`time_ship[i]`** - Integer: time slot when order i ships
3. **`ship_early[i]`** - Binary: order i ships before due date
4. **`ship_late[i]`** - Binary: order i ships after due date

### Constraints (Added)
New shipping-related constraints ensure valid shipping decisions:
- Each order ships exactly once
- Shipping time calculation
- Cannot ship before order completion
- Determine if order ships early or late

### Constraints (Modified)
- **Flow time calculation**: Now uses `time_ship[i]` variable instead of summing `ship[i,t] * t`

---

## Files Modified

### 1. `packing_model/parameters.py`
**Changes:**
- Removed `ship` parameter from `_define_inventory_parameters()` method (lines 89-94)
- Removed `demand` parameter from `_define_otif_parameters()` method (lines 108-113)

**Before:**
```python
model.ship = pyo.Param(
    model.ORDERS, model.TIME,
    initialize=lambda m, i, t: data['shipping_schedule'][i-1, t-1],
    doc="Shipping schedule for order i at time t"
)

model.demand = pyo.Param(
    model.ORDERS,
    initialize=lambda m, i: data['demand'][i-1],
    doc="Required quantity for order i"
)
```

**After:**
Both parameters removed (now decision variables).

---

### 2. `packing_model/variables.py`
**Changes:**
- Added new method `_define_shipping_variables()`
- Added `time_ship[i]` to WIP variables
- Updated `time_flow[i]` documentation to reflect shipping time
- Called `_define_shipping_variables()` in `define_all_variables()`

**New Variables Added:**
```python
# In _define_wip_variables():
model.time_ship = pyo.Var(
    model.ORDERS,
    domain=pyo.NonNegativeIntegers,
    bounds=(1, self.data['n_timeslots']),
    doc="Shipping time for order i"
)

# In _define_shipping_variables():
model.ship = pyo.Var(
    model.ORDERS, model.TIME,
    domain=pyo.Binary,
    doc="Order i ships at time t (binary decision)"
)

model.ship_early = pyo.Var(
    model.ORDERS,
    domain=pyo.Binary,
    doc="Order i ships before due date"
)

model.ship_late = pyo.Var(
    model.ORDERS,
    domain=pyo.Binary,
    doc="Order i ships after due date"
)
```

---

### 3. `packing_model/constraints/shipping.py` (NEW FILE)
**Purpose:** Define all shipping-related constraints

**Constraints Implemented:**
1. **ship_once**: Each order ships exactly once
   ```python
   sum(m.ship[i, t] for t in m.TIME) == 1
   ```

2. **shipping_time_calc**: Calculate shipping time from binary decisions
   ```python
   m.time_ship[i] == sum(t * m.ship[i, t] for t in m.TIME)
   ```

3. **ship_after_completion**: Cannot ship before production completes
   ```python
   m.time_ship[i] >= m.time_completion[i]
   ```

4. **ship_early_ind_1 & ship_early_ind_2**: Determine if order ships early
   ```python
   # Early indicator (Big-M formulation)
   m.time_ship[i] <= m.due[i] + BIG_M * (1 - m.ship_early[i])
   m.time_ship[i] >= m.due[i] - BIG_M * m.ship_early[i]
   ```

5. **ship_late_ind_1 & ship_late_ind_2**: Determine if order ships late
   ```python
   # Late indicator (Big-M formulation)
   m.time_ship[i] >= m.due[i] + 1 - BIG_M * (1 - m.ship_late[i])
   m.time_ship[i] <= m.due[i] + BIG_M * m.ship_late[i]
   ```

6. **ship_timing_status**: Order is either early, on-time, or late
   ```python
   m.ship_early[i] + m.ship_late[i] <= 1
   ```

---

### 4. `packing_model/constraints/__init__.py`
**Changes:**
- Added import: `from .shipping import add_shipping_constraints`
- Added function call: `add_shipping_constraints(model, data)` in `add_all_constraints()`

---

### 5. `packing_model/constraints/wip.py`
**Changes:**
- Modified `flow_time_rule()` to use `time_ship` variable

**Before:**
```python
def flow_time_rule(m, i):
    return m.time_flow[i] == sum(
        m.ship[i, t] * t for t in m.TIME
    ) - m.time_start[i]
```

**After:**
```python
def flow_time_rule(m, i):
    return m.time_flow[i] == m.time_ship[i] - m.time_start[i]
```

---

### 6. `example.py`
**Changes:**
- Removed `shipping_schedule` data creation (lines 57-63)
- Removed `demand` data creation (lines 71-72)
- Removed these fields from both `create_sample_data()` and `create_small_example()` dictionaries

**Before:**
```python
shipping_schedule = np.zeros((n_orders, n_timeslots), dtype=int)
shipping_schedule[0, 10] = 1  # Order 1 ships at time 10
# ...

demand = np.array([100, 150, 80, 200, 120])

data = {
    # ...
    'shipping_schedule': shipping_schedule,
    'demand': demand,
    # ...
}
```

**After:**
```python
# Both shipping_schedule and demand removed entirely
data = {
    # ... other fields without shipping_schedule and demand
}
```

---

## Model Statistics

### Problem 1 (Original)
- Variables: 1,955
- Constraints: 716
- Objective Value: 91.30

### Problem 2 (Modified)
- Variables: 2,070 (+115 variables for shipping decisions)
- Constraints: 756 (+40 constraints for shipping logic)
- Objective Value: 70.00 (improved due to flexible shipping)

---

## Testing Results

```bash
$ python example.py
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
  - Number of variables: 2070
  - Number of constraints: 756

[Step 3] Solving the optimization problem...
  - Using HiGHS solver
Starting optimization...

Optimal solution found!
Objective value: 70.00

--- ORDER ASSIGNMENTS ---
Order  1 -> Line  1 | Start: t=  3 | Complete: t=  6 | Worker:  2
Order  2 -> Line  2 | Start: t=  6 | Complete: t=  9 | Worker:  3
Order  3 -> Line  1 | Start: t=  1 | Complete: t=  3 | Worker:  2
Order  4 -> Line  2 | Start: t=  9 | Complete: t= 13 | Worker:  4
Order  5 -> Line  2 | Start: t= 13 | Complete: t= 16 | Worker:  4

--- OTIF PERFORMANCE ---
On-Time Rate: 100.0% (5/5 orders)
Late Orders: 0

--- WORKFORCE UTILIZATION ---
Average Workers: 0.8
Peak Workers: 1
Min Workers: 0

--- LINE UTILIZATION ---
Line  1: USED
Line  2: USED
Line  3: UNUSED
```

✅ **Status**: Problem 2 implementation complete and tested successfully!

---

## Implementation Notes

### Design Decisions

1. **Big-M Formulation**: Used for indicator constraints (early/late shipping) with `BIG_M = n_timeslots * 1000`

2. **Inventory Availability**: Initially considered adding `has_inv[i,t]` variable and constraints, but removed it as the inventory balance equations naturally enforce shipping feasibility.

3. **Modular Structure**: Maintained the modular architecture with shipping constraints in a separate module for easy maintenance.

### Backward Compatibility

The old Problem 1 implementation is preserved in `packing_schedule_model.py` (monolithic version). To use:
- Problem 1: Use old monolithic file
- Problem 2: Use new modular `packing_model` package (current default)

---

## Future Enhancements

Potential improvements to Problem 2 implementation:

1. **Shipping Costs**: Add cost structure for early/late shipping
2. **Inventory Holding Costs**: Penalize excess inventory
3. **Batch Shipping**: Allow multiple orders to ship together
4. **Shipping Capacity**: Add constraints on total shipping capacity per time slot
5. **Multi-objective**: Separate OTIF based on completion vs. shipping time

---

**Implemented by**: Claude Code Assistant
**Date**: 2025
**Status**: ✅ Complete and Tested
**Test Result**: Optimal solution found (objective = 70.00, 100% on-time)
