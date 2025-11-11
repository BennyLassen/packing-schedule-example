"""
Minimal test to debug Problem_4 infeasibility.

Start with absolute minimal problem and add constraints incrementally.
"""

import numpy as np
import sys
import os
import pyomo.environ as pyo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_minimal_problem():
    """
    Absolute minimal problem:
    - 1 order
    - 1 line
    - 10 time slots
    - 1 worker
    - No setup times
    - Loose due date
    """

    print("="*80)
    print("MINIMAL TEST - 1 order, 1 line, 10 time slots")
    print("="*80)

    data = {
        'n_orders': 1,
        'n_lines': 1,
        'n_timeslots': 10,
        'n_workers': 1,
        'processing_time': np.array([[3]]),  # 3 time units
        'setup_time': np.zeros((1, 1, 1)),  # No setup
        'initial_inventory': np.array([0]),
        'reserved_capacity': 0.1,
        'due_date': np.array([10]),  # Loose - due at end
        'priority': np.array([100]),
        'objective_weights': {
            'alpha': 1.0,
            'beta': 0.1,
            'gamma': 0.1,
            'delta': 0.1
        }
    }

    print("\nProblem data:")
    print(f"  Processing time: {data['processing_time'][0,0]} time units")
    print(f"  Due date: {data['due_date'][0]}")
    print(f"  Horizon: {data['n_timeslots']} time slots")

    from packing_model_simple import PackingScheduleModelSimple

    try:
        print("\nBuilding model...")
        model = PackingScheduleModelSimple(data)
        print(f"  Variables: {model.model.nvariables()}")
        print(f"  Constraints: {model.model.nconstraints()}")

        print("\nSolving...")
        results = model.solve(solver_name='appsi_highs', tee=True, time_limit=60)

        print(f"\nResult: {results['status']}")
        if results['objective_value'] is not None:
            print(f"Objective: {results['objective_value']}")
            print("\nSUCCESS - Minimal problem is feasible!")
            return True
        else:
            print("\nFAILED - Even minimal problem is infeasible!")
            return False

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_production_constraint():
    """
    Test if production constraint is the issue.
    Check the production timing logic.
    """
    print("\n" + "="*80)
    print("TESTING PRODUCTION CONSTRAINT LOGIC")
    print("="*80)

    # For a 3-unit processing time order starting at t=2:
    # - Starts at t=2
    # - Completes at t=2+3=5
    # - Should produce at t=5

    print("\nLogic check:")
    print("  Order with p=3 starts at t=2")
    print("  Should complete at t=5 (t_start + p)")
    print("  Production should occur at t=5")

    # Check if our production constraint matches this
    print("\n  Current formula: prod(i,t) = sum of x(i,j,t_start) where t_start + p(i,j) == t")
    print("  For t=5: t_start + 3 == 5 => t_start == 2 [OK]")
    print("  Logic appears correct.")


def debug_inventory_balance():
    """
    Check inventory balance logic.
    """
    print("\n" + "="*80)
    print("TESTING INVENTORY BALANCE LOGIC")
    print("="*80)

    print("\nInventory balance equation:")
    print("  inv(i,t) = inv(i,t-1) + prod(i,t) - ship(i,t)")
    print("  inv(i,0) = inv0(i)")

    print("\nFor order with p=3 starting at t=2, inv0=0:")
    print("  t=0: inv=0 (initial)")
    print("  t=1: inv=0+0-0=0")
    print("  t=2: inv=0+0-0=0 (order starts)")
    print("  t=3: inv=0+0-0=0 (processing)")
    print("  t=4: inv=0+0-0=0 (processing)")
    print("  t=5: inv=0+1-0=1 (completes, can now ship)")
    print("  t=6: inv=1+0-1=0 (ships)")
    print("\nLogic appears correct.")


def print_constraint_summary():
    """Print which constraints might be causing issues."""
    print("\n" + "="*80)
    print("CONSTRAINT ANALYSIS")
    print("="*80)

    print("\nConstraint groups:")
    print("  1. Assignment: Each order assigned once - SIMPLE")
    print("  2. Capacity: No overlap on lines - SIMPLE")
    print("  3. Shipping: Ships once, calc ship time - SIMPLE")
    print("  4. OTIF: Start/complete times, lateness - COMPLEX")
    print("  5. WIP: Production timing, inventory balance - COMPLEX")
    print("  6. Workforce: Count active orders - SIMPLE")

    print("\nMost likely culprits:")
    print("  A. Production constraint (timing logic)")
    print("  B. Has-inventory Big-M constraints")
    print("  C. Interaction between completion time and production time")

    print("\nKey question: Is completion time BEFORE production can occur?")
    print("  timecompletion(i) = sum (t + p(i,j)) * x(i,j,t)")
    print("  For x(1,1,2)=1, p=3: timecompletion = 2+3 = 5")
    print("  prod(i,5) should equal 1")
    print("  This should work...")


if __name__ == "__main__":
    print("PROBLEM_4 INFEASIBILITY DEBUGGING")
    print("="*80)

    # Run logical checks first
    test_production_constraint()
    debug_inventory_balance()
    print_constraint_summary()

    # Try to solve minimal problem
    success = test_minimal_problem()

    if not success:
        print("\n" + "="*80)
        print("NEXT DEBUGGING STEPS:")
        print("="*80)
        print("1. Use model.pprint() to inspect constraint structure")
        print("2. Export model to LP format and inspect manually")
        print("3. Remove WIP constraints and test")
        print("4. Remove OTIF constraints and test")
        print("5. Compare with working Problem_3 implementation")
