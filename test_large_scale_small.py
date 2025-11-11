"""
Quick test of large-scale example with reduced problem size.

This is a scaled-down version to verify the example works correctly
without requiring extensive computational resources.

Scaled-down scenario:
- 12 lines (instead of 48)
- 12 workers (instead of 48)
- 200 orders (instead of 1700)
- 2 days (instead of 7)
- 30-minute slots (instead of 15-minute)

This should solve in 1-5 minutes instead of 10-60 minutes.
"""

import numpy as np
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packing_model import PackingScheduleModel


def create_scaled_down_data():
    """Create a scaled-down version of the large-scale problem."""

    n_orders = 200      # Reduced from 1700
    n_lines = 12        # Reduced from 48
    n_timeslots = 96    # 2 days × 48 slots (30-min intervals)
    n_workers = 12      # Reduced from 48

    print(f"Scaled-down problem:")
    print(f"  Orders: {n_orders}")
    print(f"  Lines: {n_lines}")
    print(f"  Workers: {n_workers}")
    print(f"  Time slots: {n_timeslots} (2 days, 30-min intervals)")

    np.random.seed(42)

    # Processing times: 1-4 slots (30-120 minutes)
    processing_time = np.random.randint(1, 5, size=(n_orders, n_lines))

    # Setup times based on families
    n_families = 5
    order_families = np.random.randint(0, n_families, size=n_orders)

    setup_time = np.zeros((n_orders, n_orders, n_lines))
    for i in range(n_orders):
        for k in range(n_orders):
            if i == k:
                setup_time[i, k, :] = 0
            elif order_families[i] == order_families[k]:
                setup_time[i, k, :] = 0
            else:
                setup_time[i, k, :] = 1

    worker_availability = np.ones((n_workers, n_timeslots))
    initial_inventory = np.zeros(n_orders, dtype=int)
    reserved_capacity = 0.15

    # Due dates distributed across 2 days
    due_date = np.random.randint(1, n_timeslots+1, size=n_orders)
    priority = np.random.randint(50, 101, size=n_orders)

    workforce_target = int(n_workers * 0.6)

    objective_weights = {
        'alpha': 10.0,
        'beta': 0.1,
        'gamma': 0.05,
        'delta': 0.01,
        'omega': 0.5
    }

    return {
        'n_orders': n_orders,
        'n_lines': n_lines,
        'n_timeslots': n_timeslots,
        'n_workers': n_workers,
        'processing_time': processing_time,
        'setup_time': setup_time,
        'worker_availability': worker_availability,
        'initial_inventory': initial_inventory,
        'reserved_capacity': reserved_capacity,
        'due_date': due_date,
        'priority': priority,
        'workforce_target': workforce_target,
        'objective_weights': objective_weights
    }


def main():
    print("="*80)
    print("SCALED-DOWN LARGE-SCALE EXAMPLE TEST")
    print("="*80)

    print("\n[Step 1] Creating scaled-down problem...")
    data = create_scaled_down_data()

    print("\n[Step 2] Building model...")
    start = time.time()
    model = PackingScheduleModel(data)
    build_time = time.time() - start

    print(f"  Build time: {build_time:.2f} seconds")
    print(f"  Variables: {model.model.nvariables():,}")
    print(f"  Constraints: {model.model.nconstraints():,}")

    print("\n[Step 3] Solving...")
    results = model.solve(
        solver_name='appsi_highs',
        tee=False,
        time_limit=300,
        mip_rel_gap=0.02
    )

    solve_time = time.time() - start - build_time

    print(f"\n  Solve time: {solve_time:.2f} seconds")
    print(f"  Status: {results['status']}")
    print(f"  Objective: {results['objective_value']:.2f}")

    if results['objective_value'] is not None:
        solution = model.get_solution()
        on_time = sum(1 for _, m in solution['otif_metrics'].items() if not m['late'])
        print(f"\n  OTIF: {on_time}/{data['n_orders']} orders on-time ({on_time/data['n_orders']*100:.1f}%)")
        print("\n  SUCCESS! Large-scale example structure is working correctly.")

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()
