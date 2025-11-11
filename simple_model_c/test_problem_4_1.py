"""
Test script for Problem_4_1 Packing Schedule Model

Verifies basic functionality and constraint satisfaction.
"""

import numpy as np
from packing_model_problem_4_1 import PackingScheduleModelProblem41
import pyomo.environ as pyo


def test_minimal_problem():
    """
    Test with a minimal 2-order, 1-line problem.

    This should be solvable quickly and help verify basic functionality.
    """
    print("\n" + "="*80)
    print("TEST 1: Minimal Problem (2 orders, 1 line)")
    print("="*80)

    # Minimal problem
    n_orders = 2
    n_lines = 1
    n_timeslots = 10
    n_workers = 2

    processing_time = np.array([
        [3],  # Order 1: 3 time slots
        [2],  # Order 2: 2 time slots
    ])

    initial_inventory = np.array([0, 0])
    reserved_capacity = 0.1
    due_date = np.array([5, 8])
    priority = np.array([1, 1])

    objective_weights = {
        'beta': 1.0,
        'gamma': 0.5,
        'delta': 0.3
    }

    data = {
        'n_orders': n_orders,
        'n_lines': n_lines,
        'n_timeslots': n_timeslots,
        'n_workers': n_workers,
        'processing_time': processing_time,
        'initial_inventory': initial_inventory,
        'reserved_capacity': reserved_capacity,
        'due_date': due_date,
        'priority': priority,
        'objective_weights': objective_weights
    }

    # Create and solve
    model = PackingScheduleModelProblem41(data)
    results = model.solve(solver_name='appsi_highs', tee=False, time_limit=60)

    print(f"Status: {results['status']}")
    print(f"Objective: {results['objective_value']}")

    if results['objective_value'] is not None:
        solution = model.get_solution()
        print(f"Assignments found: {len(solution['assignments'])}")
        print(f"Workforce max: {solution['workforce_summary']['max']}")
        print(f"Workforce min: {solution['workforce_summary']['min']}")

        # Verify constraints
        verify_solution(model.model, solution)
        print("✓ Test 1 PASSED")
        return True
    else:
        print("✗ Test 1 FAILED: No solution found")
        return False


def test_standard_problem():
    """
    Test with a standard problem (3 orders, 2 lines).
    """
    print("\n" + "="*80)
    print("TEST 2: Standard Problem (3 orders, 2 lines)")
    print("="*80)

    n_orders = 3
    n_lines = 2
    n_timeslots = 15
    n_workers = 4

    processing_time = np.array([
        [4, 5],
        [3, 4],
        [5, 3],
    ])

    initial_inventory = np.array([0, 0, 0])
    reserved_capacity = 0.15
    due_date = np.array([8, 10, 12])
    priority = np.array([1, 1, 1])

    objective_weights = {
        'beta': 1.0,
        'gamma': 0.5,
        'delta': 0.3
    }

    data = {
        'n_orders': n_orders,
        'n_lines': n_lines,
        'n_timeslots': n_timeslots,
        'n_workers': n_workers,
        'processing_time': processing_time,
        'initial_inventory': initial_inventory,
        'reserved_capacity': reserved_capacity,
        'due_date': due_date,
        'priority': priority,
        'objective_weights': objective_weights
    }

    # Create and solve
    model = PackingScheduleModelProblem41(data)
    results = model.solve(solver_name='appsi_highs', tee=False, time_limit=120)

    print(f"Status: {results['status']}")
    print(f"Objective: {results['objective_value']}")

    if results['objective_value'] is not None:
        solution = model.get_solution()
        print(f"Assignments found: {len(solution['assignments'])}")
        print(f"On-time orders: {sum(1 for s in solution['shipping'].values() if s['on_time'])}/{n_orders}")

        # Verify constraints
        verify_solution(model.model, solution)
        print("✓ Test 2 PASSED")
        return True
    else:
        print("✗ Test 2 FAILED: No solution found")
        return False


def verify_solution(model, solution):
    """
    Verify that the solution satisfies basic constraints.

    Args:
        model: Pyomo model
        solution: Solution dictionary
    """
    print("\nVerifying solution constraints...")

    # Check 1: Each order assigned exactly once
    assert len(solution['assignments']) == model.n_orders, \
        f"Expected {model.n_orders} assignments, got {len(solution['assignments'])}"
    print("  ✓ Each order assigned exactly once")

    # Check 2: No line overlap (same line used at same time)
    for j in range(1, model.n_lines + 1):
        line_usage = {}
        for assignment in solution['assignments']:
            if assignment['line'] == j:
                start = assignment['start']
                end = assignment['completion']
                for t in range(start, end):
                    assert t not in line_usage, \
                        f"Line {j} has overlap at time {t}"
                    line_usage[t] = assignment['order']
    print("  ✓ No line overlaps")

    # Check 3: Workforce consistency
    ws = solution['workforce_summary']
    assert ws['range'] == ws['max'] - ws['min'], \
        f"Workforce range mismatch: {ws['range']} != {ws['max'] - ws['min']}"
    print("  ✓ Workforce range consistent")

    # Check 4: All orders shipped
    assert len(solution['shipping']) == model.n_orders, \
        f"Expected {model.n_orders} shipments, got {len(solution['shipping'])}"
    print("  ✓ All orders shipped")

    print("All constraint checks passed!")


def main():
    """Run all tests."""
    print("="*80)
    print("Problem_4_1 Model Test Suite")
    print("="*80)

    test_results = []

    # Run tests
    test_results.append(("Minimal Problem", test_minimal_problem()))
    test_results.append(("Standard Problem", test_standard_problem()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
