# HiGHS Solver Performance Tips for Problem_4_1_c2

## Problem: Slow Solution Times

The solver is taking a long time to find initial feasible solutions, as evidenced by:
- `BestSol = inf` for extended periods
- Solver spending time at root node without finding solutions
- High iteration counts before finding any feasible solution

## Solutions

### 1. **Use Recommended HiGHS Options (FASTEST IMPROVEMENT)**

Modify your solve call in `problem_4_1_c2_configurable_example.py` to use performance-tuned options:

```python
results = model.solve(
    solver_name='appsi_highs',
    tee=True,
    time_limit=CONFIG['time_limit'],
    mip_rel_gap=CONFIG['mip_gap'],
    highs_options={
        # ===== HEURISTIC SETTINGS (Find solutions faster) =====
        'mip_heuristic_effort': 0.3,     # Increase from default 0.05 (range: 0.0-1.0)
                                          # Higher = more effort on heuristics to find solutions

        # ===== PARALLELIZATION (Use multiple cores) =====
        'parallel': 'on',                 # Enable parallel solving
        'threads': 4,                     # Number of threads (adjust to your CPU)

        # ===== SYMMETRY & PRESOLVE (Reduce problem size) =====
        'mip_detect_symmetry': 'on',      # Detect and break symmetries
        'presolve': 'on',                 # Apply presolve (should be on by default)

        # ===== SEARCH LIMITS (Prevent excessive branching) =====
        'mip_max_leaves': 5000,           # Limit branch-and-bound tree size
        'mip_max_nodes': 10000,           # Maximum nodes to explore

        # ===== TOLERANCES (Relax if needed) =====
        # 'mip_feasibility_tolerance': 1e-5,  # Default is 1e-6
        # 'mip_abs_gap': 0.1,              # Stop if absolute gap < 0.1
    }
)
```

### 2. **Reduce Problem Size**

Adjust your CONFIG in `problem_4_1_c2_configurable_example.py`:

```python
# Instead of:
n_orders_per_day_per_line = 5
n_lines = 10
nr_days = 1

# Try smaller problem first:
n_orders_per_day_per_line = 3  # Reduce to 3 orders per line-day
n_lines = 5                    # Reduce to 5 lines
nr_days = 1
```

### 3. **Relax MIP Gap**

```python
CONFIG = {
    # ... other settings ...

    # Relax MIP gap from 1% to 5% for faster solving
    'mip_gap': 0.05,  # Accept solution within 5% of optimal

    # Increase time limit if needed
    'time_limit': 600,  # 10 minutes instead of 5
}
```

### 4. **Adjust Objective Weights**

The `delta` weight (line utilization) adds complexity. Try reducing or disabling it:

```python
CONFIG = {
    # ... other settings ...

    'objective_weights': {
        'beta': 1.0,     # WIP weight
        'gamma': 1.0,    # Workforce weight (reduced from 2.0)
        'delta': 0.0     # Disable line utilization penalty temporarily
    },
}
```

### 5. **Use a Warm Start (Advanced)**

If you have a good initial solution, you can provide it to the solver. This requires setting initial values for variables before solving.

## Complete Example with Recommended Settings

Update your `problem_4_1_c2_configurable_example.py`:

```python
# ===== At the top: Reduce problem size =====
n_orders_per_day_per_line = 3  # Reduced from 5
n_lines = 5                     # Reduced from 10
nr_days = 1

CONFIG = {
    'n_types': 2,
    'n_lines': n_lines,
    'n_demands': n_orders_per_day_per_line * n_lines * nr_days,
    'planning_horizon': 100.0,

    # Processing times
    'processing_time_min': 8.0,
    'processing_time_max': 15.0,

    # Setup times
    'setup_time_same_type': 0.0,
    'setup_time_diff_type': 5.0,

    # Due dates
    'due_date_start_pct': 0.3,
    'due_date_end_pct': 0.9,

    # Demand quantities
    'demand_qty_min': 1,
    'demand_qty_max': 1,

    # Priorities
    'priority_min': 5,
    'priority_max': 20,

    # Initial inventory
    'initial_inventory_pct': 0.0,
    'initial_inventory_max': 2,

    # Objective weights (simplified)
    'objective_weights': {
        'beta': 1.0,     # WIP
        'gamma': 1.0,    # Workforce (reduced)
        'delta': 0.0     # Line utilization (disabled)
    },

    # Solver settings (relaxed)
    'time_limit': 600,     # 10 minutes
    'mip_gap': 0.05,       # 5% gap
    'random_seed': 42
}

# ===== In the solve section =====
results = model.solve(
    solver_name='appsi_highs',
    tee=True,
    time_limit=CONFIG['time_limit'],
    mip_rel_gap=CONFIG['mip_gap'],
    highs_options={
        'mip_heuristic_effort': 0.3,
        'parallel': 'on',
        'threads': 4,
        'mip_detect_symmetry': 'on',
        'presolve': 'on',
        'mip_max_leaves': 5000,
        'mip_max_nodes': 10000,
    }
)
```

## Performance Expectations

With the recommended settings:

| Problem Size | Expected Solve Time | Gap |
|-------------|-------------------|-----|
| 15 orders, 5 lines, 15 demands | 30-120 seconds | < 5% |
| 30 orders, 5 lines, 15 demands | 2-5 minutes | < 5% |
| 50 orders, 10 lines, 50 demands | 5-15 minutes | < 10% |
| 100+ orders | 15+ minutes | Variable |

## Additional HiGHS Options Reference

Here are more options you can experiment with:

```python
highs_options={
    # === Solution finding ===
    'mip_heuristic_effort': 0.3,     # 0.0-1.0, higher = more heuristics
    'mip_max_improving_sols': 10,    # Stop after finding N improving solutions

    # === Search strategy ===
    'mip_pscost_minreliability': 8,  # Branching reliability (default 8)
    'mip_min_cliquetable_entries_for_parallelism': 100000,

    # === Limits ===
    'mip_max_nodes': 10000,          # Maximum nodes in B&B tree
    'mip_max_leaves': 5000,          # Maximum leaf nodes
    'mip_max_stall_nodes': 1000,     # Stop if no improvement for N nodes

    # === Tolerances ===
    'mip_abs_gap': 1.0,              # Absolute gap tolerance
    'mip_rel_gap': 0.05,             # Relative gap tolerance (5%)
    'mip_feasibility_tolerance': 1e-5,

    # === Performance ===
    'parallel': 'on',
    'threads': 4,                     # Or -1 for all available threads
    'presolve': 'on',
    'mip_detect_symmetry': 'on',

    # === Output control ===
    'log_to_console': 'true',         # Show progress
    'output_flag': 'true',
}
```

## Troubleshooting

### Still Too Slow?

1. **Check model size**: Run with `print(model.model.statistics)` to see variable counts
2. **Profile constraints**: Large numbers of `shipped(d1,d)` and `prodorder(i,d)` constraints can be bottlenecks
3. **Consider CPLEX or Gurobi**: Commercial solvers are often faster for large MIPs (if you have access)

### Getting Infeasible Solutions?

1. **Check capacity**: Ensure `n_orders >= total_demand_qty`
2. **Verify due dates**: Make sure `planning_horizon` is large enough
3. **Review inventory**: Check that `initial_inventory + production >= demands`

### Memory Issues?

1. Reduce `mip_max_leaves` and `mip_max_nodes`
2. Reduce problem size (fewer orders, demands, or lines)
3. Use 64-bit Python if not already

## Summary of Key Changes Made

I've updated [model.py](packing_model_problem_4_1_c2/model.py) to accept `highs_options` parameter in the `solve()` method. You can now pass any HiGHS-specific options as a dictionary.

**Quick Win**: Add the highs_options shown in Solution #1 to your solve call. This should reduce solve time by 2-5x for most problems.
