"""
Test Script for Problem_4 Simplified Implementation

Tests the simplified packing schedule model with a small example.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packing_model_simple import PackingScheduleModelSimple


def create_test_data():
    """Create a simple test problem for Problem_4."""

    n_orders = 5
    n_lines = 2
    n_timeslots = 20
    n_workers = 2  # Used for counting only, not explicit assignment

    print(f"Test problem dimensions:")
    print(f"  Orders: {n_orders}")
    print(f"  Lines: {n_lines}")
    print(f"  Time slots: {n_timeslots}")
    print(f"  Workers (counting): {n_workers}")

    np.random.seed(42)

    # Processing times: Different for each line
    processing_time = np.array([
        [3, 4],    # Order 1: Faster on Line 1
        [4, 3],    # Order 2: Faster on Line 2
        [2, 3],    # Order 3: Faster on Line 1
        [4, 2],    # Order 4: Much faster on Line 2
        [3, 4],    # Order 5: Faster on Line 1
    ])

    # Setup times: 2 time units between different orders, 0 within same "batch"
    # For simplicity, assume orders 1-2 can batch, orders 3-4 can batch, order 5 standalone
    setup_time = np.zeros((n_orders, n_orders, n_lines))
    for i in range(n_orders):
        for k in range(n_orders):
            for j in range(n_lines):
                if i == k:
                    setup_time[i, k, j] = 0
                elif (i < 2 and k < 2) or (i >= 2 and i < 4 and k >= 2 and k < 4):
                    # Within batch: no setup
                    setup_time[i, k, j] = 0
                else:
                    # Between batches: 2 time units setup
                    setup_time[i, k, j] = 2

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity
    reserved_capacity = 0.1  # 10% reserved (looser)

    # Due dates: All very loose to ensure feasibility
    due_date = np.array([20, 20, 20, 20, 20])  # All can be completed by end

    # Priorities
    priority = np.array([75, 85, 95, 60, 80])

    # Objective weights (Problem_4 - 4 terms)
    objective_weights = {
        'alpha': 10.0,   # High OTIF weight
        'beta': 0.2,     # Low WIP weight
        'gamma': 0.1,    # Low workforce variability
        'delta': 0.5     # Moderate line utilization cost
    }

    return {
        'n_orders': n_orders,
        'n_lines': n_lines,
        'n_timeslots': n_timeslots,
        'n_workers': n_workers,
        'processing_time': processing_time,
        'setup_time': setup_time,
        'initial_inventory': initial_inventory,
        'reserved_capacity': reserved_capacity,
        'due_date': due_date,
        'priority': priority,
        'objective_weights': objective_weights
    }


def main():
    print("="*80)
    print("PROBLEM_4 SIMPLIFIED MODEL TEST")
    print("="*80)

    print("\n[Step 1] Creating test data...")
    data = create_test_data()

    print("\n[Step 2] Building model...")
    try:
        model = PackingScheduleModelSimple(data)
        print(f"  Model built successfully!")
        print(f"  Variables: {model.model.nvariables():,}")
        print(f"  Constraints: {model.model.nconstraints():,}")
    except Exception as e:
        print(f"  ERROR building model: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n[Step 3] Solving model...")
    try:
        results = model.solve(
            solver_name='appsi_highs',
            tee=True,  # Enable output to see what's happening
            time_limit=120,
            mip_rel_gap=0.01
        )

        print(f"\n  Solve Status: {results['status']}")
        print(f"  Objective Value: {results['objective_value']}")
        if results['solve_time']:
            print(f"  Solve Time: {results['solve_time']:.2f} seconds")

    except Exception as e:
        print(f"  ERROR solving model: {e}")
        import traceback
        traceback.print_exc()
        return

    if results['objective_value'] is not None:
        print("\n[Step 4] Extracting solution...")
        try:
            model.print_solution_summary()
        except Exception as e:
            print(f"  ERROR extracting solution: {e}")
            import traceback
            traceback.print_exc()
            return

        print("\n[Step 5] Verification...")
        solution = model.get_solution()

        # Check that all orders are assigned
        assigned_orders = set(a['order'] for a in solution['assignments'])
        if len(assigned_orders) == data['n_orders']:
            print(f"  OK: All {data['n_orders']} orders assigned")
        else:
            print(f"  ERROR: Only {len(assigned_orders)}/{data['n_orders']} orders assigned")

        # Check workforce counting
        max_workers = solution['workforce_summary']['max']
        if max_workers <= data['n_workers']:
            print(f"  OK: Max workforce ({max_workers}) within limit ({data['n_workers']})")
        else:
            print(f"  ERROR: Max workforce ({max_workers}) exceeds limit ({data['n_workers']})")

        # Check line usage
        active_lines = sum(1 for used in solution['line_usage'].values() if used)
        print(f"  INFO: {active_lines}/{data['n_lines']} lines activated")

        # Check OTIF
        on_time = sum(1 for _, m in solution['otif_metrics'].items() if not m['late'])
        print(f"  INFO: {on_time}/{data['n_orders']} orders delivered on-time")

        print("\n" + "="*80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*80)

    else:
        print("\n" + "="*80)
        print("TEST FAILED - No solution found")
        print("="*80)


if __name__ == "__main__":
    main()
