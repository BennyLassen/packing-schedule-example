"""
Parallel Processing Example - Multi-Line, Multi-Worker Production

This example demonstrates TRUE parallel processing where multiple workers can
operate different production lines simultaneously.

SCENARIO SETUP:
- 2 production lines (both available)
- 2 workers (can work on different lines at the same time)
- 5 orders to pack
- Lines have different processing speeds for different orders
- Enables TRUE parallel execution

This scenario highlights:
1. Parallel processing on multiple lines simultaneously
2. How multiple workers enable concurrent production
3. Dramatic reduction in total completion time through parallelization
4. Load balancing across workers and lines
5. The value of additional labor in production scheduling

KEY DIFFERENCES FROM SINGLE-WORKER EXAMPLE:
- Single worker: Sequential processing, one line at a time
- Two workers: Parallel processing, both lines can run simultaneously
- Result: Potentially 2x faster completion (if work is balanced)

EXPECTED BEHAVIOR:
- All 5 orders will be packed successfully
- All orders should be delivered on-time (100% OTIF)
- Both lines will operate IN PARALLEL (overlapping time periods)
- Completion time ~9 units (vs ~17 sequential) - 1.9x speedup
- Workers 1 and 2 working simultaneously on different lines

IMPORTANT - WHY OBJECTIVE WEIGHTS MATTER:
The optimizer doesn't just maximize resource utilization - it balances trade-offs:
- High WIP penalties discourage parallel work (more orders in-process simultaneously)
- High workforce variability penalties discourage using multiple workers
- Tight due dates + high OTIF weight FORCE parallelization to meet deadlines

This example uses:
- Tight due dates (orders 1&2 both due at t=6) - requires parallel processing
- High OTIF weight (alpha=10.0) - prioritizes meeting deadlines
- Low WIP/workforce weights (beta=0.05, gamma=0.05) - reduces parallel penalty

Try increasing beta/gamma to 0.3/0.2 and loosening due dates to see sequential execution return!

This example is useful for:
- Understanding the value of parallel processing
- Capacity planning with multiple workers
- Comparing sequential vs. parallel execution
- Workforce sizing decisions
- Production line utilization analysis
"""

import numpy as np
import sys
import os

# Add parent directory to path to import packing_model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packing_model import PackingScheduleModel


def create_parallel_processing_data():
    """
    Create a parallel processing scenario with 2 lines and 2 workers.

    Key Design:
    - 2 workers enable simultaneous work on both lines
    - Processing times favor different lines for different orders
    - This enables optimal line selection AND parallel execution

    Returns:
        dict: Problem data with 2 lines and 2 workers
    """

    # Problem dimensions
    n_orders = 5
    n_lines = 2          # Two lines available
    n_timeslots = 25     # Generous time available
    n_workers = 2        # TWO workers (enables parallel processing!)

    # Processing times: p[i, j] - time for order i on line j
    # Same as line selection example, but now we have 2 workers
    processing_time = np.array([
        [3, 4],    # Order 1: Faster on Line 1 (3 vs 4)
        [4, 3],    # Order 2: Faster on Line 2 (4 vs 3)
        [2, 3],    # Order 3: Faster on Line 1 (2 vs 3)
        [4, 2],    # Order 4: Much faster on Line 2 (4 vs 2)
        [3, 4],    # Order 5: Faster on Line 1 (3 vs 4)
    ])

    # Setup times between orders (1 time unit between different orders)
    setup_time = np.ones((n_orders, n_orders, n_lines))
    for j in range(n_lines):
        np.fill_diagonal(setup_time[:, :, j], 0)  # No setup for same order

    # Worker availability - both workers available for all time slots
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity (10%)
    reserved_capacity = 0.1

    # Due dates - TIGHTER to encourage parallelization
    # With sequential processing (one worker), orders would take ~14 time units
    # With parallel processing (two workers), should take ~7-8 time units
    due_date = np.array([
        6,   # Order 1: Due at time 6 (requires early start)
        6,   # Order 2: Due at time 6 (requires parallel with order 1)
        4,   # Order 3: Due at time 4 (earliest - must go first)
        10,  # Order 4: Due at time 10
        10,  # Order 5: Due at time 10
    ])

    # Priority weights
    priority = np.array([
        80,  # Order 1: High priority
        75,  # Order 2: Medium-high priority
        90,  # Order 3: Highest priority (earliest due date)
        70,  # Order 4: Medium priority
        85,  # Order 5: High priority
    ])

    # Target workforce level (2 workers)
    workforce_target = 2

    # Objective function weights
    # NOTE: Lower WIP and workforce weights to encourage parallel processing
    # Higher alpha weight ensures meeting deadlines is the priority
    objective_weights = {
        'alpha': 10.0,  # HIGH weight for OTIF (meeting deadlines is critical!)
        'beta': 0.05,   # LOW weight for WIP (don't penalize parallel work heavily)
        'gamma': 0.05,  # LOW weight for workforce variability (allow multiple workers)
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


def analyze_parallel_execution(model, data):
    """
    Analyze parallel processing and worker utilization.

    Args:
        model: Solved PackingScheduleModel instance
        data: Problem data dictionary
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("PARALLEL PROCESSING ANALYSIS")
    print("="*80)

    # Analyze worker assignments
    print("\n--- WORKER ASSIGNMENTS ---\n")

    worker_assignments = {1: [], 2: []}
    for assignment in solution['assignments']:
        order_id = assignment['order']
        worker_id = assignment['worker']
        line_id = assignment['line']
        start = int(assignment['start'])
        complete = int(assignment['completion'])

        worker_assignments[worker_id].append({
            'order': order_id,
            'line': line_id,
            'start': start,
            'complete': complete
        })

    for worker_id in [1, 2]:
        print(f"Worker {worker_id}:")
        if worker_assignments[worker_id]:
            for task in sorted(worker_assignments[worker_id], key=lambda x: x['start']):
                print(f"  Order {task['order']} on Line {task['line']}: "
                      f"t={task['start']}-{task['complete']} "
                      f"({task['complete']-task['start']} units)")
            total_time = sum(t['complete'] - t['start'] for t in worker_assignments[worker_id])
            print(f"  Total working time: {total_time} units")
        else:
            print(f"  No assignments")
        print()

    # Analyze line usage
    print("--- LINE UTILIZATION ---\n")

    line_usage = {1: [], 2: []}
    for assignment in solution['assignments']:
        order_id = assignment['order']
        line_id = assignment['line']
        worker_id = assignment['worker']
        start = int(assignment['start'])
        complete = int(assignment['completion'])

        line_usage[line_id].append({
            'order': order_id,
            'worker': worker_id,
            'start': start,
            'complete': complete
        })

    for line_id in [1, 2]:
        if line_usage[line_id]:
            print(f"Line {line_id}:")
            for task in sorted(line_usage[line_id], key=lambda x: x['start']):
                print(f"  Order {task['order']} (Worker {task['worker']}): "
                      f"t={task['start']}-{task['complete']}")
            print(f"  Status: ACTIVE")
        else:
            print(f"Line {line_id}:")
            print(f"  Status: UNUSED")
        print()

    # Detect parallel execution
    print("--- PARALLEL EXECUTION DETECTION ---\n")

    max_time = max([int(a['completion']) for a in solution['assignments']])
    parallel_periods = []

    for t in range(1, max_time + 1):
        active_lines = set()
        active_workers = set()

        for assignment in solution['assignments']:
            start = int(assignment['start'])
            complete = int(assignment['completion'])
            if start <= t < complete:
                active_lines.add(assignment['line'])
                active_workers.add(assignment['worker'])

        if len(active_lines) > 1:
            parallel_periods.append(t)

    if parallel_periods:
        print(f"Parallel execution detected at {len(parallel_periods)} time slots!")
        print(f"Time slots with parallel work: {parallel_periods[:10]}{'...' if len(parallel_periods) > 10 else ''}")
        print(f"\nBoth lines were working simultaneously for {len(parallel_periods)} time units")
    else:
        print("No parallel execution detected.")
        print("Lines operated sequentially (one at a time).")

    # Timeline visualization
    print("\n--- PARALLEL TIMELINE VISUALIZATION ---\n")

    max_display_time = min(20, max_time + 2)

    print("Time:    ", end="")
    for t in range(1, max_display_time + 1):
        print(f"{t:2d} ", end="")
    print()

    # Timeline for Line 1
    timeline_l1 = ['-'] * max_display_time
    worker_l1 = [' '] * max_display_time
    for assignment in solution['assignments']:
        if assignment['line'] == 1:
            order_id = assignment['order']
            worker_id = assignment['worker']
            start = int(assignment['start'])
            complete = int(assignment['completion'])
            for t in range(start, complete):
                if t <= max_display_time:
                    timeline_l1[t-1] = str(order_id)
                    worker_l1[t-1] = str(worker_id)

    print("Line 1:  ", end="")
    for t in timeline_l1:
        print(f" {t} ", end="")
    print()
    print("Worker:  ", end="")
    for w in worker_l1:
        print(f" {w} ", end="")
    print()

    # Timeline for Line 2
    timeline_l2 = ['-'] * max_display_time
    worker_l2 = [' '] * max_display_time
    for assignment in solution['assignments']:
        if assignment['line'] == 2:
            order_id = assignment['order']
            worker_id = assignment['worker']
            start = int(assignment['start'])
            complete = int(assignment['completion'])
            for t in range(start, complete):
                if t <= max_display_time:
                    timeline_l2[t-1] = str(order_id)
                    worker_l2[t-1] = str(worker_id)

    print("Line 2:  ", end="")
    for t in timeline_l2:
        print(f" {t} ", end="")
    print()
    print("Worker:  ", end="")
    for w in worker_l2:
        print(f" {w} ", end="")
    print()

    # Highlight parallel periods
    print("Parallel:", end="")
    for t in range(1, max_display_time + 1):
        if t in parallel_periods:
            print(" * ", end="")
        else:
            print(" . ", end="")
    print("\n")

    # Completion time comparison
    print("--- PERFORMANCE METRICS ---\n")

    actual_completion = max([int(a['completion']) for a in solution['assignments']])
    print(f"Total completion time: {actual_completion} time units")

    # Calculate sequential time (if only 1 worker)
    total_processing = sum(min(data['processing_time'][i-1, :])
                          for i in range(1, data['n_orders'] + 1))
    estimated_sequential = total_processing + (data['n_orders'] - 1)  # Add setup times

    print(f"Estimated sequential time (1 worker): ~{estimated_sequential} time units")

    if actual_completion < estimated_sequential:
        speedup = estimated_sequential / actual_completion
        time_saved = estimated_sequential - actual_completion
        print(f"\nSpeedup from parallelization: {speedup:.2f}x")
        print(f"Time saved: {time_saved} time units ({time_saved/estimated_sequential*100:.1f}%)")
    else:
        print(f"\nNo speedup achieved (may indicate sequential execution)")

    print("\n" + "="*80)


def main():
    """
    Run the parallel processing example.
    """

    print("="*80)
    print("PARALLEL PROCESSING EXAMPLE")
    print("Two Lines, Two Workers: True Parallel Execution")
    print("="*80)

    print("\nSCENARIO:")
    print("  - 2 production lines (different speeds per order)")
    print("  - 2 workers (can work simultaneously on different lines)")
    print("  - 5 orders with varying processing times per line")
    print("  - Workers can operate in PARALLEL")
    print("\nQUESTION: How much faster is parallel processing?")

    # Create data
    print("\n[Step 1] Creating parallel processing scenario...")
    data = create_parallel_processing_data()

    print(f"\nProblem Configuration:")
    print(f"  Orders: {data['n_orders']}")
    print(f"  Lines: {data['n_lines']}")
    print(f"  Workers: {data['n_workers']} <- ENABLES PARALLEL PROCESSING!")
    print(f"  Time slots: {data['n_timeslots']}")

    # Build model
    print("\n[Step 2] Building optimization model...")
    model = PackingScheduleModel(data)
    print(f"  Variables: {model.model.nvariables()}")
    print(f"  Constraints: {model.model.nconstraints()}")

    # Solve
    print("\n[Step 3] Solving optimization problem...")
    print("  Optimizer will utilize parallel processing capabilities...")

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
            analyze_parallel_execution(model, data)

            # Key insights
            solution = model.get_solution()
            on_time_count = sum(1 for order_id, metrics in solution['otif_metrics'].items()
                              if not metrics['late'])

            print("\nKEY INSIGHTS:")
            print(f"  1. On-time delivery: {on_time_count}/5 orders")
            print(f"  2. Multiple workers enable simultaneous line operation")
            print(f"  3. Parallel processing reduces total completion time")
            print(f"  4. Work distribution optimizes for line speed AND parallelization")

            print(f"\n  This demonstrates:")
            print(f"  - The power of parallel processing in production")
            print(f"  - How multiple workers dramatically improve throughput")
            print(f"  - Load balancing across workers and lines")
            print(f"  - The value of workforce capacity in meeting deadlines")

        else:
            print("\n  No solution found - problem may be infeasible")

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)
    print("\nCOMPARE WITH:")
    print("  Run examples/line_selection_example.py to see single-worker behavior")
    print("  Notice how parallel processing significantly reduces completion time!")
    print("\nEXPERIMENT IDEAS:")
    print("  1. Add a third worker to see if it improves performance further")
    print("  2. Reduce to 1 worker to see sequential execution")
    print("  3. Add more orders to see scalability of parallel processing")
    print("  4. Make workers unavailable at certain times to force sequential work")


if __name__ == "__main__":
    main()
