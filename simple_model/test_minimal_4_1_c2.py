"""
Minimal test case for Problem_4_1_c2 to debug infeasibility
"""

import numpy as np
from packing_model_problem_4_1_c2 import PackingScheduleModelProblem4_1_c2


def create_minimal_data():
    """
    Create the simplest possible problem data.
    """

    # Minimal problem: 1 type, 1 order, 1 demand, 1 line
    n_unique_types = 1
    n_orders = 1
    n_demands = 1
    n_lines = 1
    T_max = 50.0

    # Processing times: very simple
    processing_time = np.array([[10.0]])  # Type 1 on line 1 takes 10 units

    # Setup times: no setup (all zeros)
    setup_time = np.array([[0.0]])

    # Initial inventory: empty
    initial_inventory = np.array([0])

    # Order data
    order_type = np.array([1])  # Order 1 is type 1
    priority = np.array([1])

    # Demand data
    due_date = np.array([15.0])  # Due at time 15
    demand_type = np.array([1])   # Demand for type 1
    demand_qty = np.array([1])    # Quantity 1

    # Simple objective weights
    objective_weights = {
        'beta': 1.0,
        'gamma': 0.0,
        'delta': 0.0
    }

    data = {
        'n_unique_types': n_unique_types,
        'n_orders': n_orders,
        'n_demands': n_demands,
        'n_lines': n_lines,
        'T_max': T_max,
        'processing_time': processing_time,
        'setup_time': setup_time,
        'initial_inventory': initial_inventory,
        'order_type': order_type,
        'due_date': due_date,
        'demand_type': demand_type,
        'demand_qty': demand_qty,
        'priority': priority,
        'objective_weights': objective_weights
    }

    return data


def main():
    print("="*80)
    print("Minimal Test Case for Problem_4_1_c2")
    print("="*80)

    # Create minimal data
    print("\nCreating minimal problem data...")
    data = create_minimal_data()
    print(f"  Types: {data['n_unique_types']}, Orders: {data['n_orders']}, ")
    print(f"  Demands: {data['n_demands']}, Lines: {data['n_lines']}")

    # Build model
    print("\nBuilding model...")
    model = PackingScheduleModelProblem4_1_c2(data)
    print("  Model built successfully!")

    # Write LP file for inspection
    print("\nWriting model to LP file for inspection...")
    model.model.write('minimal_test.lp', io_options={'symbolic_solver_labels': True})
    print("  Model written to minimal_test.lp")

    # Try to solve
    print("\nAttempting to solve...")
    try:
        results = model.solve(solver_name='appsi_highs', tee=True)
        print(f"\nStatus: {results['status']}")
        print(f"Objective: {results['objective_value']}")

        if results['objective_value'] is not None:
            model.print_solution_summary()
    except RuntimeError as e:
        print(f"\nSolver error: {e}")
        print("\nModel is likely infeasible. Check minimal_test.lp for details.")


if __name__ == "__main__":
    import pyomo.environ as pyo
    main()
