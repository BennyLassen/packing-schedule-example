"""
Example usage of the Simple Packing Schedule Model (Problem 4.1)

This script demonstrates how to set up and solve a packing schedule optimization
problem using the Problem 4.1 formulation.
"""
import sys
import os
# Add parent directory to path to import packing_model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from simple_model import PackingScheduleModel


def create_simple_problem():
    """
    Create a simple test problem for Problem 4.1.

    Returns:
        dict: Problem data with all required parameters
    """
    # Problem dimensions
    n_orders = 3
    n_lines = 2
    n_timeslots = 20
    n_workers = 3

    # Processing times (order i on line j)
    processing_time = np.array([
        [3, 4],  # Order 1
        [2, 3],  # Order 2
        [4, 5],  # Order 3
    ])

    # Setup times (between orders i and k on line j)
    setup_time = np.zeros((n_orders, n_orders, n_lines))
    setup_time[0, 1, :] = [1, 1]  # Setup between order 1 and 2
    setup_time[1, 0, :] = [1, 1]  # Setup between order 2 and 1
    setup_time[0, 2, :] = [2, 2]  # Setup between order 1 and 3
    setup_time[2, 0, :] = [2, 2]  # Setup between order 3 and 1
    setup_time[1, 2, :] = [1, 1]  # Setup between order 2 and 3
    setup_time[2, 1, :] = [1, 1]  # Setup between order 3 and 2

    # Worker availability (all workers available all the time for simplicity)
    worker_availability = np.ones((n_workers, n_timeslots))

    # Initial inventory (no initial inventory)
    initial_inventory = np.zeros(n_orders)

    # Due dates
    due_date = np.array([10, 12, 15])

    # Priority weights
    priority = np.array([100, 80, 90])

    # Reserved capacity (10% reserve)
    reserved_capacity = 0.1

    # Workforce target
    workforce_target = 2

    # Objective weights
    objective_weights = {
        'alpha': 1.0,   # OTIF weight
        'beta': 0.5,    # WIP weight
        'gamma': 0.3,   # Workforce weight
        'delta': 0.2,   # Line utilization weight
        'omega': 0.1    # Worker movement weight
    }

    # Package all data
    data = {
        'n_orders': n_orders,
        'n_lines': n_lines,
        'n_timeslots': n_timeslots,
        'n_workers': n_workers,
        'processing_time': processing_time,
        'setup_time': setup_time,
        'worker_availability': worker_availability,
        'initial_inventory': initial_inventory,
        'due_date': due_date,
        'priority': priority,
        'reserved_capacity': reserved_capacity,
        'workforce_target': workforce_target,
        'objective_weights': objective_weights
    }

    return data


def main():
    """Run the example problem."""
    print("="*80)
    print("Simple Packing Schedule Model - Problem 4.1 Example")
    print("="*80)

    # Create problem data
    print("\nCreating problem data...")
    data = create_simple_problem()
    print(f"Problem size: {data['n_orders']} orders, {data['n_lines']} lines, "
          f"{data['n_timeslots']} time slots, {data['n_workers']} workers")

    # Create model
    print("\nBuilding optimization model...")
    model = PackingScheduleModel(data)
    print("Model built successfully!")

    # Optional: Write LP file for inspection
    print("\nWriting LP file for inspection...")
    model.write_lp('simple_model_example.lp')

    # Solve the model
    print("\nSolving the optimization problem...")
    results = model.solve(
        solver_name='appsi_highs',
        tee=True,
        time_limit=300  # 5 minute time limit
    )

    # Print results
    print("\n" + "="*80)
    print("OPTIMIZATION RESULTS")
    print("="*80)
    print(f"Status: {results['status']}")
    print(f"Termination: {results['termination_condition']}")
    if results['objective_value'] is not None:
        print(f"Objective Value: {results['objective_value']:.2f}")
    if results['solve_time'] is not None:
        print(f"Solve Time: {results['solve_time']:.2f} seconds")

    # Print solution summary
    if results['termination_condition'] == 'optimal':
        model.print_solution_summary()

        # Export detailed solution
        print("\nExporting detailed solution...")
        model.export_solution('simple_model_solution.txt')

    print("\n" + "="*80)
    print("Example completed!")
    print("="*80)


if __name__ == '__main__':
    main()
