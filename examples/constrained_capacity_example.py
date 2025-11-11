"""
Constrained Capacity Example - Trade-off Analysis

This example demonstrates a realistic scheduling scenario where resource constraints
force the optimizer to make trade-offs between on-time delivery and other objectives.

SCENARIO SETUP:
- 1 production line (limited capacity)
- 1 worker (limited labor)
- 5 orders to pack
- Tight due dates that CANNOT all be met simultaneously

This scenario highlights:
1. The optimizer's ability to prioritize orders based on priority weights
2. How limited capacity forces late deliveries for some orders
3. The trade-off between minimizing lateness vs. flow time vs. workforce stability
4. Realistic production planning under resource constraints

EXPECTED BEHAVIOR:
- All 5 orders will be packed (feasible schedule exists)
- NOT all orders will be delivered on-time (due to capacity constraints)
- Higher priority orders should be scheduled earlier
- The optimizer will minimize total weighted lateness

This example is useful for:
- Understanding optimizer behavior under tight constraints
- Testing priority-based scheduling
- Analyzing trade-offs in multi-objective optimization
- Production planning with limited resources
"""

import numpy as np
import sys
import os

# Add parent directory to path to import packing_model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packing_model import PackingScheduleModel


def create_constrained_capacity_data():
    """
    Create a constrained capacity scenario with impossible-to-meet deadlines.

    Constraints:
    - 1 line only
    - 1 worker only
    - 5 orders with processing times totaling 15 time units
    - Due dates that would require parallel processing (which we can't do)

    Returns:
        dict: Problem data with tight constraints
    """

    # Problem dimensions - HIGHLY CONSTRAINED
    n_orders = 5
    n_lines = 1          # Only 1 line available
    n_timeslots = 20     # 20 time slots available
    n_workers = 1        # Only 1 worker available

    # Processing times for each order on the single line
    # Total processing time: 3 + 4 + 2 + 4 + 3 = 16 time units
    processing_time = np.array([
        [3],    # Order 1: 3 time units
        [4],    # Order 2: 4 time units
        [2],    # Order 3: 2 time units
        [4],    # Order 4: 4 time units
        [3],    # Order 5: 3 time units
    ])

    # Setup times between orders (1 time unit between different orders)
    # This adds 4 more time units (setup between each consecutive order)
    # Total time needed: 16 (processing) + 4 (setup) = 20 time units
    setup_time = np.ones((n_orders, n_orders, n_lines))
    np.fill_diagonal(setup_time[:, :, 0], 0)  # No setup for same order

    # Worker availability - worker available for all time slots
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity (10%)
    reserved_capacity = 0.1

    # Due dates - IMPOSSIBLE TO MEET ALL
    # These due dates assume orders could be processed in parallel (which they can't!)
    # Order 3 has earliest due date, Order 4 has latest
    due_date = np.array([
        6,   # Order 1: Due at time 6 (needs to start by t=3, but setup delays this)
        8,   # Order 2: Due at time 8 (will likely be late)
        5,   # Order 3: Due at time 5 (HIGHEST priority, earliest due date)
        15,  # Order 4: Due at time 15 (lower priority, more slack)
        10,  # Order 5: Due at time 10 (will likely be late)
    ])

    # Priority weights - Order 3 is most critical, Order 4 is least critical
    # Higher priority orders should be scheduled earlier when conflicts arise
    priority = np.array([
        75,  # Order 1: Medium-high priority
        85,  # Order 2: High priority
        95,  # Order 3: HIGHEST priority (earliest due date)
        60,  # Order 4: Lower priority (has slack)
        80,  # Order 5: High priority
    ])

    # Target workforce level (we only have 1 worker, so target is 1)
    workforce_target = 1

    # Objective function weights
    # Emphasize OTIF performance (alpha) to see clear priority-based scheduling
    objective_weights = {
        'alpha': 10.0,  # High weight for OTIF (minimize lateness)
        'beta': 0.5,    # Low weight for WIP
        'gamma': 0.1,   # Low weight for workforce variability
        'delta': 0.2    # Low weight for line utilization
    }

    # Compile all data
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


def analyze_schedule(model, data):
    """
    Analyze and explain the scheduling decisions made by the optimizer.

    Args:
        model: Solved PackingScheduleModel instance
        data: Problem data dictionary
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("DETAILED SCHEDULE ANALYSIS")
    print("="*80)

    # Analyze each order
    print("\n--- ORDER-BY-ORDER ANALYSIS ---\n")

    for order_id, order_data in solution['otif_metrics'].items():
        idx = order_id - 1

        # Get assignment info
        assignment = next(a for a in solution['assignments'] if a['order'] == order_id)

        # Calculate metrics
        start_time = assignment['start']
        completion_time = assignment['completion']
        processing_time = data['processing_time'][idx, 0]
        due_date = data['due_date'][idx]
        priority = data['priority'][idx]

        # Determine status
        if completion_time <= due_date:
            status = "ON-TIME"
            symbol = "OK"
        else:
            status = "LATE"
            symbol = "!!"

        print(f"Order {order_id} [{symbol} {status}]:")
        print(f"  Priority: {priority}/100")
        print(f"  Processing time: {processing_time} units")
        print(f"  Scheduled: Start t={start_time}, Complete t={completion_time}")
        print(f"  Due date: t={due_date}")

        if completion_time > due_date:
            lateness = completion_time - due_date
            print(f"  Lateness: {lateness} time units LATE")
        else:
            earliness = due_date - completion_time
            print(f"  Earliness: {earliness} time units early")

        print()

    # Summary statistics
    print("--- CONSTRAINT ANALYSIS ---\n")

    total_processing = np.sum(data['processing_time'])
    total_setup = (data['n_orders'] - 1) * 1  # Assuming 1 unit setup between orders
    total_time_needed = total_processing + total_setup

    print(f"Total processing time needed: {total_processing} units")
    print(f"Total setup time needed: {total_setup} units")
    print(f"Total time required: {total_time_needed} units")
    print(f"Total time available: {data['n_timeslots']} units")
    print(f"Capacity utilization: {total_time_needed/data['n_timeslots']*100:.1f}%")

    # Timeline visualization
    print("\n--- TIMELINE VISUALIZATION ---\n")
    print("Time: ", end="")
    for t in range(1, 21):
        print(f"{t:2d} ", end="")
    print()
    print("Order:", end="")

    # Create timeline
    timeline = ['-'] * 20
    for assignment in solution['assignments']:
        order_id = assignment['order']
        start = int(assignment['start'])
        complete = int(assignment['completion'])
        for t in range(start, complete):
            if t <= 20:
                timeline[t-1] = str(order_id)

    for t in timeline:
        print(f" {t} ", end="")
    print("\n")

    # Due date markers
    print("Due:  ", end="")
    for t in range(1, 21):
        due_here = [i+1 for i, d in enumerate(data['due_date']) if d == t]
        if due_here:
            print(f"D{due_here[0]} ", end="")
        else:
            print(" . ", end="")
    print()

    print("\n" + "="*80)


def main():
    """
    Run the constrained capacity example.
    """

    print("="*80)
    print("CONSTRAINED CAPACITY EXAMPLE")
    print("Trade-off Analysis: Limited Resources, Impossible Deadlines")
    print("="*80)

    print("\nSCENARIO:")
    print("  - 1 production line (no parallel processing)")
    print("  - 1 worker (no concurrent work)")
    print("  - 5 orders with tight, conflicting due dates")
    print("  - Total work requires ~20 time units")
    print("  - Due dates assume parallel processing (impossible!)")
    print("\nQUESTION: Which orders will be late? How does the optimizer prioritize?")

    # Create data
    print("\n[Step 1] Creating constrained scenario...")
    data = create_constrained_capacity_data()

    print(f"\nProblem Configuration:")
    print(f"  Orders: {data['n_orders']}")
    print(f"  Lines: {data['n_lines']} (CONSTRAINED)")
    print(f"  Workers: {data['n_workers']} (CONSTRAINED)")
    print(f"  Time slots: {data['n_timeslots']}")
    print(f"\nOrder Priorities:")
    for i in range(data['n_orders']):
        print(f"  Order {i+1}: Priority={data['priority'][i]:3d}, "
              f"Due t={data['due_date'][i]:2d}, "
              f"Processing={data['processing_time'][i,0]} units")

    # Build model
    print("\n[Step 2] Building optimization model...")
    model = PackingScheduleModel(data)
    print(f"  Variables: {model.model.nvariables()}")
    print(f"  Constraints: {model.model.nconstraints()}")

    # Solve
    print("\n[Step 3] Solving optimization problem...")
    print("  Optimizer will minimize: weighted lateness + WIP + workforce variability")

    try:
        results = model.solve(
            solver_name='appsi_highs',
            tee=False,
            time_limit=300
        )

        print(f"\n  Status: {results['status']}")
        print(f"  Termination: {results['termination_condition']}")

        if results['objective_value'] is not None:
            print(f"  Objective value: {results['objective_value']:.2f}")

            # Display solution
            print("\n[Step 4] Solution found!")
            model.print_solution_summary()

            # Detailed analysis
            analyze_schedule(model, data)

            # Insights
            solution = model.get_solution()
            on_time_count = sum(1 for order_id, metrics in solution['otif_metrics'].items()
                              if not metrics['late'])
            late_count = data['n_orders'] - on_time_count

            print("\nKEY INSIGHTS:")
            print(f"  1. {on_time_count} orders delivered on-time, {late_count} orders late")
            print(f"  2. Optimizer prioritized high-priority orders (check Order 3)")
            print(f"  3. Limited capacity (1 line, 1 worker) forced sequential processing")
            print(f"  4. Trade-offs were made to minimize total weighted lateness")

            if late_count > 0:
                print(f"\n  This demonstrates realistic production planning where:")
                print(f"  - Not all deadlines can be met due to resource constraints")
                print(f"  - Priority-based scheduling minimizes impact on critical orders")
                print(f"  - The optimizer finds the best feasible compromise")
        else:
            print("\n  No solution found - problem may be infeasible")

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)
    print("\nTRY THIS:")
    print("  - Modify priority weights to see different scheduling decisions")
    print("  - Adjust due dates to make problem more/less constrained")
    print("  - Add a second line to see how it affects on-time performance")
    print("  - Change objective weights (alpha) to emphasize OTIF vs WIP")


if __name__ == "__main__":
    main()
