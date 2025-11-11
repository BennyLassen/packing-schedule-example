"""
Initial Inventory Usage Example for Problem_3 Model

This example demonstrates how the optimizer uses existing inventory before
producing new orders. The scenario is designed to clearly show:

1. Initial inventory is consumed to fulfill early demands
2. Production is delayed until inventory is depleted
3. Only necessary production orders are scheduled
4. Single production line forces sequential decision-making

SCENARIO SETUP:
- 1 production line (forces sequential processing)
- 2 product types (Type 1 and Type 2)
- Initial inventory: 3 units of Type 1, 2 units of Type 2
- 3 demands to fulfill
- 4 production orders available (not all may be needed)

KEY INSIGHT:
The optimizer should use existing inventory first to meet demands,
only producing new units when inventory is insufficient.

EXPECTED BEHAVIOR:
- Demand 1 (Type 1, qty 2, due 10): Fulfilled from initial inventory
- Demand 2 (Type 2, qty 1, due 15): Fulfilled from initial inventory
- Demand 3 (Type 1, qty 3, due 30): Partially from inventory (1 unit),
  requires production of 2 more units
- Some production orders may not be scheduled at all if inventory is sufficient
"""

import numpy as np
import sys
import os

# Add src directory to path to import simple_packing_model
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from simple_packing_model import PackingScheduleModelProblem3


def create_inventory_test_data():
    """
    Create a scenario to test initial inventory usage.

    The key is to have enough initial inventory to partially fulfill demands,
    forcing the optimizer to decide when to use inventory vs. production.

    Returns:
        Dictionary with problem data focused on inventory management.
    """

    # Problem dimensions
    n_unique_types = 2   # Type 1 and Type 2
    n_orders = 4         # 4 production orders available (may not all be used)
    n_demands = 3        # 3 shipping demands to fulfill
    n_lines = 1          # Single line (forces sequential decisions)

    # Planning horizon
    T_max = 50.0

    # Processing times p(u,j): [types x lines]
    # Both types take 5 time units to produce on the single line
    processing_time = np.array([
        [5.0],   # Type 1: 5 time units on line 1
        [5.0],   # Type 2: 5 time units on line 1
    ])

    # Setup times s(u,v): [types x types]
    # Small setup time when switching between types
    setup_time = np.array([
        [0.0, 2.0],   # From Type 1: no setup to stay on 1, 2 units to switch to 2
        [2.0, 0.0],   # From Type 2: 2 units to switch to 1, no setup to stay on 2
    ])

    # Initial inventory inv0(u): [types]
    # THIS IS THE KEY: We have existing inventory
    initial_inventory = np.array([
        3,  # Type 1: 3 units already in inventory
        2,  # Type 2: 2 units already in inventory
    ])

    # Order types: which type each order produces
    # Orders 1,2 produce Type 1; Orders 3,4 produce Type 2
    order_type = np.array([1, 1, 2, 2])

    # Demand data
    # Demand 1: Type 1, quantity 2, due at time 10
    #   -> Should be fulfilled from initial inventory (have 3 units)
    # Demand 2: Type 2, quantity 1, due at time 15
    #   -> Should be fulfilled from initial inventory (have 2 units)
    # Demand 3: Type 1, quantity 3, due at time 30
    #   -> Can use 1 unit from remaining inventory, must produce 2 more

    due_date = np.array([10.0, 15.0, 30.0])
    demand_type = np.array([1, 2, 1])  # Type 1, Type 2, Type 1
    demand_qty = np.array([2, 1, 3])   # 2 units, 1 unit, 3 units

    # Priority weights for production orders
    # Higher priority for earlier orders
    priority = np.array([10, 10, 10, 10])

    # Objective weights
    # Emphasize OTIF (on-time delivery) and WIP minimization
    # Lower workforce variability weight since we have one line
    objective_weights = {
        'alpha': 10.0,  # High OTIF weight (meet deadlines)
        'beta': 2.0,    # WIP weight (minimize inventory holding)
        'gamma': 0.5,   # Workforce variability (less important with 1 line)
        'delta': 0.1    # Utilization penalty (less important)
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


def analyze_inventory_usage(model, data):
    """
    Analyze how initial inventory was used vs. production.

    Args:
        model: Solved PackingScheduleModelProblem3 instance
        data: Problem data dictionary
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("INVENTORY USAGE ANALYSIS")
    print("="*80)

    # Display initial inventory
    print("\n--- INITIAL INVENTORY ---")
    print(f"Type 1: {data['initial_inventory'][0]} units")
    print(f"Type 2: {data['initial_inventory'][1]} units")
    print(f"Total:  {sum(data['initial_inventory'])} units")

    # Display demands
    print("\n--- DEMAND REQUIREMENTS ---")
    total_demand_by_type = {1: 0, 2: 0}

    for d_idx in range(data['n_demands']):
        demand_id = d_idx + 1
        prod_type = data['demand_type'][d_idx]
        qty = data['demand_qty'][d_idx]
        due = data['due_date'][d_idx]
        total_demand_by_type[prod_type] += qty

        print(f"Demand {demand_id}: Type {prod_type}, Qty {qty}, Due {due:.0f}")

    print(f"\nTotal demand by type:")
    print(f"  Type 1: {total_demand_by_type[1]} units")
    print(f"  Type 2: {total_demand_by_type[2]} units")

    # Calculate what needs to be produced
    print("\n--- PRODUCTION REQUIREMENTS ---")
    type1_needed = max(0, total_demand_by_type[1] - data['initial_inventory'][0])
    type2_needed = max(0, total_demand_by_type[2] - data['initial_inventory'][1])

    print(f"Type 1: Need to produce {type1_needed} units")
    print(f"  (Demand: {total_demand_by_type[1]}, Inventory: {data['initial_inventory'][0]})")
    print(f"Type 2: Need to produce {type2_needed} units")
    print(f"  (Demand: {total_demand_by_type[2]}, Inventory: {data['initial_inventory'][1]})")

    # Display production schedule
    print("\n--- ACTUAL PRODUCTION SCHEDULE ---")

    if solution['assignments']:
        print(f"\n{'Order':<8} {'Type':<8} {'Line':<8} {'Start':<10} {'Complete':<12} {'Duration'}")
        print("-" * 70)

        total_produced = {1: 0, 2: 0}
        for assignment in sorted(solution['assignments'], key=lambda x: x['start']):
            order_id = assignment['order']
            order_idx = order_id - 1
            prod_type = data['order_type'][order_idx]
            line = assignment['line']
            start = assignment['start']
            complete = assignment['completion']
            duration = complete - start

            total_produced[prod_type] += 1

            print(f"{order_id:<8} {prod_type:<8} {line:<8} {start:<10.1f} {complete:<12.1f} {duration:.1f}")

        print(f"\nTotal produced:")
        print(f"  Type 1: {total_produced[1]} units (needed {type1_needed})")
        print(f"  Type 2: {total_produced[2]} units (needed {type2_needed})")
    else:
        print("\nNo production scheduled - all demands fulfilled from inventory!")

    # Display shipping schedule
    print("\n--- SHIPPING SCHEDULE ---")
    print(f"\n{'Demand':<10} {'Type':<8} {'Qty':<8} {'Due':<10} {'Ship':<10} {'Status':<12} {'Source'}")
    print("-" * 80)

    inventory_used = {1: 0, 2: 0}
    production_used = {1: 0, 2: 0}

    for d_idx in range(data['n_demands']):
        demand_id = d_idx + 1
        prod_type = data['demand_type'][d_idx]
        qty = data['demand_qty'][d_idx]
        due = data['due_date'][d_idx]

        # Find corresponding demand fulfillment
        demand_info = next((d for d in solution['demands'] if d['demand'] == demand_id), None)

        if demand_info:
            ship_time = demand_info['ship_time']
            status = "On-time" if ship_time <= due else f"Late ({ship_time - due:.1f})"

            # Determine source (heuristic: if shipped before any production completes, it's from inventory)
            earliest_production = float('inf')
            if solution['assignments']:
                for assignment in solution['assignments']:
                    order_idx = assignment['order'] - 1
                    if data['order_type'][order_idx] == prod_type:
                        earliest_production = min(earliest_production, assignment['completion'])

            if ship_time < earliest_production:
                source = "Inventory"
                inventory_used[prod_type] += qty
            else:
                source = "Production"
                production_used[prod_type] += qty

            print(f"{demand_id:<10} {prod_type:<8} {qty:<8} {due:<10.1f} {ship_time:<10.1f} {status:<12} {source}")
        else:
            print(f"{demand_id:<10} {prod_type:<8} {qty:<8} {due:<10.1f} {'--':<10} {'Not shipped':<12} --")

    # Summary
    print("\n--- INVENTORY VS. PRODUCTION SUMMARY ---")
    print(f"\nType 1:")
    print(f"  Initial inventory: {data['initial_inventory'][0]} units")
    print(f"  Used from inventory: {inventory_used[1]} units")
    print(f"  Used from production: {production_used[1]} units")
    print(f"  Remaining inventory: {data['initial_inventory'][0] - inventory_used[1]} units")

    print(f"\nType 2:")
    print(f"  Initial inventory: {data['initial_inventory'][1]} units")
    print(f"  Used from inventory: {inventory_used[2]} units")
    print(f"  Used from production: {production_used[2]} units")
    print(f"  Remaining inventory: {data['initial_inventory'][1] - inventory_used[2]} units")

    # Timeline visualization
    print("\n--- TIMELINE VISUALIZATION ---\n")

    max_time = min(50, int(max([d['ship_time'] for d in solution['demands']] +
                               [a['completion'] for a in solution['assignments']] +
                               [data['due_date'].max()])) + 5)

    print("Time:      ", end="")
    for t in range(0, max_time + 1, 5):
        print(f"{t:>5}", end="")
    print()

    print("           ", end="")
    for t in range(0, max_time + 1, 5):
        print("    |", end="")
    print()

    # Production timeline
    if solution['assignments']:
        print("Production:", end="")
        timeline = [' '] * (max_time + 1)
        for assignment in solution['assignments']:
            order_id = assignment['order']
            order_idx = order_id - 1
            prod_type = data['order_type'][order_idx]
            start = int(assignment['start'])
            complete = int(assignment['completion'])
            for t in range(start, min(complete, max_time + 1)):
                timeline[t] = str(prod_type)

        for i in range(0, max_time + 1):
            if i % 5 == 0:
                print(f"{timeline[i]:>5}", end="")
        print()

    # Shipping timeline
    print("Shipping:  ", end="")
    ship_timeline = [' '] * (max_time + 1)
    for demand_info in solution['demands']:
        demand_id = demand_info['demand']
        demand_idx = demand_id - 1
        prod_type = data['demand_type'][demand_idx]
        ship_time = int(demand_info['ship_time'])
        if ship_time <= max_time:
            ship_timeline[ship_time] = f"D{demand_id}"

    for i in range(0, max_time + 1):
        if i % 5 == 0:
            if ship_timeline[i] != ' ':
                print(f"{ship_timeline[i]:>5}", end="")
            else:
                print(f"{ship_timeline[i]:>5}", end="")
    print()

    # Due dates
    print("Due Dates: ", end="")
    for i in range(0, max_time + 1):
        if i % 5 == 0:
            due_here = [d_idx + 1 for d_idx, due in enumerate(data['due_date']) if abs(due - i) < 0.1]
            if due_here:
                print(f" D{due_here[0]}", end="  ")
            else:
                print("     ", end="")
    print("\n")

    print("="*80)


def main():
    """
    Run the initial inventory usage example.
    """

    print("="*80)
    print("INITIAL INVENTORY USAGE EXAMPLE")
    print("Testing Inventory-First Policy on Single Production Line")
    print("="*80)

    print("\nSCENARIO:")
    print("  - 1 production line (sequential processing)")
    print("  - 2 product types")
    print("  - Initial inventory: 3 units Type 1, 2 units Type 2")
    print("  - 3 demands totaling: 5 units Type 1, 1 unit Type 2")
    print("  - Question: Will inventory be used before production?")

    # Create data
    print("\n[Step 1] Creating inventory test scenario...")
    data = create_inventory_test_data()

    print(f"\nProblem Configuration:")
    print(f"  Product types: {data['n_unique_types']}")
    print(f"  Production orders available: {data['n_orders']}")
    print(f"  Shipping demands: {data['n_demands']}")
    print(f"  Production lines: {data['n_lines']}")
    print(f"  Planning horizon: {data['T_max']}")

    print(f"\nInitial Inventory:")
    print(f"  Type 1: {data['initial_inventory'][0]} units")
    print(f"  Type 2: {data['initial_inventory'][1]} units")

    print(f"\nTotal Demand:")
    type1_demand = sum(qty for qty, typ in zip(data['demand_qty'], data['demand_type']) if typ == 1)
    type2_demand = sum(qty for qty, typ in zip(data['demand_qty'], data['demand_type']) if typ == 2)
    print(f"  Type 1: {type1_demand} units (inventory: {data['initial_inventory'][0]}, need to produce: {max(0, type1_demand - data['initial_inventory'][0])})")
    print(f"  Type 2: {type2_demand} units (inventory: {data['initial_inventory'][1]}, need to produce: {max(0, type2_demand - data['initial_inventory'][1])})")

    # Build model
    print("\n[Step 2] Building optimization model...")
    model = PackingScheduleModelProblem3(data)
    print("  Model built successfully!")

    # Solve
    print("\n[Step 3] Solving optimization problem...")
    print("  Optimizer will decide when to use inventory vs. production...")

    try:
        import pyomo.environ as pyo

        results = model.solve(
            solver_name='appsi_highs',
            tee=False,
            time_limit=300
        )

        print(f"\n  Status: {results['status']}")

        if results['objective_value'] is not None:
            print(f"  Objective value: {results['objective_value']:.2f}")

            # Display solution
            print("\n[Step 4] Solution found!")
            model.print_solution_summary()

            # Detailed inventory analysis
            analyze_inventory_usage(model, data)

            # Key insights
            solution = model.get_solution()

            print("\nKEY INSIGHTS:")
            print(f"  1. Initial inventory allows early demand fulfillment without production")
            print(f"  2. Production is scheduled only when inventory is insufficient")
            print(f"  3. Single line forces sequential processing decisions")
            print(f"  4. Optimizer minimizes WIP by using existing inventory first")

            print(f"\n  This demonstrates:")
            print(f"  - Inventory-first fulfillment strategy")
            print(f"  - Just-in-time production scheduling")
            print(f"  - Trade-offs between inventory holding and production costs")
            print(f"  - Sequential decision-making on a single line")

        else:
            print("\n  No solution found - problem may be infeasible")

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)
    print("\nEXPERIMENT IDEAS:")
    print("  1. Increase initial inventory to eliminate all production")
    print("  2. Set initial inventory to zero to see full production schedule")
    print("  3. Add more product types to test complex inventory management")
    print("  4. Vary due dates to create urgency vs. inventory trade-offs")
    print("  5. Add setup times to see batching with inventory")


if __name__ == "__main__":
    main()
