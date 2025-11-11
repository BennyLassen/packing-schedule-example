"""
Example usage of the Packing Schedule Optimization Model

This script demonstrates how to:
1. Prepare input data
2. Create and configure the model
3. Solve the optimization problem
4. Extract and visualize results
"""

import numpy as np
from packing_model import PackingScheduleModel


def create_sample_data():
    """
    Create sample input data for the packing schedule problem.

    Returns:
        dict: Dictionary containing all required input parameters
    """

    # Problem dimensions
    n_orders = 5        # Number of packing orders
    n_lines = 3         # Number of production lines
    n_timeslots = 20    # Number of time slots (e.g., 20 x 15min = 5 hours)
    n_workers = 4       # Number of workers

    # Processing times: p[i, j] - time for order i on line j
    # Each order can be processed on different lines with different times
    processing_time = np.array([
        [3, 4, 5],    # Order 1: 3 time units on line 1, 4 on line 2, 5 on line 3
        [4, 3, 4],    # Order 2
        [2, 2, 3],    # Order 3
        [5, 4, 6],    # Order 4
        [3, 3, 4],    # Order 5
    ])

    # Setup times: s[i, k, j] - setup time between orders i and k on line j
    # For simplicity, using a constant setup time of 1 unit
    setup_time = np.ones((n_orders, n_orders, n_lines))
    np.fill_diagonal(setup_time[:, :, 0], 0)  # No setup when same order
    np.fill_diagonal(setup_time[:, :, 1], 0)
    np.fill_diagonal(setup_time[:, :, 2], 0)

    # Worker availability: a[w, t] - worker w available at time t
    # All workers available for all time slots in this simple example
    worker_availability = np.ones((n_workers, n_timeslots))

    # Optional: Make some workers unavailable at certain times
    worker_availability[0, 15:] = 0  # Worker 1 unavailable after time 15
    worker_availability[3, :5] = 0   # Worker 4 unavailable before time 5

    # Initial inventory: inv0[i] - initial stock for order i
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity: fraction of capacity to keep in reserve
    reserved_capacity = 0.1  # 10% reserved

    # Due dates: due[i] - due date for order i
    due_date = np.array([10, 12, 8, 15, 18])

    # Priority: priority[i] - priority weight for order i (1-100)
    priority = np.array([80, 90, 70, 95, 85])

    # Target workforce level
    workforce_target = 2

    # Objective function weights
    objective_weights = {
        'alpha': 1.0,   # Weight for OTIF term
        'beta': 0.5,    # Weight for WIP term
        'gamma': 0.3,   # Weight for workforce term
        'delta': 0.2    # Weight for line utilization term
    }

    # Compile all data into a dictionary
    data = {
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

    return data


def main():
    """
    Main function to demonstrate the packing schedule optimization.
    """

    print("="*80)
    print("PACKING SCHEDULE OPTIMIZATION - EXAMPLE")
    print("="*80)

    # Step 1: Create sample data
    print("\n[Step 1] Creating sample data...")
    data = create_sample_data()

    print(f"  - Number of orders: {data['n_orders']}")
    print(f"  - Number of lines: {data['n_lines']}")
    print(f"  - Number of time slots: {data['n_timeslots']}")
    print(f"  - Number of workers: {data['n_workers']}")

    # Step 2: Create the optimization model
    print("\n[Step 2] Building optimization model...")
    model = PackingScheduleModel(data)
    print("  - Model created successfully")
    print(f"  - Number of variables: {model.model.nvariables()}")
    print(f"  - Number of constraints: {model.model.nconstraints()}")

    # Step 3: Solve the model
    print("\n[Step 3] Solving the optimization problem...")
    print("  - Using HiGHS solver")

    try:
        # Solve with HiGHS
        results = model.solve(
            solver_name='appsi_highs',
            tee=False,  # Set to True to see solver output
            time_limit=300  # 5 minute time limit
        )

        # Display results
        print(f"\n  - Solver status: {results['status']}")
        print(f"  - Termination condition: {results['termination_condition']}")

        if results['objective_value'] is not None:
            print(f"  - Objective value: {results['objective_value']:.2f}")

            # Step 4: Extract and display solution
            print("\n[Step 4] Extracting solution...")
            model.print_solution_summary()

            # Optional: Save solution to file
            solution = model.get_solution()
            print("\n[Step 5] Solution extracted successfully")
            print(f"  - Total assignments: {len(solution['assignments'])}")
            print(f"  - Orders tracked: {len(solution['otif_metrics'])}")

        else:
            print("\n  No optimal solution found. Check model formulation and data.")

    except Exception as e:
        print(f"\n  Error during optimization: {str(e)}")
        print("\n  This might happen if:")
        print("    1. HiGHS solver is not installed")
        print("    2. The problem is infeasible")
        print("    3. The problem is too large for available memory")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)


def create_small_example():
    """
    Create a minimal example for quick testing.

    Returns:
        dict: Minimal problem instance
    """

    # Very small problem: 2 orders, 2 lines, 10 time slots, 2 workers
    n_orders = 2
    n_lines = 2
    n_timeslots = 10
    n_workers = 2

    processing_time = np.array([
        [2, 3],  # Order 1
        [3, 2],  # Order 2
    ])

    setup_time = np.ones((n_orders, n_orders, n_lines))
    np.fill_diagonal(setup_time[:, :, 0], 0)
    np.fill_diagonal(setup_time[:, :, 1], 0)

    worker_availability = np.ones((n_workers, n_timeslots))

    initial_inventory = np.zeros(n_orders, dtype=int)

    reserved_capacity = 0.1

    due_date = np.array([5, 8])
    priority = np.array([80, 90])

    workforce_target = 1

    objective_weights = {
        'alpha': 1.0,
        'beta': 0.5,
        'gamma': 0.3,
        'delta': 0.2
    }

    data = {
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

    return data


def run_small_example():
    """Run the minimal example for quick testing."""

    print("\n" + "="*80)
    print("RUNNING SMALL EXAMPLE (for quick testing)")
    print("="*80)

    data = create_small_example()
    model = PackingScheduleModel(data)

    print(f"\nProblem size:")
    print(f"  - Orders: {data['n_orders']}")
    print(f"  - Lines: {data['n_lines']}")
    print(f"  - Time slots: {data['n_timeslots']}")
    print(f"  - Workers: {data['n_workers']}")

    results = model.solve(solver_name='appsi_highs', tee=False)

    if results['objective_value'] is not None:
        model.print_solution_summary()


if __name__ == "__main__":
    # Run the main example
    main()

    # Uncomment to run small example instead
    # run_small_example()
