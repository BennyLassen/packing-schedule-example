"""
Debug model structure by inspecting constraints.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from packing_model_simple import PackingScheduleModelSimple

# Ultra minimal problem
data = {
    'n_orders': 1,
    'n_lines': 1,
    'n_timeslots': 10,
    'n_workers': 1,
    'processing_time': np.array([[3]]),
    'setup_time': np.zeros((1, 1, 1)),
    'initial_inventory': np.array([0]),
    'reserved_capacity': 0.1,
    'due_date': np.array([10]),
    'priority': np.array([100]),
    'objective_weights': {
        'alpha': 1.0,
        'beta': 0.1,
        'gamma': 0.1,
        'delta': 0.1
    }
}

print("Building model...")
model_obj = PackingScheduleModelSimple(data)
m = model_obj.model

print("\n" + "="*80)
print("MODEL STRUCTURE INSPECTION")
print("="*80)

# Check key constraints
print("\n1. ASSIGNMENT CONSTRAINT:")
print(f"   one_assignment[1] = {m.one_assignment[1].expr}")

print("\n2. SHIPPING TIME:")
print(f"   shipping_time[1] = {m.shipping_time[1].expr}")

print("\n3. START TIME:")
print(f"   start_time[1] = {m.start_time[1].expr}")

print("\n4. COMPLETION TIME:")
print(f"   completion_time[1] = {m.completion_time[1].expr}")

print("\n5. SHIP AFTER COMPLETE:")
print(f"   ship_after_complete[1] = {m.ship_after_complete[1].expr}")

print("\n6. PRODUCTION at t=1:")
print(f"   production[1,1] = {m.production[1,1].expr}")

print("\n7. PRODUCTION at t=5 (should be when order completes if starts at t=2):")
print(f"   production[1,5] = {m.production[1,5].expr}")

print("\n8. INITIAL INVENTORY:")
print(f"   initial_inventory[1] = {m.initial_inventory[1].expr}")

print("\n9. INVENTORY BALANCE at t=1:")
print(f"   inventory_balance[1,1] = {m.inventory_balance[1,1].expr}")

print("\n10. INVENTORY BALANCE at t=5:")
print(f"   inventory_balance[1,5] = {m.inventory_balance[1,5].expr}")

print("\n11. HAS INVENTORY LOWER at t=5:")
print(f"   has_inventory_lower[1,5] = {m.has_inventory_lower[1,5].expr}")

print("\n12. SHIP REQUIRES INVENTORY at t=5:")
print(f"   ship_requires_inventory[1,5] = {m.ship_requires_inventory[1,5].expr}")

print("\n" + "="*80)
print("CHECKING FOR OBVIOUS CONFLICTS")
print("="*80)

# Manual feasibility check
print("\nManual feasibility check for x[1,1,2]=1 (order 1 starts on line 1 at time 2):")
print("  - Processing time: 3")
print("  - timestart[1] = 2")
print("  - timecompletion[1] = 2 + 3 = 5")
print("  - prod[1,5] = 1 (completes at t=5)")
print("  - inv[1,0] = 0")
print("  - inv[1,1] = 0 + 0 - 0 = 0")
print("  - inv[1,2] = 0 + 0 - 0 = 0")
print("  - inv[1,3] = 0 + 0 - 0 = 0")
print("  - inv[1,4] = 0 + 0 - 0 = 0")
print("  - inv[1,5] = 0 + 1 - 0 = 1")
print("  - Can ship at t >= 5")
print("  - timeship[1] = 5 (or later)")
print("  - Due date = 10")
print("  - Should be feasible!")

print("\n" + "="*80)
print("Exporting model to LP file for inspection...")
print("="*80)

try:
    m.write('problem_4_debug.lp', io_options={'symbolic_solver_labels': True})
    print("Model exported to: problem_4_debug.lp")
    print("Inspect this file to find conflicting constraints")
except Exception as e:
    print(f"Export failed: {e}")
