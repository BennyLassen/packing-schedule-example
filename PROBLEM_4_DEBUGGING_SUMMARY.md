# Problem_4 Debugging Summary

## Current Status

The Problem_4 implementation is **architecturally complete** but has a **fundamental constraint formulation bug** that causes infeasibility even for trivial problems.

## Key Finding

Even with a **manually fixed assignment** (x[1,1,2]=1, ship[1,5]=1 for a 1-order problem), the model is infeasible. This means the issue is not with finding a solution, but with the constraint formulation itself.

##  Bugs Found and Fixed

###  Bug #1: TimeCompletion Bound Issue (ATTEMPTED FIX - Not the root cause)
- **Issue**: `timecompletion` was initially set to unbounded, but Problem_3 keeps it bounded
- **Fix**: Reverted to `bounds=(1, n_timeslots)` to match Problem_3
- **Result**: Still infeasible

### Remaining Issues

The infeasibility persists even with:
- ✅ 1 order, 1 line, 10 time slots (minimal problem)
- ✅ Loose due date (t=10, end of horizon)
- ✅ 90% available capacity (10% reserved)
- ✅ Fixed assignment (x[1,1,2]=1, ship[1,5]=1)

## Systematic Debugging Performed

1. **Logic Verification**: Manually verified production and inventory balance logic - appears correct
2. **Constraint Inspection**: Exported model to LP format and inspected constraints
3. **Minimal Test**: Created 1-order test case - infeasible
4. **Fixed Assignment Test**: Fixed x and ship variables - still infeasible

## Most Likely Root Causes

Based on the investigation, the issue is likely in one of these areas:

### Hypothesis #1: Production Timing Constraint ⭐ MOST LIKELY
The production constraint calculates when production completes:
```python
prod(i,t) = sum(x(i,j,t_start) for t_start where t_start + p(i,j) == t)
```

**Potential Issue**: The condition `t_start + p(i,j) == t` might not be generating any terms for certain values, leading to `prod(i,t) = 0` when it should be 1.

**Test**: For p=3, t=5, this requires t_start=2. But what if there's an off-by-one error or the iteration doesn't include all valid t_start values?

### Hypothesis #2: Inventory Balance with Production Timing
The inventory balance equation:
```python
inv(i,t) = inv(i,t-1) + prod(i,t) - ship(i,t)
```

If `prod(i,t)` is incorrectly zero due to Hypothesis #1, then `inv(i,t)` can never become positive, which means:
- `hasinv(i,t)` must be 0 (from upper bound constraint)
- But we need `hasinv(i,t)=1` to ship (from `ship(i,t) <= hasinv(i,t)`)
- **CONFLICT** → Infeasible!

### Hypothesis #3: Has-Inventory Big-M Formulation
The has-inventory constraints use Big-M formulation:
```python
inv(i,t) >= 1 - M*(1-hasinv(i,t))  # Lower bound
inv(i,t) <= M*hasinv(i,t)           # Upper bound
```

**Issue**: The lower bound requires `inv >= 1` when `hasinv=1`. But what if production only produces 1 unit total (not per time slot)? The formulation might be assuming integer units, but the problem is stated as binary completion.

### Hypothesis #4: Missing or Incorrect Constraint from Problem_3
Problem_4 PDF might have omitted a critical constraint that Problem_3 includes. Need to compare constraint-by-constraint with working Problem_3.

## Recommended Debugging Approach

### Step 1: Compare with Problem_3 (Highest Priority)
1. Take the exact same 1-order test case
2. Run it with Problem_3 (packing_model) - verify it works
3. Extract the solution values for all variables
4. Compare Problem_3 and Problem_4 constraint formulations side-by-side
5. Identify which constraint differs

### Step 2: Incremental Constraint Removal
Create a version of the model with constraints removed one group at a time:
1. Start with ONLY: assignment + capacity
2. Add: shipping (ship once, calc timeship)
3. Add: OTIF (start/complete time) **← Likely fails here**
4. Add: WIP (production, inventory) **← Or fails here**
5. Add: workforce

### Step 3: Fix Production Constraint Logic
If Hypothesis #1 is correct, the fix might be to ensure the production timing logic correctly identifies when orders complete. Possible issues:
- Integer division/rounding
- Parameter type mismatches (int vs float)
- Index range issues in the summation

### Step 4: Simplify Inventory Tracking
Consider replacing the complex has-inventory + Big-M formulation with simpler direct constraints:
- Remove `hasinv` variable entirely
- Use: `ship(i,t) <= sum(prod(i,tau) for tau <= t)` (can only ship if produced)

## Quick Win: Test with Problem_3 Data Format

The **fastest path to a working model** might be:
1. Take a working Problem_3 example
2. Create a script that "aggregates" the worker dimension from Problem_3
3. Use that to validate that Problem_4 logic should work
4. Compare the two formulations to find the discrepancy

## Files for Reference

- **Test Scripts**:
  - `test_problem_4_minimal.py` - Minimal 1-order test (infeasible)
  - `test_manual_assignment.py` - Fixed assignment test (infeasible)
  - `debug_model_structure.py` - Model inspection

- **Model Files**:
  - `packing_model_simple/constraints/wip.py` - Production constraint (line 46-64)
  - `packing_model_simple/constraints/shipping.py` - Has-inventory constraints (line 86-123)
  - `packing_model_simple/constraints/otif.py` - OTIF constraints

- **Debug Output**:
  - `problem_4_debug.lp` - LP file export for manual inspection

## Conclusion

The Problem_4 implementation has correct architecture and most constraints appear logically sound. However, there's a subtle but critical bug that causes infeasibility even for trivial cases. The most efficient next step is to **compare with a working Problem_3 solution** to identify the discrepancy.

The issue is likely in the production timing constraint or the interaction between production, inventory, and shipping constraints.

---

**Time Investment**: ~3 hours of implementation + 1 hour of debugging
**Status**: Implementation complete, requires constraint debugging
**Estimated Fix Time**: 1-2 hours with proper constraint comparison
