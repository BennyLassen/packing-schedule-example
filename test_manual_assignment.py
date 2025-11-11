"""
Manually test if a specific assignment is feasible.

We'll set x[1,1,2] = 1 (order 1 starts on line 1 at time 2) and check if all constraints are satisfied.
"""

import pyomo.environ as pyo
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create minimal data
data = {
    'n_orders': 1,
    'n_lines': 1,
    'n_timeslots': 10,
    'n_workers': 1,
    'processing_time': np.array([[3]]),
    'setup_time': np.zeros((1, 1, 1)),
    'initial_inventory': np.array([0]),
    'reserved_capacity': 0.9,  # Very loose
    'due_date': np.array([10]),
    'priority': np.array([100]),
    'objective_weights': {
        'alpha': 1.0,
        'beta': 0.1,
        'gamma': 0.1,
        'delta': 0.1
    }
}

from packing_model_simple import PackingScheduleModelSimple

model_obj = PackingScheduleModelSimple(data)
m = model_obj.model

print("="*80)
print("MANUAL FEASIBILITY CHECK")
print("="*80)

print("\nSetting: x[1,1,2] = 1")
print("(Order 1 starts on line 1 at time 2, with processing time 3)")

# Fix the assignment
m.x[1,1,2].fix(1)
for j in [1]:
    for t in [1,3,4,5,6,7,8,9,10]:
        m.x[1,j,t].fix(0)

# Ship at time 5 (earliest possible)
m.ship[1,5].fix(1)
for t in [1,2,3,4,6,7,8,9,10]:
    m.ship[1,t].fix(0)

print("\nFixed variables:")
print("  x[1,1,2] = 1")
print("  All other x = 0")
print("  ship[1,5] = 1")
print("  All other ship = 0")

print("\nNow solving to check if remaining variables can satisfy constraints...")

from pyomo.opt import SolverFactory
solver = SolverFactory('appsi_highs')
solver.config.load_solution = False

try:
    results = solver.solve(m, tee=False)
    print(f"\nResult: {results.solver.termination_condition}")

    if str(results.solver.termination_condition) in ['optimal', 'feasible']:
        solver.load_vars()
        print("\nFEASIBLE! Variable values:")
        print(f"  timestart[1] = {pyo.value(m.timestart[1])}")
        print(f"  timecompletion[1] = {pyo.value(m.timecompletion[1])}")
        print(f"  timeship[1] = {pyo.value(m.timeship[1])}")
        print(f"  late[1] = {pyo.value(m.late[1])}")
        print(f"  lateness[1] = {pyo.value(m.lateness[1])}")
        print(f"  inv[1,0] = {pyo.value(m.inv[1,0])}")
        print(f"  inv[1,5] = {pyo.value(m.inv[1,5])}")
        print(f"  prod[1,5] = {pyo.value(m.prod[1,5])}")
        print(f"  workersused[2] = {pyo.value(m.workersused[2])}")
        print(f"  workersused[5] = {pyo.value(m.workersused[5])}")
    else:
        print("\nINFEASIBLE even with fixed assignment!")
        print("This means the constraint formulation has a fundamental issue.")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
