"""
Example usage of the Problem_4_1 Packing Schedule Model

This script demonstrates how to use the Problem_4_1 model with a small example.
"""

import numpy as np
from packing_model_problem_4_1_c import PackingScheduleModelProblem41c


def create_simple_example():
    """
    Create a simple example dataset for testing.

    Returns:
        Dictionary with all required input data.
    """
    # Problem dimensions
    n_orders = 3
    n_lines = 2
    n_timeslots = 20
    n_workers = 5

    # Processing times: 3 orders x 2 lines
    # Each order takes different time on each line
    processing_time = np.array([
        [4, 5],  # Order 1: 4 slots on line 1, 5 slots on line 2
        [3, 4],  # Order 2: 3 slots on line 1, 4 slots on line 2
        [5, 3],  # Order 3: 5 slots on line 1, 3 slots on line 2
    ])

    # Initial inventory: start with no inventory
    initial_inventory = np.array([0, 0, 0])

    # Reserved capacity: reserve 10% of capacity
    reserved_capacity = 0.1

    # Due dates: orders due at different times
    due_date = np.array([10, 12, 15])

    # Priority: all orders have equal priority
    priority = np.array([1, 1, 1])

    # Objective weights
    objective_weights = {
        'beta': 1.0,    # WIP weight
        'gamma': 0.5,   # Workforce variability weight
        'delta': 0.3    # Total not utilized weight
    }

    return {
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


def main():
    """Main function to run the example."""
    print("="*80)
    print("Problem_4_1 Packing Schedule Model - Simple Example")
    print("="*80)

    # Create example data
    print("\nCreating example data...")
    data = create_simple_example()

    print(f"  Orders: {data['n_orders']}")
    print(f"  Lines: {data['n_lines']}")
    print(f"  Time slots: {data['n_timeslots']}")
    print(f"  Workers: {data['n_workers']}")

    # Create and solve model
    print("\nBuilding model...")
    model = PackingScheduleModelProblem41c(data)

    print("Solving model...")
    results = model.solve(
        solver_name='appsi_highs',
        tee=True,
        time_limit=300,  # 5 minutes
        mip_rel_gap=0.01  # 1% gap
    )

    # Display results
    print("\n" + "="*80)
    print("SOLVER RESULTS")
    print("="*80)
    print(f"Status: {results['status']}")
    print(f"Objective value: {results['objective_value']}")
    print(f"Solve time: {results['solve_time']:.2f} seconds")

    if results['objective_value'] is not None:
        # Print detailed solution summary
        model.print_solution_summary()

        # Get detailed solution
        solution = model.get_solution()

        # Print inventory details
        print("\n" + "="*80)
        print("INVENTORY DETAILS")
        print("="*80)
        for order_id, inv_data in solution['inventory'].items():
            print(f"\nOrder {order_id}:")
            inv_str = ", ".join([f"t={t}:{qty}" for t, qty in inv_data.items() if qty > 0])
            print(f"  Inventory: {inv_str if inv_str else 'None'}")

        # Print workforce details
        print("\n" + "="*80)
        print("WORKFORCE UTILIZATION")
        print("="*80)
        print("Time slot | Workers used")
        print("-" * 30)
        for t, workers in solution['workforce'].items():
            if workers > 0:
                print(f"{t:9d} | {workers:12d}")

    else:
        print("\nNo solution found!")


if __name__ == "__main__":
    main()
