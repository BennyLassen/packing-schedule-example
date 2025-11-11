"""
Line Selection Optimization Example

This example demonstrates the optimizer's line selection decisions when multiple
production lines are available with different characteristics.

SCENARIO SETUP:
- 2 production lines (both available)
- 1 worker (can work on either line, but not both simultaneously)
- 5 orders to pack
- All orders CAN be completed on Line 1 alone
- Lines have different processing speeds for different orders

This scenario highlights:
1. How the optimizer chooses between available lines
2. Processing time variations across lines (some orders faster on Line 1, others on Line 2)
3. Line utilization vs. minimizing active lines
4. Trade-offs between using one line vs. spreading work across multiple lines

KEY INSIGHTS TO OBSERVE:
- Will the optimizer use both lines or just one?
- How does the objective function weight for line utilization affect this decision?
- Which orders get assigned to which line based on processing time differences?
- How does line selection affect overall completion time and OTIF performance?

EXPECTED BEHAVIOR:
- All 5 orders will be packed successfully
- All orders should be delivered on-time (generous due dates)
- The optimizer may use 1 or 2 lines depending on objective weights
- Line selection will consider processing time differences

This example is useful for:
- Understanding line selection trade-offs
- Comparing single-line vs. multi-line strategies
- Analyzing the impact of processing time variations
- Production planning with multiple resources
"""

import numpy as np
import sys
import os

# Add src directory to path to import packing_model
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from packing_model import PackingScheduleModel


def create_line_selection_data():
    """
    Create a line selection scenario with 2 lines and varying processing times.

    Key Design:
    - All orders CAN complete on Line 1 alone (total time = 16 + 4 setup = 20 units)
    - Line 2 is faster for some orders, slower for others
    - This creates interesting line selection decisions

    Returns:
        dict: Problem data with 2 lines and processing time variations
    """

    # Problem dimensions
    n_orders = 5
    n_lines = 2          # Two lines available
    n_timeslots = 25     # Generous time available
    n_workers = 1        # Only 1 worker (can't use both lines simultaneously)

    # Processing times: p[i, j] - time for order i on line j
    # Line 1: General purpose (moderate speeds)
    # Line 2: Specialized (faster for some orders, slower for others)
    processing_time = np.array([
        [3, 4],    # Order 1: Faster on Line 1 (3 vs 4)
        [4, 3],    # Order 2: Faster on Line 2 (4 vs 3)
        [2, 3],    # Order 3: Faster on Line 1 (2 vs 3)
        [4, 2],    # Order 4: Much faster on Line 2 (4 vs 2)
        [3, 4],    # Order 5: Faster on Line 1 (3 vs 4)
    ])
    # Line 1 total: 3+4+2+4+3 = 16 time units
    # Line 2 total: 4+3+3+2+4 = 16 time units (same total!)
    # But individual orders have preferences

    # Setup times between orders (1 time unit between different orders)
    setup_time = np.ones((n_orders, n_orders, n_lines))
    for j in range(n_lines):
        np.fill_diagonal(setup_time[:, :, j], 0)  # No setup for same order

    # Worker availability - worker available for all time slots
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity (10%)
    reserved_capacity = 0.1

    # Due dates - GENEROUS (all orders should be on-time)
    # Total processing + setup on one line = 16 + 4 = 20 time units
    # Setting due dates beyond this ensures all can be on-time
    due_date = np.array([
        8,   # Order 1: Due at time 8
        12,  # Order 2: Due at time 12
        6,   # Order 3: Due at time 6 (earliest)
        18,  # Order 4: Due at time 18
        15,  # Order 5: Due at time 15
    ])

    # Priority weights - varied to make selection interesting
    priority = np.array([
        80,  # Order 1: High priority
        75,  # Order 2: Medium-high priority
        90,  # Order 3: Highest priority (earliest due date)
        70,  # Order 4: Medium priority
        85,  # Order 5: High priority
    ])

    # Target workforce level
    workforce_target = 1

    # Objective function weights
    # TRY DIFFERENT VALUES OF DELTA to see different line selection behavior:
    # - High delta (e.g., 10.0): Optimizer will prefer using fewer lines
    # - Low delta (e.g., 0.1): Optimizer will freely use multiple lines
    objective_weights = {
        'alpha': 1.0,   # Weight for OTIF
        'beta': 0.3,    # Weight for WIP
        'gamma': 0.2,   # Weight for workforce variability
        'delta': 0.5    # Weight for line utilization (EXPERIMENT WITH THIS!)
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


def analyze_line_selection(model, data):
    """
    Analyze line selection decisions and processing time trade-offs.

    Args:
        model: Solved PackingScheduleModel instance
        data: Problem data dictionary
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("LINE SELECTION ANALYSIS")
    print("="*80)

    # Analyze line usage
    print("\n--- LINE UTILIZATION ---\n")

    line_usage = {1: [], 2: []}
    total_time_by_line = {1: 0, 2: 0}

    for assignment in solution['assignments']:
        order_id = assignment['order']
        line_id = assignment['line']
        start = int(assignment['start'])
        complete = int(assignment['completion'])
        processing = data['processing_time'][order_id-1, line_id-1]

        line_usage[line_id].append(order_id)
        total_time_by_line[line_id] += (complete - start)

    for line_id in [1, 2]:
        if line_usage[line_id]:
            print(f"Line {line_id}:")
            print(f"  Orders assigned: {line_usage[line_id]} ({len(line_usage[line_id])} orders)")
            print(f"  Total time used: {total_time_by_line[line_id]} units")
            print(f"  Status: ACTIVE")
        else:
            print(f"Line {line_id}:")
            print(f"  Orders assigned: None")
            print(f"  Total time used: 0 units")
            print(f"  Status: UNUSED")
        print()

    # Processing time analysis
    print("--- PROCESSING TIME COMPARISON ---\n")
    print("Order | Line 1 | Line 2 | Selected | Time Saved")
    print("------|--------|--------|----------|------------")

    for assignment in solution['assignments']:
        order_id = assignment['order']
        selected_line = assignment['line']

        time_line1 = data['processing_time'][order_id-1, 0]
        time_line2 = data['processing_time'][order_id-1, 1]
        selected_time = data['processing_time'][order_id-1, selected_line-1]

        faster_line = 1 if time_line1 < time_line2 else (2 if time_line2 < time_line1 else 0)
        optimal_choice = "Yes" if selected_line == faster_line or faster_line == 0 else "No"
        time_saved = abs(time_line1 - time_line2) if selected_line == faster_line else -abs(time_line1 - time_line2)

        status = ""
        if faster_line == 0:
            status = " (equal)"
        elif optimal_choice == "Yes":
            status = f" (saved {abs(time_saved)} units)"
        else:
            status = f" (lost {abs(time_saved)} units)"

        print(f"  {order_id}   |   {time_line1}    |   {time_line2}    |  Line {selected_line}  | {status}")

    print()

    # Timeline visualization for both lines
    print("\n--- DUAL-LINE TIMELINE ---\n")

    max_time = min(25, max([int(a['completion']) for a in solution['assignments']]) + 2)

    print("Time: ", end="")
    for t in range(1, max_time + 1):
        print(f"{t:2d} ", end="")
    print()

    # Timeline for Line 1
    timeline_l1 = ['-'] * max_time
    for assignment in solution['assignments']:
        if assignment['line'] == 1:
            order_id = assignment['order']
            start = int(assignment['start'])
            complete = int(assignment['completion'])
            for t in range(start, complete):
                if t <= max_time:
                    timeline_l1[t-1] = str(order_id)

    print("Line 1:", end="")
    for t in timeline_l1:
        print(f" {t} ", end="")
    print()

    # Timeline for Line 2
    timeline_l2 = ['-'] * max_time
    for assignment in solution['assignments']:
        if assignment['line'] == 2:
            order_id = assignment['order']
            start = int(assignment['start'])
            complete = int(assignment['completion'])
            for t in range(start, complete):
                if t <= max_time:
                    timeline_l2[t-1] = str(order_id)

    print("Line 2:", end="")
    for t in timeline_l2:
        print(f" {t} ", end="")
    print()

    # Due date markers
    print("Due:   ", end="")
    for t in range(1, max_time + 1):
        due_here = [i+1 for i, d in enumerate(data['due_date']) if d == t]
        if due_here:
            print(f"D{due_here[0]} ", end="")
        else:
            print(" . ", end="")
    print("\n")

    # Decision analysis
    print("--- DECISION INSIGHTS ---\n")

    lines_used = len([l for l in [1, 2] if line_usage[l]])

    print(f"Number of lines activated: {lines_used}/2")

    if lines_used == 1:
        used_line = 1 if line_usage[1] else 2
        print(f"\nSINGLE-LINE STRATEGY:")
        print(f"  All orders assigned to Line {used_line}")
        print(f"  Benefits: Lower line activation cost, simpler scheduling")
        print(f"  Trade-off: May not use fastest line for each order")
    else:
        print(f"\nMULTI-LINE STRATEGY:")
        print(f"  Work distributed across both lines")
        print(f"  Benefits: Can select optimal line per order, potentially faster completion")
        print(f"  Trade-off: Higher line activation cost")

        # Analyze if multi-line was beneficial
        total_saved = 0
        for assignment in solution['assignments']:
            order_id = assignment['order']
            selected_line = assignment['line']
            time_line1 = data['processing_time'][order_id-1, 0]
            time_line2 = data['processing_time'][order_id-1, 1]
            if selected_line == 1:
                total_saved += (time_line2 - time_line1)
            else:
                total_saved += (time_line1 - time_line2)

        if total_saved > 0:
            print(f"  Total processing time saved: {total_saved} units")
        else:
            print(f"  Total processing time penalty: {abs(total_saved)} units")

    print("\n" + "="*80)


def main():
    """
    Run the line selection example.
    """

    print("="*80)
    print("LINE SELECTION OPTIMIZATION EXAMPLE")
    print("Two Lines, One Worker: Which Line to Choose?")
    print("="*80)

    print("\nSCENARIO:")
    print("  - 2 production lines (different speeds per order)")
    print("  - 1 worker (can only work one line at a time)")
    print("  - 5 orders with varying processing times per line")
    print("  - All orders CAN be completed on Line 1 alone")
    print("  - Line 2 is faster for some orders, slower for others")
    print("\nQUESTION: Will the optimizer use one line or both?")

    # Create data
    print("\n[Step 1] Creating line selection scenario...")
    data = create_line_selection_data()

    print(f"\nProblem Configuration:")
    print(f"  Orders: {data['n_orders']}")
    print(f"  Lines: {data['n_lines']}")
    print(f"  Workers: {data['n_workers']}")
    print(f"  Time slots: {data['n_timeslots']}")

    print(f"\nProcessing Time Matrix:")
    print(f"  Order | Line 1 | Line 2 | Faster Line")
    print(f"  ------|--------|--------|-------------")
    for i in range(data['n_orders']):
        t1 = data['processing_time'][i, 0]
        t2 = data['processing_time'][i, 1]
        faster = "Line 1" if t1 < t2 else ("Line 2" if t2 < t1 else "Equal")
        print(f"    {i+1}   |   {t1}    |   {t2}    | {faster}")

    print(f"\nObjective Weights:")
    print(f"  OTIF (alpha):     {data['objective_weights']['alpha']}")
    print(f"  WIP (beta):       {data['objective_weights']['beta']}")
    print(f"  Workforce (gamma):{data['objective_weights']['gamma']}")
    print(f"  Line Cost (delta):{data['objective_weights']['delta']} <- Controls single vs. multi-line")

    # Build model
    print("\n[Step 2] Building optimization model...")
    model = PackingScheduleModel(data)
    print(f"  Variables: {model.model.nvariables()}")
    print(f"  Constraints: {model.model.nconstraints()}")

    # Solve
    print("\n[Step 3] Solving optimization problem...")
    print("  Optimizer deciding: Use one line or both?")

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
            analyze_line_selection(model, data)

            # Key insights
            solution = model.get_solution()
            lines_used = sum(1 for l in solution['line_usage'] if l['used'])
            on_time_count = sum(1 for order_id, metrics in solution['otif_metrics'].items()
                              if not metrics['late'])

            print("\nKEY INSIGHTS:")
            print(f"  1. Lines activated: {lines_used}/2")
            print(f"  2. On-time delivery: {on_time_count}/5 orders (100% target)")
            print(f"  3. Line selection driven by processing time differences")
            print(f"  4. Line activation cost (delta={data['objective_weights']['delta']}) influenced strategy")

            print(f"\n  This demonstrates:")
            print(f"  - How objective function weights affect resource utilization")
            print(f"  - Trade-offs between minimizing active lines vs. processing time")
            print(f"  - Optimizer's ability to select optimal line per order")

        else:
            print("\n  No solution found - problem may be infeasible")

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)
    print("\nEXPERIMENT IDEAS:")
    print("  1. Change delta weight:")
    print("     - Set delta=10.0 -> Optimizer should prefer single line")
    print("     - Set delta=0.1  -> Optimizer may use both lines freely")
    print("  2. Modify processing times to make one line clearly superior")
    print("  3. Add a second worker to enable parallel line usage")
    print("  4. Make processing time differences larger to amplify line selection")
    print("\nTo modify: Edit 'objective_weights' in create_line_selection_data()")


if __name__ == "__main__":
    main()
