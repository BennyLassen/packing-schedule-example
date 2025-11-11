# Correction Notes for Problem 4.1 c2 Implementation

## Date: 2025-11-11

## Update 4 (Latest - prodorder Assignment Requirement)
Updated prodorder constraint to require that orders must be assigned to a line, based on the corrected PDF Page 6 specification.

## Update 3 (OTIF Implementation)
Added OTIF (On-Time In-Full) variables, constraints, and objective term based on the updated PDF specification.

## Update 2
Added the `shipped(d1,d)` binary variable and updated inventory balance constraint to use it, based on the corrected PDF specification (Page 7).

## Update 1
Initial correction to remove the `d' ≤ d` condition from the inventory balance equation.

## Summary
1. **Update 4**: Updated prodorder constraint to require order assignment to a line
2. **Update 3**: Added OTIF (On-Time In-Full) variables, constraints, and objective term to track delivery performance
3. **Update 2**: Updated the inventory balance constraint and added shipped timing constraints
4. **Update 1**: Initial correction to remove the `d' ≤ d` condition from the inventory balance equation

## Changes Made

### Update 4: prodorder Assignment Requirement

#### Issue:
The prodorder constraint in the original implementation only enforced timing (completion before shipping) but did not require that an order be assigned to a production line. This meant that orders could be counted as "produced before demand d" even if they weren't actually assigned to any line.

#### Updated PDF Specification (Page 6):
```
prodorder(i,d) = 1 ⇒ [c(i) ≤ ship(d) ∧ x(i,j) = 1]
```

The key addition is `∧ x(i,j) = 1`, which means the order must be assigned to at least one line.

#### Implementation:

**Location:** [simple_model/packing_model_problem_4_1_c2/constraints/shipping.py](packing_model_problem_4_1_c2/constraints/shipping.py)

**New Constraint:**
```python
def order_assignment_required_rule(m, i, d):
    """
    If order i is produced before demand d, it must be assigned to a line.

    [prodorder(i,d) = 1] ⇒ [c(i) ≤ ship(d) ∧ x(i,j) = 1]

    The assignment part is reformulated as:
    ∑_j x(i,j) ≥ prodorder(i,d)

    This ensures that if prodorder(i,d) = 1, then the order must be assigned
    to at least one line. If prodorder(i,d) = 0, this constraint is trivially satisfied.
    """
    return sum(m.x[i, j] for j in m.LINES) >= m.prodorder[i, d]

model.order_assignment_required = pyo.Constraint(
    model.ORDERS, model.DEMANDS,
    rule=order_assignment_required_rule,
    doc="If order produced before demand, it must be assigned to a line"
)
```

#### Impact:
Before this update, the model could find "solutions" where no orders were assigned to lines (all x(i,j) = 0). After this update, the model correctly assigns orders to lines, ensuring that production actually happens on the production lines.

**Test Results:**
- Standard example solves to optimal with objective value: 4.00
- All 4 orders now properly assigned to lines
- Both demands delivered ON-TIME
- Inventory properly tracked through production and shipping

### Update 3: OTIF Implementation

#### 1. Added OTIF Variables (variables.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/variables.py](packing_model_problem_4_1_c2/variables.py)

**New Variables (from PDF Page 2 & 5):**
```python
# lateness(d): Lateness of demand d (ship_time - due_date if late, else 0)
model.lateness = pyo.Var(
    model.DEMANDS,
    domain=pyo.NonNegativeReals,
    doc="Lateness of demand d (ship_time - due_date if late, else 0)"
)

# late(d): Binary indicator for late demand (1 if late, 0 if on-time)
model.late = pyo.Var(
    model.DEMANDS,
    domain=pyo.Binary,
    doc="Binary indicator: 1 if demand d is late, 0 if on-time"
)
```

#### 2. Created OTIF Constraints File (constraints/otif.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/constraints/otif.py](packing_model_problem_4_1_c2/constraints/otif.py)

**New Constraints (from PDF Page 5):**

**Lateness Calculation:**
```python
# lateness(d) ≥ ship(d) - due(d)  ∀d
def lateness_calculation_rule(m, d):
    return m.lateness[d] >= m.ship[d] - m.due[d]
```

**Lateness Non-negativity:**
```python
# lateness(d) ≥ 0  ∀d
def lateness_nonnegative_rule(m, d):
    return m.lateness[d] >= 0
```

**Late Indicator Constraints:**
```python
# If late(d) = 1, then lateness(d) > 0
# Reformulated as: lateness(d) ≥ epsilon * late(d)
def late_if_positive_lateness_rule(m, d):
    return m.lateness[d] >= m.epsilon * m.late[d]

# If late(d) = 0, then lateness(d) = 0
# Reformulated as: lateness(d) ≤ M * late(d)
def not_late_if_zero_lateness_rule(m, d):
    return m.lateness[d] <= m.M * m.late[d]
```

#### 3. Updated Objective Function (objective.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/objective.py](packing_model_problem_4_1_c2/objective.py)

**New Objective Formula (from PDF Page 9):**
```
f = α * otif + β * wipobj + γ * workforce + δ * totalnotutilized

where:
otif = ∑_d priority(d) * (7 * late(d) + 3 * lateness(d))
```

**Implementation:**
```python
def _otif_term(self, m):
    """
    OTIF term: Minimize late deliveries and lateness.

    This penalizes:
    - Being late (binary late(d) with weight 7)
    - Amount of lateness (continuous lateness(d) with weight 3)
    Each weighted by the demand's priority.
    """
    return sum(
        m.priority[d] * (7 * m.late[d] + 3 * m.lateness[d])
        for d in m.DEMANDS
    )
```

#### 4. Updated Parameters (parameters.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/parameters.py](packing_model_problem_4_1_c2/parameters.py)

**Added Alpha Weight:**
```python
model.alpha = pyo.Param(initialize=obj_weights.get('alpha', 1.0), doc="OTIF weight")
```

#### 5. Updated Model Integration (model.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/model.py](packing_model_problem_4_1_c2/model.py)

**Added OTIF Constraints:**
```python
from .constraints import (
    # ... other imports
    define_otif_constraints
)

# In _build_model():
define_otif_constraints(self.model)
```

### Update 2: Inventory Balance Correction

#### 1. Added `shipped(d1,d)` Binary Variable (variables.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/variables.py](packing_model_problem_4_1_c2/variables.py)

**New Variable (from PDF Page 2):**
```python
# shipped(d1,d): Demand d1 is shipped before or at the same time as demand d (binary)
model.shipped = pyo.Var(
    model.DEMANDS, model.DEMANDS,
    domain=pyo.Binary,
    doc="Demand d1 is shipped before or at the same time as demand d"
)
```

This binary variable tracks the relative shipping order of demands, which is needed for the corrected inventory balance equation.

### 2. Updated Inventory Balance Constraint (wip.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/constraints/wip.py](packing_model_problem_4_1_c2/constraints/wip.py)

**Issue:**
The inventory balance equation needed to account for which demands have actually shipped by the time demand d ships, not just sum all demands or demands up to index d.

**Original (INCORRECT) Formula:**
```
inv(u,d) = inv0(u) + prodbefore(u,d) - ∑_{d':prodtype(d')=u, d'≤d} qty(d')
```

**Intermediate (ALSO INCORRECT) Formula:**
```
inv(u,d) = inv0(u) + prodbefore(u,d) - ∑_{d':prodtype(d')=u} qty(d')
```

**Corrected Formula (from PDF Page 7):**
```
inv(u,d) = inv0(u) + prodbefore(u,d) - ∑_{d1:prodtype(d1)=u} shipped(d1,d) * qty(d1)  ∀u ∀d
```

**Key Difference:**
The summation now uses `shipped(d1,d) * qty(d1)` to only count demands that have actually shipped by the time demand d ships. This correctly models the timing-dependent inventory levels.

**Code Change:**
```python
# OLD (INCORRECT):
total_demand = sum(
    m.qty[d_prime]
    for d_prime in m.DEMANDS
    if m.prodtype[d_prime] == u
)

# NEW (CORRECT):
shipped_demand = sum(
    m.shipped[d1, d] * m.qty[d1]
    for d1 in m.DEMANDS
    if m.prodtype[d1] == u
)
```

### 3. Added Shipped Timing Constraints (wip.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/constraints/wip.py](packing_model_problem_4_1_c2/constraints/wip.py)

**New Constraints (from PDF Page 7):**

Two constraints link the `shipped(d1,d)` binary variable to the actual shipping times:

```python
# If shipped(d1,d) = 1, then ship(d1) ≤ ship(d)
def shipped_before_rule(m, d1, d):
    return m.ship[d1] <= m.ship[d] + m.M * (1 - m.shipped[d1, d])

# If shipped(d1,d) = 0, then ship(d1) > ship(d)
def shipped_after_rule(m, d1, d):
    return m.ship[d1] >= m.ship[d] + m.epsilon - m.M * m.shipped[d1, d]
```

These constraints ensure that `shipped(d1,d) = 1` if and only if demand d1 ships before or at the same time as demand d.

### 4. WIP Objective Term (objective.py)

**Location:** [simple_model/packing_model_problem_4_1_c2/objective.py](packing_model_problem_4_1_c2/objective.py)

**Status:** ✓ Already Correct

The WIP objective term was already correctly implemented as specified in PDF Page 9:

```
wipobj = ∑_u ∑_d inv(u,d)
```

Implementation:
```python
def _wip_term(self, m):
    return sum(
        m.inv[u, d]
        for u in m.TYPES
        for d in m.DEMANDS
    )
```

**No changes needed** for the objective function.

## Semantic Interpretation

The corrected inventory balance equation makes sense:

- `inv(u,d)` represents the inventory of type u **remaining after demand d ships**
- `inv0(u)` is the initial inventory
- `prodbefore(u,d)` is the amount produced before demand d ships
- `shipped(d1,d) * qty(d1)` for each demand d1 of type u represents the quantity shipped if d1 has shipped by the time d ships

The equation states:
> Inventory remaining after demand d = Initial inventory + Amount produced before d ships - Demands of type u that have shipped by time demand d ships

This correctly models timing-dependent inventory:
- Different demands can ship at different times
- The `prodbefore(u,d)` variable counts orders that complete before demand d ships
- The `shipped(d1,d)` binary variable determines whether demand d1's quantity should be subtracted from inventory at the time demand d ships
- Inventory is tracked at each demand shipping point, allowing proper WIP accounting

## Testing

All test cases run successfully with the OTIF implementation:

1. **Standard Example** ([problem_4_1_c2_example.py](problem_4_1_c2_example.py)):
   - 2 types, 4 orders, 2 demands, 2 lines
   - Solves to optimal with objective value: 2.00
   - Both demands delivered ON-TIME

2. **Configurable Example** ([problem_4_1_c2_configurable_example.py](problem_4_1_c2_configurable_example.py)):
   - Allows testing different problem sizes through CONFIG dictionary
   - Automatically generates data with perfect capacity matching
   - Default configuration: 240 demands, 240 orders, 48 lines

## Files Modified

### Update 4: prodorder Assignment Requirement
1. `simple_model/packing_model_problem_4_1_c2/constraints/shipping.py` - Added `order_assignment_required` constraint
2. `simple_model/CORRECTION_NOTES.md` - This document

### Update 3: OTIF Implementation
1. `simple_model/packing_model_problem_4_1_c2/variables.py` - Added `lateness(d)` and `late(d)` variables
2. `simple_model/packing_model_problem_4_1_c2/constraints/otif.py` - NEW FILE: OTIF constraints
3. `simple_model/packing_model_problem_4_1_c2/constraints/__init__.py` - Added OTIF import
4. `simple_model/packing_model_problem_4_1_c2/objective.py` - Added OTIF term to objective
5. `simple_model/packing_model_problem_4_1_c2/parameters.py` - Added alpha weight parameter
6. `simple_model/packing_model_problem_4_1_c2/model.py` - Integrated OTIF constraints
7. `simple_model/CORRECTION_NOTES.md` - This document

### Update 2: Inventory Balance Correction
1. `simple_model/packing_model_problem_4_1_c2/variables.py` - Added `shipped(d1,d)` binary variable
2. `simple_model/packing_model_problem_4_1_c2/constraints/wip.py` - Updated inventory balance constraint and added shipped timing constraints
3. `simple_model/CORRECTION_NOTES.md` - This document

## Files Verified (No Changes Needed)

1. `simple_model/packing_model_problem_4_1_c2/objective.py` - WIP objective term already correct

## References

- Problem_4_1_c2.pdf Page 7: Corrected inventory balance equation
- Problem_4_1_c2.pdf Page 9: WIP objective term specification
