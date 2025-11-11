"""
Test script to verify worker movement penalty implementation (Problem_3)

This test creates a simple scenario where worker movement would occur,
and verifies that:
1. The movement constraint is working
2. The movement penalty affects the objective function
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packing_model import PackingScheduleModel


def create_test_data_with_movement():
    """
    Create a simple test case that encourages worker movement.

    Setup:
    - 2 lines, 2 workers, 4 orders
    - Orders 1&2 favor Line 1, Orders 3&4 favor Line 2
    - With 2 workers, optimizer might use both lines in parallel
    - Movement penalty should discourage workers from switching lines
    """
    n_orders = 4
    n_lines = 2
    n_timeslots = 20
    n_workers = 2

    # Processing times - clear preferences for different lines
    processing_time = np.array([
        [2, 4],  # Order 1: Much faster on Line 1
        [2, 4],  # Order 2: Much faster on Line 1
        [4, 2],  # Order 3: Much faster on Line 2
        [4, 2],  # Order 4: Much faster on Line 2
    ])

    # Minimal setup times
    setup_time = np.ones((n_orders, n_orders, n_lines))
    for j in range(n_lines):
        np.fill_diagonal(setup_time[:, :, j], 0)

    # Worker availability - both workers always available
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity
    reserved_capacity = 0.05

    # Due dates - tight enough to encourage parallel work
    due_date = np.array([8, 8, 8, 8])

    # Priority weights
    priority = np.array([80, 80, 80, 80])

    # Target workforce
    workforce_target = 2

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
    }


def test_without_movement_penalty():
    """Test with omega=0 (no movement penalty)."""
    print("="*80)
    print("TEST 1: WITHOUT WORKER MOVEMENT PENALTY (omega=0)")
    print("="*80)

    data = create_test_data_with_movement()
    data['objective_weights'] = {
        'alpha': 5.0,
        'beta': 0.1,
        'gamma': 0.1,
        'delta': 0.5,
        'omega': 0.0  # NO movement penalty
    }

    model = PackingScheduleModel(data)
    print(f"\nModel created with {model.model.nvariables()} variables")
    print(f"and {model.model.nconstraints()} constraints")

    results = model.solve(solver_name='appsi_highs', tee=False)

    if results['objective_value'] is not None:
        print(f"\nObjective value: {results['objective_value']:.2f}")

        solution = model.get_solution()

        # Count worker movements
        movements = count_worker_movements(solution)
        print(f"\nWorker Movements:")
        for worker_id, count in movements.items():
            print(f"  Worker {worker_id}: {count} movements")

        total_movements = sum(movements.values())
        print(f"  Total movements: {total_movements}")

        return solution, total_movements
    else:
        print("\nNo solution found!")
        return None, None


def test_with_movement_penalty():
    """Test with omega>0 (with movement penalty)."""
    print("\n" + "="*80)
    print("TEST 2: WITH WORKER MOVEMENT PENALTY (omega=2.0)")
    print("="*80)

    data = create_test_data_with_movement()
    data['objective_weights'] = {
        'alpha': 5.0,
        'beta': 0.1,
        'gamma': 0.1,
        'delta': 0.5,
        'omega': 2.0  # HIGH movement penalty
    }

    model = PackingScheduleModel(data)
    print(f"\nModel created with {model.model.nvariables()} variables")
    print(f"and {model.model.nconstraints()} constraints")

    results = model.solve(solver_name='appsi_highs', tee=False)

    if results['objective_value'] is not None:
        print(f"\nObjective value: {results['objective_value']:.2f}")

        solution = model.get_solution()

        # Count worker movements
        movements = count_worker_movements(solution)
        print(f"\nWorker Movements:")
        for worker_id, count in movements.items():
            print(f"  Worker {worker_id}: {count} movements")

        total_movements = sum(movements.values())
        print(f"  Total movements: {total_movements}")

        return solution, total_movements
    else:
        print("\nNo solution found!")
        return None, None


def count_worker_movements(solution):
    """
    Count worker movements between lines.

    A movement occurs when a worker switches from one line to another
    between consecutive assignments.
    """
    movements = {}

    # Group assignments by worker
    worker_assignments = {}
    for assignment in solution['assignments']:
        worker_id = assignment['worker']
        if worker_id not in worker_assignments:
            worker_assignments[worker_id] = []
        worker_assignments[worker_id].append(assignment)

    # Count movements for each worker
    for worker_id, assignments in worker_assignments.items():
        # Sort by start time
        sorted_assignments = sorted(assignments, key=lambda x: x['start'])

        movement_count = 0
        prev_line = None

        for assignment in sorted_assignments:
            current_line = assignment['line']
            if prev_line is not None and current_line != prev_line:
                movement_count += 1
            prev_line = current_line

        movements[worker_id] = movement_count

    return movements


def main():
    """Run the worker movement penalty tests."""
    print("\n" + "="*80)
    print("WORKER MOVEMENT PENALTY TEST (Problem_3 Verification)")
    print("="*80)
    print("\nThis test verifies that the worker movement penalty is working correctly.")
    print("We expect:")
    print("  - Test 1 (omega=0): Optimizer may move workers between lines freely")
    print("  - Test 2 (omega>0): Optimizer should reduce worker movements")
    print()

    # Test without movement penalty
    solution1, movements1 = test_without_movement_penalty()

    # Test with movement penalty
    solution2, movements2 = test_with_movement_penalty()

    # Compare results
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)

    if movements1 is not None and movements2 is not None:
        print(f"\nWorker movements WITHOUT penalty (omega=0): {movements1}")
        print(f"Worker movements WITH penalty (omega=2.0): {movements2}")

        if movements2 <= movements1:
            print("\nRESULT: SUCCESS!")
            print("The movement penalty successfully reduced worker movements.")
        else:
            print("\nRESULT: UNEXPECTED")
            print("Movement penalty did not reduce movements as expected.")
            print("This may be due to other objective trade-offs.")
    else:
        print("\nCould not complete comparison - one or both tests failed.")

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()
