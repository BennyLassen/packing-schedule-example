"""
Setup Time and Batching Example - Order Sequencing Optimization

This example demonstrates how setup times and batching affect production scheduling.
Setup times represent changeover costs between different product types, and the optimizer
can batch similar orders together to minimize these transitions.

SCENARIO SETUP:
- 1 production line (sequential processing only)
- 1 worker (limited labor)
- 10 orders to pack (mix of 3 product families)
- Significant setup times between different product types
- Low/zero setup times within same product family (batching benefit)

This scenario highlights:
1. How setup times affect scheduling decisions
2. The value of batching similar orders together
3. Trade-offs between batching efficiency and due date pressure
4. Sequence-dependent setup time optimization
5. Product family grouping strategies

PRODUCT FAMILIES:
- Family A: Orders 1, 2, 3 (e.g., small boxes)
- Family B: Orders 4, 5, 6, 7 (e.g., medium boxes)
- Family C: Orders 8, 9, 10 (e.g., large boxes)

SETUP TIME STRUCTURE:
- Within family: 0 time units (no changeover needed)
- Between families: 2 time units (significant changeover cost)

KEY INSIGHTS TO OBSERVE:
- Will the optimizer batch orders by product family?
- How does due date urgency affect batching decisions?
- What's the trade-off between setup minimization and on-time delivery?

EXPECTED BEHAVIOR:
- Orders should be grouped by product family where possible
- Some batching may be broken to meet tight due dates
- Total setup time significantly reduced through batching
- Visual comparison of batched vs. non-batched schedules

This example is useful for:
- Understanding sequence-dependent setup times
- Optimizing production sequences for efficiency
- Product family scheduling strategies
- Balancing setup reduction with delivery requirements
- Analyzing the cost of poor sequencing
"""

import numpy as np
import sys
import os

# Add src directory to path to import packing_model
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from packing_model import PackingScheduleModel


def create_setup_batching_data():
    """
    Create a setup time and batching scenario.

    Key Design:
    - 10 orders in 3 product families (A, B, C)
    - High setup times between families (2 units)
    - Zero setup times within families (batching benefit)
    - Due dates create tension between batching and urgency

    Returns:
        dict: Problem data with setup time focus
    """

    # Problem dimensions
    n_orders = 10
    n_lines = 1           # Single line (forces sequencing decisions)
    n_timeslots = 40      # Ample time available
    n_workers = 1         # Single worker

    # Processing times for each order (similar within families)
    # Family A (orders 1-3): 3 units each
    # Family B (orders 4-7): 2 units each
    # Family C (orders 8-10): 4 units each
    processing_time = np.array([
        [3],    # Order 1: Family A
        [3],    # Order 2: Family A
        [3],    # Order 3: Family A
        [2],    # Order 4: Family B
        [2],    # Order 5: Family B
        [2],    # Order 6: Family B
        [2],    # Order 7: Family B
        [4],    # Order 8: Family C
        [4],    # Order 9: Family C
        [4],    # Order 10: Family C
    ])

    # Setup times: SEQUENCE-DEPENDENT based on product families
    # Define product families (0-indexed)
    # Family A: orders 0, 1, 2 (orders 1, 2, 3)
    # Family B: orders 3, 4, 5, 6 (orders 4, 5, 6, 7)
    # Family C: orders 7, 8, 9 (orders 8, 9, 10)

    def get_family(order_idx):
        """Get product family for order (0-indexed)."""
        if order_idx <= 2:
            return 'A'
        elif order_idx <= 6:
            return 'B'
        else:
            return 'C'

    # Setup time matrix: s[i, k, j] - setup from order i to order k on line j
    setup_time = np.zeros((n_orders, n_orders, n_lines))

    for i in range(n_orders):
        for k in range(n_orders):
            if i == k:
                setup_time[i, k, 0] = 0  # No setup for same order
            else:
                family_i = get_family(i)
                family_k = get_family(k)

                if family_i == family_k:
                    # Within same family: minimal setup (0 time units)
                    setup_time[i, k, 0] = 0
                else:
                    # Between different families: significant setup (2 time units)
                    setup_time[i, k, 0] = 2

    # Worker availability - always available
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity (5%)
    reserved_capacity = 0.05

    # Due dates - create tension between batching and urgency
    # Some orders have tight deadlines that may break optimal batching
    due_date = np.array([
        15,  # Order 1 (Family A): Medium urgency
        18,  # Order 2 (Family A): Less urgent
        12,  # Order 3 (Family A): More urgent (may force early scheduling)
        22,  # Order 4 (Family B): Relaxed
        25,  # Order 5 (Family B): Relaxed
        20,  # Order 6 (Family B): Medium urgency
        10,  # Order 7 (Family B): URGENT! (may break batching)
        30,  # Order 8 (Family C): Very relaxed
        28,  # Order 9 (Family C): Relaxed
        32,  # Order 10 (Family C): Very relaxed
    ])

    # Priority weights - higher for urgent orders
    priority = np.array([
        75,  # Order 1
        70,  # Order 2
        80,  # Order 3 (earlier due date)
        65,  # Order 4
        60,  # Order 5
        70,  # Order 6
        95,  # Order 7 (HIGHEST - very urgent!)
        60,  # Order 8
        65,  # Order 9
        60,  # Order 10
    ])

    # Target workforce level
    workforce_target = 1

    # Objective function weights
    # NOTE: These weights balance OTIF with other objectives
    # The optimizer will try to batch, but not at the expense of late deliveries
    objective_weights = {
        'alpha': 5.0,   # High weight for OTIF (meeting deadlines important)
        'beta': 0.2,    # Low weight for WIP
        'gamma': 0.1,   # Low weight for workforce variability
        'delta': 0.1    # Low weight for line utilization
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


def analyze_setup_and_batching(model, data):
    """
    Analyze setup times, batching behavior, and sequencing decisions.

    Args:
        model: Solved PackingScheduleModel instance
        data: Problem data dictionary
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("SETUP TIME AND BATCHING ANALYSIS")
    print("="*80)

    # Product family definitions
    def get_family(order_id):
        """Get product family for order (1-indexed)."""
        if order_id <= 3:
            return 'A'
        elif order_id <= 7:
            return 'B'
        else:
            return 'C'

    # Analyze order sequence
    print("\n--- PRODUCTION SEQUENCE ---\n")

    # Sort assignments by start time
    sequence = sorted(solution['assignments'], key=lambda x: x['start'])

    total_setup_time = 0
    family_transitions = 0
    batches = []
    current_batch = []

    print("Order Sequence (by start time):")
    print(f"{'Order':<8} {'Family':<10} {'Start':<8} {'Complete':<10} {'Setup':<10} {'Status'}")
    print("-" * 70)

    prev_order = None
    prev_family = None

    for i, assignment in enumerate(sequence):
        order_id = assignment['order']
        start = int(assignment['start'])
        complete = int(assignment['completion'])
        family = get_family(order_id)

        # Calculate setup time from previous order
        if prev_order is not None:
            setup = data['setup_time'][prev_order-1, order_id-1, 0]
            total_setup_time += setup

            if prev_family != family:
                family_transitions += 1
                status = f"<- CHANGEOVER from {prev_family}"
                # Start new batch
                if current_batch:
                    batches.append(current_batch)
                current_batch = [order_id]
            else:
                setup = 0  # Within family
                status = f"<- Batched with {prev_family}"
                current_batch.append(order_id)
        else:
            setup = 0
            status = "(First order)"
            current_batch = [order_id]

        print(f"{order_id:<8} {family:<10} {start:<8} {complete:<10} {setup:<10.0f} {status}")

        prev_order = order_id
        prev_family = family

    # Add last batch
    if current_batch:
        batches.append(current_batch)

    print(f"\nTotal Setup Time: {total_setup_time} time units")
    print(f"Family Transitions: {family_transitions}")
    print(f"Number of Batches: {len(batches)}")

    # Analyze batches
    print("\n--- BATCH ANALYSIS ---\n")

    for i, batch in enumerate(batches, 1):
        family = get_family(batch[0])
        print(f"Batch {i} (Family {family}): Orders {batch} ({len(batch)} orders)")

    # Calculate theoretical minimum setup time (perfect batching)
    print("\n--- SETUP TIME COMPARISON ---\n")

    # Perfect batching: A -> B -> C (2 transitions)
    min_setup = 2 * 2  # 2 transitions * 2 time units

    # Worst case: alternating families (9 transitions)
    max_setup = 9 * 2  # 9 transitions * 2 time units

    print(f"Theoretical minimum setup (perfect batching): {min_setup} time units")
    print(f"Actual setup time: {total_setup_time} time units")
    print(f"Theoretical maximum setup (worst sequence): {max_setup} time units")

    efficiency = 100 * (1 - (total_setup_time - min_setup) / (max_setup - min_setup))
    print(f"\nBatching efficiency: {efficiency:.1f}%")
    print(f"Time saved vs. worst case: {max_setup - total_setup_time} time units")

    # Timeline visualization
    print("\n--- PRODUCTION TIMELINE ---\n")

    max_time = min(40, max([int(a['completion']) for a in solution['assignments']]) + 2)

    print("Time:  ", end="")
    for t in range(1, max_time + 1):
        print(f"{t:2d} ", end="")
    print()

    # Order timeline
    timeline = ['-'] * max_time
    for assignment in solution['assignments']:
        order_id = assignment['order']
        start = int(assignment['start'])
        complete = int(assignment['completion'])
        for t in range(start, complete):
            if t <= max_time:
                timeline[t-1] = str(order_id % 10)  # Use last digit for orders > 9

    print("Order: ", end="")
    for t in timeline:
        print(f" {t} ", end="")
    print()

    # Family timeline
    family_timeline = ['-'] * max_time
    for assignment in solution['assignments']:
        order_id = assignment['order']
        family = get_family(order_id)
        start = int(assignment['start'])
        complete = int(assignment['completion'])
        for t in range(start, complete):
            if t <= max_time:
                family_timeline[t-1] = family

    print("Family:", end="")
    for f in family_timeline:
        print(f" {f} ", end="")
    print()

    # Due date markers
    print("Due:   ", end="")
    for t in range(1, max_time + 1):
        due_here = [i+1 for i, d in enumerate(data['due_date']) if d == t]
        if due_here:
            print(f"D{due_here[0]:<1}", end="")
        else:
            print(" . ", end="")
    print()

    # Mark setup periods
    print("Setup: ", end="")
    setup_timeline = [' '] * max_time
    for i in range(1, len(sequence)):
        prev_order = sequence[i-1]['order']
        curr_order = sequence[i]['order']
        prev_complete = int(sequence[i-1]['completion'])
        curr_start = int(sequence[i]['start'])

        setup = data['setup_time'][prev_order-1, curr_order-1, 0]
        if setup > 0:
            for t in range(prev_complete, curr_start):
                if t < max_time:
                    setup_timeline[t] = 'S'

    for s in setup_timeline:
        print(f" {s} ", end="")
    print("\n")

    print("="*80)


def main():
    """
    Run the setup time and batching example.
    """

    print("="*80)
    print("SETUP TIME AND BATCHING EXAMPLE")
    print("Sequence Optimization with Product Families")
    print("="*80)

    print("\nSCENARIO:")
    print("  - 1 production line (sequential processing)")
    print("  - 10 orders in 3 product families:")
    print("    * Family A: Orders 1, 2, 3 (small boxes)")
    print("    * Family B: Orders 4, 5, 6, 7 (medium boxes)")
    print("    * Family C: Orders 8, 9, 10 (large boxes)")
    print("  - Setup times:")
    print("    * Within family: 0 time units (batching benefit)")
    print("    * Between families: 2 time units (changeover cost)")
    print("\nQUESTION: Will the optimizer batch orders by family to minimize setup?")

    # Create data
    print("\n[Step 1] Creating setup and batching scenario...")
    data = create_setup_batching_data()

    print(f"\nProblem Configuration:")
    print(f"  Orders: {data['n_orders']}")
    print(f"  Product families: 3 (A, B, C)")
    print(f"  Lines: {data['n_lines']}")
    print(f"  Workers: {data['n_workers']}")
    print(f"  Time slots: {data['n_timeslots']}")

    print(f"\nSetup Time Structure:")
    print(f"  Within family: 0 time units")
    print(f"  Between families: 2 time units")
    print(f"  Perfect batching setup: 4 time units (2 transitions)")
    print(f"  Worst case setup: 18 time units (9 transitions)")

    # Build model
    print("\n[Step 2] Building optimization model...")
    model = PackingScheduleModel(data)
    print(f"  Variables: {model.model.nvariables()}")
    print(f"  Constraints: {model.model.nconstraints()}")

    # Solve
    print("\n[Step 3] Solving optimization problem...")
    print("  Optimizer will balance batching efficiency with due date constraints...")

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
            analyze_setup_and_batching(model, data)

            # Key insights
            solution = model.get_solution()
            on_time_count = sum(1 for order_id, metrics in solution['otif_metrics'].items()
                              if not metrics['late'])

            print("\nKEY INSIGHTS:")
            print(f"  1. On-time delivery: {on_time_count}/10 orders")
            print(f"  2. Batching strategy optimizes setup time reduction")
            print(f"  3. Urgent orders may break batches to meet deadlines")
            print(f"  4. Significant time savings through intelligent sequencing")

            print(f"\n  This demonstrates:")
            print(f"  - The impact of sequence-dependent setup times")
            print(f"  - Value of batching similar orders together")
            print(f"  - Trade-offs between batching efficiency and urgency")
            print(f"  - Product family scheduling strategies")

        else:
            print("\n  No solution found - problem may be infeasible")

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)
    print("\nEXPERIMENT IDEAS:")
    print("  1. Increase setup times (4 units) to see stronger batching")
    print("  2. Make all due dates tight to see batching break down")
    print("  3. Add more product families for complex sequencing")
    print("  4. Reduce OTIF weight to favor batching over deadlines")
    print("  5. Add a second line to enable parallel family processing")


if __name__ == "__main__":
    main()
