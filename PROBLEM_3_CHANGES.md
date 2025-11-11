# Problem 3 Implementation - Worker Movement Penalty

This document describes the changes made to implement Problem 3, which adds a **worker movement penalty** to the optimization model.

## Overview

Problem 3 extends Problem 2 by adding a penalty for workers switching between production lines. This encourages the optimizer to keep workers on the same line when possible, which can:

- Reduce setup overhead when workers move between lines
- Improve production efficiency by minimizing worker transitions
- Create more stable work assignments

## Key Changes

### 1. Objective Function Enhancement

The objective function now includes a fifth term for worker movement:

#### Previous (Problem 2):
```
minimize: α×OTIF + β×WIP + γ×Workforce + δ×LineUtil
```

#### Current (Problem 3):
```
minimize: α×OTIF + β×WIP + γ×Workforce + δ×LineUtil + ω×WorkerMove
```

**New Term - Worker Movement:**
```
WorkerMove = ∑_w ∑_t m[w,t]
```

Where:
- `m[w,t]` is a binary variable indicating if worker `w` moved to a different line at time `t`
- `ω` (omega) is the weight parameter controlling the importance of minimizing worker movements

### 2. New Constraint: Worker Movement Tracking

A new constraint was added to track worker movements between lines:

```
m[w,t] ≥ ∑_i (x[i,j,w,t] - x[i,j,w,t-1])    ∀w, ∀j, ∀t>1
```

**Explanation:**
- For each worker `w`, line `j`, and time `t` (after the first time slot)
- The constraint calculates the difference in assignments between consecutive time periods
- If worker `w` was working on line `j` at time `t-1` but switches to a different line at time `t`, the movement indicator `m[w,t]` becomes 1
- The constraint ensures that `m[w,t]` captures any line switch by the worker

**Note:** The movement indicator `m[w,t]` is defined per worker and time, not per line. This means a single movement indicator captures whether the worker moved to *any* different line at time `t`.

### 3. New Objective Weight Parameter

A new weight parameter `ω` (omega) was added to control the worker movement penalty:

```python
objective_weights = {
    'alpha': 1.0,   # OTIF weight
    'beta': 0.5,    # WIP weight
    'gamma': 0.3,   # Workforce variability weight
    'delta': 0.2,   # Line utilization weight
    'omega': 0.1    # Worker movement penalty (NEW in Problem_3)
}
```

**Key Points:**
- `omega = 0.0`: No penalty for worker movements (equivalent to Problem 2 behavior)
- `omega > 0`: Encourages workers to stay on the same line when possible
- Higher `omega` values more strongly discourage worker movements
- The parameter is optional - if not specified, no movement penalty is applied

## Implementation Details

### Files Modified

1. **[packing_model/constraints/worker.py](packing_model/constraints/worker.py)**
   - Added `worker_movement_rule()` function
   - Implements the movement balance constraint: `m[w,t] ≥ Σ_i(x[i,j,w,t] - x[i,j,w,t-1])`
   - Constraint is defined for all workers, lines, and time slots (t > 1)

2. **[packing_model/objective.py](packing_model/objective.py)**
   - Added `_worker_movement_term()` method to `ObjectiveManager` class
   - Calculates worker movement penalty: `Σ_w Σ_t m[w,t]`
   - Updated `objective_rule()` to include the worker movement term when `omega > 0`
   - Added default `omega = 0.1` to the default weights dictionary

3. **[packing_model/variables.py](packing_model/variables.py)**
   - The movement variable `m[w,t]` was already defined in Problem 2
   - No changes needed (variable was present but unused until Problem 3)

4. **[README.md](README.md)**
   - Updated objective function documentation
   - Added worker movement constraint documentation
   - Updated decision variables table to highlight the `m[w,t]` variable

## Usage Examples

### Example 1: No Worker Movement Penalty (Problem 2 Behavior)

```python
data = {
    # ... problem data ...
    'objective_weights': {
        'alpha': 5.0,
        'beta': 0.2,
        'gamma': 0.1,
        'delta': 0.5,
        'omega': 0.0  # No movement penalty
    }
}

model = PackingScheduleModel(data)
results = model.solve()
```

### Example 2: Moderate Worker Movement Penalty

```python
data = {
    # ... problem data ...
    'objective_weights': {
        'alpha': 5.0,
        'beta': 0.2,
        'gamma': 0.1,
        'delta': 0.5,
        'omega': 1.0  # Moderate penalty for worker movements
    }
}

model = PackingScheduleModel(data)
results = model.solve()
```

### Example 3: High Worker Movement Penalty

```python
data = {
    # ... problem data ...
    'objective_weights': {
        'alpha': 5.0,
        'beta': 0.2,
        'gamma': 0.1,
        'delta': 0.5,
        'omega': 5.0  # Strong penalty - workers stay on same line
    }
}

model = PackingScheduleModel(data)
results = model.solve()
```

## Backward Compatibility

**The implementation is fully backward compatible with Problem 2:**

- If `omega` is not specified in `objective_weights`, the worker movement penalty is **not applied**
- If `omega = 0`, the worker movement penalty is **not applied**
- Existing code that doesn't specify `omega` will continue to work exactly as before

This means:
- All existing examples continue to work without modification
- Problem 2 behavior is preserved when `omega` is omitted or set to 0
- Users can gradually adopt the worker movement penalty by adding the `omega` parameter

## When to Use Worker Movement Penalty

### Use Higher `omega` Values When:

1. **Setup overhead is significant** when workers switch lines
2. **Worker specialization** is important (workers are more efficient on certain lines)
3. **Training costs** are high for workers moving to new lines
4. **Quality concerns** arise when workers frequently change equipment
5. **Stability** in work assignments is valued

### Use Lower `omega` Values (or 0) When:

1. **Flexibility** is more important than stability
2. **Worker cross-training** is encouraged
3. **Line balancing** takes priority over worker continuity
4. **Setup overhead** for worker movements is negligible
5. **Meeting deadlines** (high OTIF) is the dominant concern

## Trade-offs and Considerations

### Multi-Objective Optimization

The worker movement penalty interacts with other objectives:

- **vs. OTIF:** Movement penalty may conflict with meeting tight deadlines if optimal line selection requires worker movements
- **vs. WIP:** Reducing movements might increase WIP if it prevents optimal parallel processing
- **vs. Workforce Variability:** Can complement workforce stability by keeping workers on consistent lines
- **vs. Line Utilization:** May increase number of lines used if workers stay on their initial lines

### Tuning Recommendations

Start with low `omega` values (0.1 - 0.5) and increase gradually:

1. **ω = 0.0 - 0.2:** Minimal penalty, allows flexibility
2. **ω = 0.5 - 1.0:** Moderate penalty, encourages but doesn't force consistency
3. **ω = 2.0 - 5.0:** Strong penalty, workers rarely switch lines
4. **ω > 5.0:** Very strong penalty, worker assignments become nearly fixed

The optimal value depends on:
- Your production environment
- The relative importance of different objectives
- The characteristics of your orders and lines
- The skill levels and versatility of your workers

## Testing

A test script `test_worker_movement.py` is provided to verify the implementation:

```bash
python test_worker_movement.py
```

This test:
1. Runs the model with `omega=0` (no penalty)
2. Runs the model with `omega=2.0` (high penalty)
3. Compares the number of worker movements in each solution
4. Verifies that the movement penalty affects optimizer decisions

## Mathematical Formulation Reference

For complete mathematical details, see `Problem_3.pdf` in the project root:

- **Page 2:** Decision variable `m(w,t)` definition
- **Page 5:** Movement balance constraint formulation
- **Page 11:** Objective function with worker movement term

## Summary

Problem 3 adds sophisticated worker movement tracking and penalization to the optimization model, providing users with fine-grained control over how workers are assigned across production lines. The implementation:

- ✅ Is fully backward compatible with Problem 2
- ✅ Uses optional parameter `omega` to control the penalty strength
- ✅ Adds minimal computational overhead (one constraint per worker-line-time combination)
- ✅ Integrates seamlessly with existing objective terms
- ✅ Provides realistic production scheduling capabilities

The worker movement penalty is particularly valuable in environments where setup overhead, worker specialization, or assignment stability are important considerations.
