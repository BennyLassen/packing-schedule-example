"""
Example usage of Problem_4_1_c2 Packing Schedule Model

This script demonstrates how to use the Problem_4_1_c2 model with sample data.
"""

import numpy as np
import sys
import os

# Add src directory to path to import simple_packing_model
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from simple_packing_model import PackingScheduleModelProblem4_1_c2


def create_sample_data():
    """
    Create sample problem data for the Problem_4_1_c2 model.

    Returns:
        Dictionary with all required input data.
    """

    # Problem dimensions
    n_unique_types = 2   # U: number of unique packing types
    n_orders = 4         # I: number of production orders
    n_demands = 2        # D: number of demand/shipping requirements
    n_lines = 2          # J: number of production lines

    # Planning horizon
    T_max = 60.0

    # Processing times p(u,j): [types x lines]
    # Each type has different processing times on different lines
    processing_time = np.array([
        [10.0, 12.0],  # Type 1: 10 on line 1, 12 on line 2
        [15.0, 13.0],  # Type 2: 15 on line 1, 13 on line 2
    ])

    # Setup times s(u,v): [types x types]
    # Time to change from type u to type v
    setup_time = np.array([
        [0.0, 5.0],   # From type 1: no setup to 1, 5 to type 2
        [5.0, 0.0],   # From type 2: 5 to type 1, no setup to 2
    ])

    # Initial inventory inv0(u): [types]
    initial_inventory = np.array([0, 0])

    # Order types: which type each order produces
    # Orders 1,2 are type 1; Orders 3,4 are type 2
    order_type = np.array([1, 1, 2, 2])

    # Demand data
    # Each demand specifies: due date, product type, quantity

    # due(d): Due dates for each demand
    due_date = np.array([20.0, 40.0])

    # prodtype(d): Product type for each demand
    demand_type = np.array([1, 2])

    # qty(d): Quantity for each demand
    demand_qty = np.array([2, 2])

    # priority(i): Priority weights for orders (higher = more important)
    priority = np.array([10, 10, 10, 10])

    # Objective weights
    objective_weights = {
        'alpha': 1.0,  # OTIF weight
        'beta': 1.0,    # WIP weight
        'gamma': 2.0,   # Workforce variability weight
        'delta': 0.5    # Not utilized weight
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
    """
    Main function to run the example.
    """
    print("="*80)
    print("Problem_4_1_c2 Packing Schedule Model - Example")
    print("="*80)

    # Create sample data
    print("\n1. Creating sample problem data...")
    data = create_sample_data()

    print(f"   - Unique types: {data['n_unique_types']}")
    print(f"   - Production orders: {data['n_orders']}")
    print(f"   - Demands: {data['n_demands']}")
    print(f"   - Production lines: {data['n_lines']}")
    print(f"   - Planning horizon: {data['T_max']}")
    print(f"   - Orders by type: {data['order_type']}")
    print(f"   - Demand quantities: {data['demand_qty']} for types {data['demand_type']}")
    print(f"   - Initial inventory: {data['initial_inventory']}")

    # Create model
    print("\n2. Building optimization model...")
    model = PackingScheduleModelProblem4_1_c2(data)
    print("   Model built successfully!")

    # Display model statistics
    print(f"\n3. Model Statistics:")
    print(f"   - Variables: {len(model.model.component_map(pyo.Var))}")
    print(f"   - Constraints: {len(model.model.component_map(pyo.Constraint))}")

    # Solve the model
    print("\n4. Solving the model...")
    print("   (This may take a few moments...)")

    try:
        results = model.solve(
            solver_name='appsi_highs',
            tee=False,
            time_limit=300,  # 5 minutes
            mip_rel_gap=0.01  # 1% gap
        )
    except RuntimeError as e:
        print(f"\n   Solver encountered an error: {str(e)}")
        print("\n   This might indicate an infeasible model.")
        print("   Try adjusting problem parameters or relaxing constraints.")
        return

    print(f"\n5. Solver Results:")
    print(f"   - Status: {results['status']}")
    print(f"   - Objective Value: {results['objective_value']}")
    print(f"   - Solve Time: {results['solve_time']:.2f} seconds" if results['solve_time'] else "")

    # Print solution summary
    if results['objective_value'] is not None:
        print("\n6. Solution Details:")
        model.print_solution_summary()

        # Print assignment matrix
        model.print_assignment_matrix()

        # Print shipped matrix
        model.print_shipped_matrix()

        # Print inventory matrix
        model.print_inventory_matrix()
    else:
        print("\n6. No feasible solution found.")
        print("   Try adjusting the problem parameters or relaxing constraints.")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    import pyomo.environ as pyo
    main()
