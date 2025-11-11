"""
Large-Scale Weekly Production Example - Industrial-Scale Scheduling

This example demonstrates the scalability of the packing schedule optimization model
for realistic industrial production scenarios.

SCENARIO SETUP:
- 48 production lines (large manufacturing facility)
- 48 workers (one worker per line capacity, can work on any line)
- 1700 orders to pack (realistic weekly volume for large operation)
- 7-day planning horizon (168 hours = 1 week)
- Time slots: 15-minute intervals (672 time slots per week)

This scenario represents:
- A large distribution center or manufacturing facility
- High-volume order fulfillment operations
- Multi-shift operations across a full week
- Realistic capacity constraints and resource allocation

SCALE CHARACTERISTICS:
- Orders per day: ~243 orders
- Orders per hour: ~10 orders
- Average ~35 orders per line per week
- Worker utilization: Flexible assignment across lines

KEY INSIGHTS TO OBSERVE:
1. How the optimizer distributes work across 48 lines
2. Line utilization patterns over the week
3. Worker assignment strategies
4. OTIF performance with high order volumes
5. Computational performance at scale

EXPECTED BEHAVIOR:
- The model will find a feasible schedule if capacity is sufficient
- Some lines may be used more heavily than others
- Worker assignments will balance workload
- Processing times and due dates will drive prioritization
- The solver may take longer due to problem size

COMPUTATIONAL CONSIDERATIONS:
- Variables: ~55 million (1700 orders × 48 lines × 672 time slots × 48 workers)
- This is a large-scale MILP problem
- Solving may take several minutes to hours depending on hardware
- Consider using time limits and gap tolerances for faster solutions

This example is useful for:
- Testing scalability of the optimization model
- Understanding industrial-scale scheduling
- Capacity planning for large facilities
- Benchmarking solver performance
- Validating model behavior at scale

RUNNING TIPS:
- Use a powerful machine with adequate RAM (16GB+ recommended)
- Set reasonable time limits (e.g., 600-1800 seconds)
- Accept MIP gaps (e.g., 1-5%) for faster solutions
- Consider reducing problem size for initial testing
- Monitor memory usage during solving
"""

import numpy as np
import sys
import os
import time

# Add parent directory to path to import packing_model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packing_model import PackingScheduleModel


def create_large_scale_weekly_data():
    """
    Create a large-scale weekly production scenario.

    Design Decisions:
    - 48 lines: Represents a large facility with multiple production areas
    - 48 workers: Provides flexible assignment (workers can move between lines)
    - 1700 orders: Realistic weekly volume for high-throughput operation
    - 15-minute time slots: Balances granularity with model size
    - 7 days (672 slots): Full week planning horizon

    Order Distribution:
    - Processing times: 15-120 minutes (1-8 time slots)
    - Due dates: Distributed across the week
    - Priorities: Mix of standard and high-priority orders
    - Product families: 10 families for batching opportunities

    Returns:
        dict: Large-scale problem data
    """

    print("\n[Data Generation] Creating large-scale problem data...")
    start_time = time.time()

    # Problem dimensions
    n_orders = 1700          # Weekly order volume
    n_lines = 48             # Large facility capacity
    n_timeslots = 672        # 7 days × 24 hours × 4 (15-min slots)
    n_workers = 48           # Flexible workforce

    print(f"  Orders: {n_orders}")
    print(f"  Lines: {n_lines}")
    print(f"  Workers: {n_workers}")
    print(f"  Time slots: {n_timeslots} (7 days, 15-min intervals)")
    print(f"  Planning horizon: 168 hours (1 week)")

    # Processing times: 15-120 minutes (1-8 slots) per order
    # Most orders are 30-60 minutes (2-4 slots)
    print("\n  Generating processing times...")
    np.random.seed(42)  # For reproducibility

    # Create realistic processing time distribution
    # 60% fast (1-3 slots), 30% medium (4-6 slots), 10% slow (7-8 slots)
    fast_orders = int(n_orders * 0.6)
    medium_orders = int(n_orders * 0.3)
    slow_orders = n_orders - fast_orders - medium_orders

    processing_times_list = []

    # Fast orders: 15-45 minutes (1-3 slots)
    processing_times_list.extend(np.random.randint(1, 4, size=fast_orders))

    # Medium orders: 60-90 minutes (4-6 slots)
    processing_times_list.extend(np.random.randint(4, 7, size=medium_orders))

    # Slow orders: 105-120 minutes (7-8 slots)
    processing_times_list.extend(np.random.randint(7, 9, size=slow_orders))

    # Shuffle to randomize order sequence
    np.random.shuffle(processing_times_list)

    # Create processing time matrix [orders x lines]
    # Lines have slight variations in speed (±20%)
    processing_time = np.zeros((n_orders, n_lines), dtype=int)
    for i in range(n_orders):
        base_time = processing_times_list[i]
        for j in range(n_lines):
            # Add variation: some lines faster/slower for different orders
            variation = np.random.uniform(0.8, 1.2)
            processing_time[i, j] = max(1, int(base_time * variation))

    print(f"    Processing time range: {processing_time.min()}-{processing_time.max()} slots")
    print(f"    Average processing time: {processing_time.mean():.1f} slots ({processing_time.mean()*15:.0f} minutes)")

    # Setup times: Product family-based (10 families)
    print("\n  Generating setup times (10 product families)...")
    n_families = 10
    order_families = np.random.randint(0, n_families, size=n_orders)

    setup_time = np.zeros((n_orders, n_orders, n_lines))
    for i in range(n_orders):
        for k in range(n_orders):
            if i == k:
                setup_time[i, k, :] = 0
            elif order_families[i] == order_families[k]:
                # Same family: minimal setup (0-1 slots)
                setup_time[i, k, :] = np.random.randint(0, 2)
            else:
                # Different family: moderate setup (1-2 slots)
                setup_time[i, k, :] = np.random.randint(1, 3)

    print(f"    Setup time range: {setup_time.min():.0f}-{setup_time.max():.0f} slots")

    # Worker availability: 24/7 operation (all workers always available)
    # In a real scenario, this would model shifts and breaks
    print("\n  Setting worker availability (24/7 operation)...")
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

    # Reserved capacity: 15% (buffer for variability)
    reserved_capacity = 0.15

    # Due dates: Distributed across the week
    # 20% urgent (1-2 days), 50% standard (3-5 days), 30% flexible (6-7 days)
    print("\n  Generating due dates...")
    urgent_orders = int(n_orders * 0.2)
    standard_orders = int(n_orders * 0.5)
    flexible_orders = n_orders - urgent_orders - standard_orders

    due_dates_list = []

    # Urgent: days 1-2 (slots 1-192)
    due_dates_list.extend(np.random.randint(1, 193, size=urgent_orders))

    # Standard: days 3-5 (slots 193-480)
    due_dates_list.extend(np.random.randint(193, 481, size=standard_orders))

    # Flexible: days 6-7 (slots 481-672)
    due_dates_list.extend(np.random.randint(481, 673, size=flexible_orders))

    np.random.shuffle(due_dates_list)
    due_date = np.array(due_dates_list)

    print(f"    Due date range: slot {due_date.min()} to {due_date.max()}")
    print(f"    Urgent orders (days 1-2): {urgent_orders}")
    print(f"    Standard orders (days 3-5): {standard_orders}")
    print(f"    Flexible orders (days 6-7): {flexible_orders}")

    # Priority weights: Higher for urgent orders
    print("\n  Generating priority weights...")
    priority = np.zeros(n_orders, dtype=int)
    for i in range(n_orders):
        if due_date[i] <= 192:  # Days 1-2
            priority[i] = np.random.randint(85, 101)  # High priority
        elif due_date[i] <= 480:  # Days 3-5
            priority[i] = np.random.randint(65, 86)   # Medium priority
        else:  # Days 6-7
            priority[i] = np.random.randint(50, 71)   # Standard priority

    print(f"    Priority range: {priority.min()}-{priority.max()}")

    # Target workforce: Use about 60% of workers on average (29 workers)
    workforce_target = int(n_workers * 0.6)
    print(f"\n  Target workforce: {workforce_target} workers (60% utilization)")

    # Objective function weights
    # For large-scale problems, emphasize OTIF and reduce complexity penalties
    objective_weights = {
        'alpha': 10.0,   # High weight for OTIF (critical for customer satisfaction)
        'beta': 0.1,     # Low WIP penalty (high volume makes this less critical)
        'gamma': 0.05,   # Low workforce variability (flexibility is key at scale)
        'delta': 0.01,   # Very low line utilization cost (use all lines as needed)
        'omega': 0.5     # Moderate worker movement penalty (some stability desired)
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

    elapsed = time.time() - start_time
    print(f"\n[Data Generation] Complete in {elapsed:.2f} seconds")

    return data


def analyze_large_scale_solution(model, data):
    """
    Analyze the large-scale solution with summary statistics.

    Args:
        model: Solved PackingScheduleModel instance
        data: Problem data dictionary
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("LARGE-SCALE SOLUTION ANALYSIS")
    print("="*80)

    # OTIF Performance
    print("\n--- OTIF PERFORMANCE ---")
    on_time_count = sum(1 for order_id, metrics in solution['otif_metrics'].items()
                       if not metrics['late'])
    late_count = data['n_orders'] - on_time_count

    print(f"\nTotal orders: {data['n_orders']}")
    print(f"On-time orders: {on_time_count} ({on_time_count/data['n_orders']*100:.1f}%)")
    print(f"Late orders: {late_count} ({late_count/data['n_orders']*100:.1f}%)")

    if late_count > 0:
        late_orders = [order_id for order_id, metrics in solution['otif_metrics'].items()
                      if metrics['late']]
        total_lateness = sum(solution['otif_metrics'][order_id]['lateness']
                           for order_id in late_orders)
        avg_lateness = total_lateness / late_count
        print(f"\nTotal lateness: {total_lateness} time slots ({total_lateness*15:.0f} minutes)")
        print(f"Average lateness: {avg_lateness:.1f} slots ({avg_lateness*15:.0f} minutes)")

    # Line Utilization
    print("\n--- LINE UTILIZATION ---")

    line_usage = {}
    for assignment in solution['assignments']:
        line_id = assignment['line']
        if line_id not in line_usage:
            line_usage[line_id] = {
                'orders': 0,
                'time_used': 0
            }
        line_usage[line_id]['orders'] += 1
        line_usage[line_id]['time_used'] += (assignment['completion'] - assignment['start'])

    lines_used = len(line_usage)
    total_line_time = sum(usage['time_used'] for usage in line_usage.values())
    avg_line_time = total_line_time / lines_used if lines_used > 0 else 0

    print(f"\nLines activated: {lines_used}/{data['n_lines']} ({lines_used/data['n_lines']*100:.1f}%)")
    print(f"Average orders per active line: {data['n_orders']/lines_used:.1f}")
    print(f"Average time per active line: {avg_line_time:.1f} slots ({avg_line_time*15:.0f} minutes)")

    # Show top 10 most utilized lines
    sorted_lines = sorted(line_usage.items(), key=lambda x: x[1]['time_used'], reverse=True)
    print(f"\nTop 10 most utilized lines:")
    print(f"{'Line':<8} {'Orders':<10} {'Time Used (slots)':<20} {'Time (hours)'}")
    print("-" * 70)
    for line_id, usage in sorted_lines[:10]:
        hours = usage['time_used'] * 15 / 60
        print(f"{line_id:<8} {usage['orders']:<10} {usage['time_used']:<20} {hours:.1f}")

    # Worker Utilization
    print("\n--- WORKER UTILIZATION ---")

    worker_usage = {}
    for assignment in solution['assignments']:
        worker_id = assignment['worker']
        if worker_id not in worker_usage:
            worker_usage[worker_id] = {
                'orders': 0,
                'time_worked': 0,
                'lines_used': set()
            }
        worker_usage[worker_id]['orders'] += 1
        worker_usage[worker_id]['time_worked'] += (assignment['completion'] - assignment['start'])
        worker_usage[worker_id]['lines_used'].add(assignment['line'])

    workers_used = len(worker_usage)
    total_worker_time = sum(usage['time_worked'] for usage in worker_usage.values())
    avg_worker_time = total_worker_time / workers_used if workers_used > 0 else 0

    print(f"\nWorkers utilized: {workers_used}/{data['n_workers']} ({workers_used/data['n_workers']*100:.1f}%)")
    print(f"Average orders per worker: {data['n_orders']/workers_used:.1f}")
    print(f"Average time per worker: {avg_worker_time:.1f} slots ({avg_worker_time*15:.0f} minutes)")

    # Worker movement analysis
    total_movements = sum(len(usage['lines_used']) - 1 for usage in worker_usage.values()
                         if len(usage['lines_used']) > 1)
    workers_who_moved = sum(1 for usage in worker_usage.values() if len(usage['lines_used']) > 1)

    print(f"\nWorker movements:")
    print(f"  Workers who moved between lines: {workers_who_moved}")
    print(f"  Total line switches: {total_movements}")
    if workers_who_moved > 0:
        print(f"  Average switches per moving worker: {total_movements/workers_who_moved:.1f}")

    # Capacity Analysis
    print("\n--- CAPACITY ANALYSIS ---")

    total_available_capacity = data['n_lines'] * data['n_timeslots']
    capacity_used = total_line_time
    capacity_percentage = (capacity_used / total_available_capacity) * 100

    print(f"\nTotal available capacity: {total_available_capacity} line-slots")
    print(f"Capacity used: {capacity_used:.0f} line-slots")
    print(f"Capacity utilization: {capacity_percentage:.2f}%")
    print(f"Reserved capacity: {data['reserved_capacity']*100:.0f}%")
    print(f"Effective available capacity: {(1-data['reserved_capacity'])*100:.0f}%")

    # Completion timeline
    print("\n--- COMPLETION TIMELINE ---")

    completion_by_day = {}
    for order_id, metrics in solution['otif_metrics'].items():
        completion_time = metrics['completion_time']
        day = (completion_time - 1) // 96 + 1  # 96 slots per day (15-min intervals)
        if day not in completion_by_day:
            completion_by_day[day] = 0
        completion_by_day[day] += 1

    print(f"\nOrders completed per day:")
    for day in sorted(completion_by_day.keys()):
        count = completion_by_day[day]
        print(f"  Day {day}: {count} orders ({count/data['n_orders']*100:.1f}%)")

    print("\n" + "="*80)


def main():
    """
    Run the large-scale weekly production example.
    """

    print("="*80)
    print("LARGE-SCALE WEEKLY PRODUCTION EXAMPLE")
    print("Industrial-Scale Production Scheduling")
    print("="*80)

    print("\nSCENARIO:")
    print("  - 48 production lines (large manufacturing facility)")
    print("  - 48 workers (flexible assignment across lines)")
    print("  - 1700 orders to schedule (realistic weekly volume)")
    print("  - 7-day planning horizon (168 hours)")
    print("  - 15-minute time slots (672 time slots total)")
    print("\nThis represents a high-volume, multi-line production operation.")

    # Create data
    print("\n[Step 1] Creating large-scale problem data...")
    data = create_large_scale_weekly_data()

    # Estimate model size
    print("\n[Step 2] Building optimization model...")
    print("\nModel size estimation:")
    n_assignment_vars = data['n_orders'] * data['n_lines'] * data['n_timeslots'] * data['n_workers']
    print(f"  Assignment variables (x): ~{n_assignment_vars:,}")
    print(f"  Total decision variables: ~{n_assignment_vars * 1.5:,.0f} (including auxiliary variables)")
    print("\n  WARNING: This is a large-scale problem!")
    print("  Model building may take several minutes...")
    print("  Solving may take 10-60+ minutes depending on hardware.")

    build_start = time.time()

    try:
        model = PackingScheduleModel(data)
        build_time = time.time() - build_start

        print(f"\n  Model built successfully!")
        print(f"  Build time: {build_time:.2f} seconds")
        print(f"  Variables: {model.model.nvariables():,}")
        print(f"  Constraints: {model.model.nconstraints():,}")

    except MemoryError:
        print("\n  ERROR: Insufficient memory to build model!")
        print("  Try reducing problem size (fewer orders, lines, or time slots)")
        return
    except Exception as e:
        print(f"\n  ERROR building model: {str(e)}")
        raise

    # Solve with time limit and gap tolerance
    print("\n[Step 3] Solving optimization problem...")
    print("\n  Solver settings:")
    print("    Solver: HiGHS (appsi_highs)")
    print("    Time limit: 1800 seconds (30 minutes)")
    print("    MIP gap tolerance: 2% (for faster solving)")
    print("\n  Starting optimization...")
    print("  This may take a while for large problems...")
    print("  (Progress updates from solver may be sparse)\n")

    solve_start = time.time()

    try:
        results = model.solve(
            solver_name='appsi_highs',
            tee=True,  # Show solver output
            time_limit=1800,  # 30 minutes
            mip_rel_gap=0.02  # 2% optimality gap tolerance
        )

        solve_time = time.time() - solve_start

        print(f"\n  Solver finished!")
        print(f"  Solve time: {solve_time:.2f} seconds ({solve_time/60:.1f} minutes)")
        print(f"  Status: {results['status']}")
        print(f"  Termination: {results['termination_condition']}")

        if results['objective_value'] is not None:
            print(f"  Objective value: {results['objective_value']:.2f}")

            # Display solution
            print("\n[Step 4] Solution analysis...")
            model.print_solution_summary()

            # Detailed large-scale analysis
            analyze_large_scale_solution(model, data)

            # Key insights
            solution = model.get_solution()
            on_time_count = sum(1 for order_id, metrics in solution['otif_metrics'].items()
                              if not metrics['late'])

            print("\nKEY INSIGHTS:")
            print(f"  1. OTIF performance: {on_time_count}/{data['n_orders']} orders on-time")
            print(f"  2. Model successfully handled {data['n_orders']} orders across {data['n_lines']} lines")
            print(f"  3. Optimization balanced multiple objectives at industrial scale")
            print(f"  4. Solved in {solve_time/60:.1f} minutes")

            print(f"\n  This demonstrates:")
            print(f"  - Scalability of the optimization model")
            print(f"  - Feasibility of large-scale industrial scheduling")
            print(f"  - Effective resource allocation across 48 lines and 48 workers")
            print(f"  - Weekly production planning capabilities")

        else:
            print("\n  No solution found within time limit!")
            print("  Try:")
            print("    1. Increasing time limit")
            print("    2. Relaxing MIP gap tolerance")
            print("    3. Reducing problem size")
            print("    4. Adjusting capacity constraints")

    except MemoryError:
        print("\n  ERROR: Insufficient memory during solving!")
        print("  The problem may be too large for available RAM.")
    except Exception as e:
        print(f"\n  Error during solving: {str(e)}")
        raise

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)

    total_time = time.time() - build_start
    print(f"\nTotal execution time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")

    print("\nSCALING RECOMMENDATIONS:")
    print("  For even larger problems:")
    print("    - Use more powerful hardware (more RAM, faster CPU)")
    print("    - Increase time limits further")
    print("    - Accept larger MIP gaps (3-5%)")
    print("    - Consider decomposition approaches")
    print("    - Use warm starts from previous solutions")
    print("    - Implement rolling horizon planning")


if __name__ == "__main__":
    main()
