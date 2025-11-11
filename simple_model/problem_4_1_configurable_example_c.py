"""
Configurable Scenario Example for Problem_4_1 Model

This example allows easy configuration of problem dimensions to explore different
scales and scenarios. Simply change the configuration parameters in the CONFIG
section below to test different problem sizes.

EASY CONFIGURATION:
Modify the parameters in the CONFIG section below to create different scenarios:
- n_lines: Number of production lines
- n_workers: Number of available workers
- n_orders: Number of orders to schedule
- n_days: Planning horizon in days
- time_slot_minutes: Duration of each time slot

DEFAULT SCENARIO:
- 2 production lines
- 5 workers
- 10 orders to pack
- 2-day planning horizon
- 15-minute time slots (192 time slots total)

WHAT THIS EXAMPLE DEMONSTRATES:
1. How to easily scale the problem for testing
2. Automatic generation of realistic input parameters
3. Impact of problem size on solving time
4. Flexibility of the Problem_4_1 optimization model

USE CASES:
- Quick prototyping and testing
- Educational demonstrations
- Benchmarking different problem sizes
- Exploring trade-offs between scale and solving time
- Testing different resource configurations

EXPERIMENT IDEAS:
Try these configurations to see different behaviors:

1. **Tiny scenario** (very fast solving, <30 seconds):
   - 1 line, 3 workers, 5 orders, 1 day, 15-min slots

2. **Small scenario** (fast solving, <1 minute):
   - 2 lines, 5 workers, 10 orders, 2 days, 15-min slots

3. **Medium scenario** (moderate solving, 1-5 minutes):
   - 3 lines, 8 workers, 20 orders, 3 days, 15-min slots

4. **Large scenario** (longer solving, 5-15 minutes):
   - 5 lines, 15 workers, 35 orders, 5 days, 15-min slots

5. **Worker shortage** (test resource constraints):
   - 3 lines, 3 workers, 15 orders, 2 days, 15-min slots

6. **Tight deadlines** (test time pressure):
   - 2 lines, 5 workers, 15 orders, 1 day, 15-min slots

This example automatically generates:
- Processing times with realistic distributions
- Due dates distributed across the planning horizon
- Priority weights based on urgency
- Initial inventory (typically zero)
- All required parameters for the Problem_4_1 model
"""

import numpy as np
import time
from packing_model_problem_4_1_c import PackingScheduleModelProblem41c


# ============================================================================
# CONFIGURATION SECTION - CHANGE THESE PARAMETERS TO CREATE DIFFERENT SCENARIOS
# ============================================================================

n_orders_per_day_per_line = 5  # Number of orders per day per line
n_lines = 48          # Number of production lines
nr_days = 1  # Planning horizon in days

CONFIG = {
    # Problem dimensions
    'n_lines': n_lines,              # Number of production lines
    'n_workers': n_lines,            # Number of available workers
    'n_orders': n_orders_per_day_per_line * n_lines * nr_days,            # Number of orders to schedule
    'n_days': nr_days,               # Planning horizon in days
    'time_slot_minutes': 15,   # Duration of each time slot in minutes

    # Processing time settings (in time slots)
    'processing_time_min': 2,  # Minimum processing time
    'processing_time_max': 8,  # Maximum processing time

    # Due date distribution (percentage of orders in each category)
    'urgent_orders_pct': 0.3,      # 30% urgent (early due dates)
    'standard_orders_pct': 0.5,    # 50% standard (middle due dates)
    'flexible_orders_pct': 0.2,    # 20% flexible (late due dates)

    # Priority settings
    'priority_min': 1,         # Minimum priority weight
    'priority_max': 100,       # Maximum priority weight

    # Initial inventory settings
    'initial_inventory_pct': 0.0,  # Percentage of orders with initial inventory (0.0 = none)
    'initial_inventory_amount': 1,  # Amount of initial inventory if any

    # Reserved capacity
    'reserved_capacity': 0.10,     # Reserved capacity (10%)

    # Objective function weights
    'objective_weights': {
        'beta': 1.0,     # WIP weight (work-in-progress)
        'gamma': 0.5,    # Workforce variability weight
        'delta': 0.3     # Unutilized capacity weight
    },

    # Solver settings
    'time_limit': 300,         # Solver time limit in seconds (5 minutes)
    'mip_gap': 0.01,          # MIP gap tolerance (1%)
    'random_seed': 42          # Random seed for reproducibility
}

# ============================================================================
# END OF CONFIGURATION SECTION
# ============================================================================


def calculate_time_slots(n_days, time_slot_minutes):
    """
    Calculate the number of time slots for the given planning horizon.

    Args:
        n_days: Number of days in planning horizon
        time_slot_minutes: Duration of each time slot in minutes

    Returns:
        int: Number of time slots
    """
    minutes_per_day = 24 * 60
    return int((n_days * minutes_per_day) / time_slot_minutes)


def generate_processing_times(n_orders, n_lines, proc_min, proc_max, seed=42):
    """
    Generate realistic processing times for orders across lines.

    Processing times vary by line (some lines faster for certain orders).

    Args:
        n_orders: Number of orders
        n_lines: Number of production lines
        proc_min: Minimum processing time (time slots)
        proc_max: Maximum processing time (time slots)
        seed: Random seed for reproducibility

    Returns:
        np.ndarray: Processing time matrix [orders x lines]
    """
    np.random.seed(seed)

    processing_time = np.zeros((n_orders, n_lines), dtype=int)

    for i in range(n_orders):
        # Base processing time for this order
        base_time = np.random.randint(proc_min, proc_max + 1)

        for j in range(n_lines):
            # Add variation: some lines faster/slower (±30%)
            variation = np.random.uniform(0.7, 1.3)
            processing_time[i, j] = max(proc_min, int(base_time * variation))

    return processing_time


def generate_due_dates(n_orders, n_timeslots, urgent_pct, standard_pct, flexible_pct, seed=42):
    """
    Generate due dates distributed across the planning horizon.

    Args:
        n_orders: Number of orders
        n_timeslots: Total number of time slots
        urgent_pct: Percentage of urgent orders (early due dates)
        standard_pct: Percentage of standard orders (middle due dates)
        flexible_pct: Percentage of flexible orders (late due dates)
        seed: Random seed

    Returns:
        np.ndarray: Due dates for each order
    """
    np.random.seed(seed + 2)

    # Calculate number of orders in each category
    n_urgent = int(n_orders * urgent_pct)
    n_standard = int(n_orders * standard_pct)
    n_flexible = n_orders - n_urgent - n_standard

    # Define time ranges for each category
    urgent_range = (1, max(2, int(n_timeslots * 0.3)))           # First 30% of time
    standard_range = (max(2, int(n_timeslots * 0.3)), int(n_timeslots * 0.7))  # Middle 40%
    flexible_range = (int(n_timeslots * 0.7), n_timeslots)  # Last 30%

    due_dates = []

    # Generate due dates for each category
    if n_urgent > 0:
        due_dates.extend(np.random.randint(urgent_range[0], urgent_range[1] + 1, size=n_urgent))
    if n_standard > 0:
        due_dates.extend(np.random.randint(standard_range[0], standard_range[1] + 1, size=n_standard))
    if n_flexible > 0:
        due_dates.extend(np.random.randint(flexible_range[0], flexible_range[1] + 1, size=n_flexible))

    # Shuffle to randomize order sequence
    np.random.shuffle(due_dates)

    return np.array(due_dates)


def generate_priorities(n_orders, due_dates, n_timeslots, priority_min, priority_max, seed=42):
    """
    Generate priority weights based on due date urgency.

    Earlier due dates get higher priorities.

    Args:
        n_orders: Number of orders
        due_dates: Due date for each order
        n_timeslots: Total time slots
        priority_min: Minimum priority value
        priority_max: Maximum priority value
        seed: Random seed

    Returns:
        np.ndarray: Priority weights for each order
    """
    np.random.seed(seed + 3)

    priority = np.zeros(n_orders, dtype=int)

    for i in range(n_orders):
        # Priority inversely proportional to due date
        # Earlier due dates = higher priority
        urgency_factor = 1 - (due_dates[i] / n_timeslots)

        # Map urgency to priority range
        priority[i] = int(priority_min + urgency_factor * (priority_max - priority_min))

        # Add small random variation
        variation = np.random.randint(-5, 6)
        priority[i] = max(priority_min, min(priority_max, priority[i] + variation))

    return priority


def generate_initial_inventory(n_orders, inventory_pct, inventory_amount, seed=42):
    """
    Generate initial inventory for orders.

    Args:
        n_orders: Number of orders
        inventory_pct: Percentage of orders with initial inventory
        inventory_amount: Amount of inventory per order
        seed: Random seed

    Returns:
        np.ndarray: Initial inventory for each order
    """
    np.random.seed(seed + 4)

    initial_inventory = np.zeros(n_orders, dtype=int)

    if inventory_pct > 0:
        # Select orders to have initial inventory
        n_with_inventory = int(n_orders * inventory_pct)
        orders_with_inv = np.random.choice(n_orders, size=n_with_inventory, replace=False)
        initial_inventory[orders_with_inv] = inventory_amount

    return initial_inventory


def create_configurable_data(config):
    """
    Create problem data based on configuration parameters.

    Args:
        config: Configuration dictionary

    Returns:
        dict: Complete problem data for Problem_4_1 optimization
    """
    print("\n" + "="*80)
    print("GENERATING PROBLEM DATA FROM CONFIGURATION")
    print("="*80)

    # Extract configuration
    n_lines = config['n_lines']
    n_workers = config['n_workers']
    n_orders = config['n_orders']
    n_days = config['n_days']
    time_slot_minutes = config['time_slot_minutes']

    # Calculate time slots
    n_timeslots = calculate_time_slots(n_days, time_slot_minutes)

    print(f"\nProblem Dimensions:")
    print(f"  Orders: {n_orders}")
    print(f"  Lines: {n_lines}")
    print(f"  Workers: {n_workers}")
    print(f"  Planning horizon: {n_days} days ({n_days * 24} hours)")
    print(f"  Time slot duration: {time_slot_minutes} minutes")
    print(f"  Total time slots: {n_timeslots}")

    # Generate processing times
    print(f"\nGenerating processing times...")
    processing_time = generate_processing_times(
        n_orders, n_lines,
        config['processing_time_min'],
        config['processing_time_max'],
        config['random_seed']
    )
    avg_proc_time = processing_time.mean()
    print(f"  Processing time range: {processing_time.min()}-{processing_time.max()} slots")
    print(f"  Average: {avg_proc_time:.1f} slots ({avg_proc_time * time_slot_minutes:.0f} minutes)")

    # Generate initial inventory
    print(f"\nGenerating initial inventory...")
    initial_inventory = generate_initial_inventory(
        n_orders,
        config['initial_inventory_pct'],
        config['initial_inventory_amount'],
        config['random_seed']
    )
    orders_with_inv = np.sum(initial_inventory > 0)
    if orders_with_inv > 0:
        print(f"  Orders with initial inventory: {orders_with_inv}/{n_orders}")
        print(f"  Inventory amount: {config['initial_inventory_amount']}")
    else:
        print(f"  No initial inventory (all orders start from scratch)")

    # Generate due dates
    print(f"\nGenerating due dates...")
    due_date = generate_due_dates(
        n_orders, n_timeslots,
        config['urgent_orders_pct'],
        config['standard_orders_pct'],
        config['flexible_orders_pct'],
        config['random_seed']
    )
    print(f"  Due date range: slot {due_date.min()} to {due_date.max()}")
    print(f"  Urgent orders: {int(n_orders * config['urgent_orders_pct'])} ({config['urgent_orders_pct']*100:.0f}%)")
    print(f"  Standard orders: {int(n_orders * config['standard_orders_pct'])} ({config['standard_orders_pct']*100:.0f}%)")
    print(f"  Flexible orders: {int(n_orders * config['flexible_orders_pct'])} ({config['flexible_orders_pct']*100:.0f}%)")

    # Generate priorities
    print(f"\nGenerating priority weights...")
    priority = generate_priorities(
        n_orders, due_date, n_timeslots,
        config['priority_min'],
        config['priority_max'],
        config['random_seed']
    )
    print(f"  Priority range: {priority.min()}-{priority.max()}")
    print(f"  Average priority: {priority.mean():.1f}")

    print(f"\nReserved capacity: {config['reserved_capacity']*100:.0f}%")

    print(f"\nObjective weights:")
    for key, value in config['objective_weights'].items():
        print(f"  {key}: {value}")

    # Compile data
    data = {
        'n_orders': n_orders,
        'n_lines': n_lines,
        'n_timeslots': n_timeslots,
        'n_workers': n_workers,
        'processing_time': processing_time,
        'initial_inventory': initial_inventory,
        'reserved_capacity': config['reserved_capacity'],
        'due_date': due_date,
        'priority': priority,
        'objective_weights': config['objective_weights']
    }

    print("\n" + "="*80)
    print("DATA GENERATION COMPLETE")
    print("="*80)

    return data


def print_solution_analysis(model, data, config):
    """
    Print analysis of the solution.

    Args:
        model: Solved model
        data: Problem data
        config: Configuration parameters
    """
    solution = model.get_solution()

    print("\n" + "="*80)
    print("SOLUTION ANALYSIS")
    print("="*80)

    # OTIF Performance
    on_time_count = sum(1 for _, ship_info in solution['shipping'].items()
                       if ship_info['on_time'])

    print(f"\n--- DELIVERY PERFORMANCE ---")
    print(f"Orders on-time: {on_time_count}/{data['n_orders']} ({on_time_count/data['n_orders']*100:.1f}%)")

    late_orders = [order_id for order_id, ship_info in solution['shipping'].items()
                   if not ship_info['on_time']]
    if late_orders:
        print(f"Late orders: {late_orders}")

    # Resource utilization
    print(f"\n--- RESOURCE UTILIZATION ---")

    # Line usage
    lines_used = len(set(a['line'] for a in solution['assignments']))
    print(f"Lines used: {lines_used}/{data['n_lines']} ({lines_used/data['n_lines']*100:.1f}%)")

    # Worker usage summary
    ws = solution['workforce_summary']
    print(f"Workers used:")
    print(f"  Maximum: {ws['max']} workers")
    print(f"  Minimum: {ws['min']} workers")
    print(f"  Range: {ws['range']} workers")
    print(f"  Average: {np.mean(list(solution['workforce'].values())):.1f} workers")

    # Time metrics
    completion_times = [a['completion'] for a in solution['assignments']]
    latest_completion = max(completion_times)
    time_slot_minutes = config['time_slot_minutes']

    print(f"\n--- TIMELINE ---")
    print(f"First order starts: slot {min(a['start'] for a in solution['assignments'])}")
    print(f"Latest completion: slot {latest_completion} ({latest_completion * time_slot_minutes / 60:.1f} hours)")
    print(f"Planning horizon: {data['n_timeslots']} slots ({data['n_timeslots'] * time_slot_minutes / 60:.0f} hours)")
    print(f"Utilization: {latest_completion/data['n_timeslots']*100:.1f}% of available time")

    # Inventory analysis
    print(f"\n--- INVENTORY METRICS ---")
    total_inv = sum(sum(inv_data.values()) for inv_data in solution['inventory'].values())
    avg_inv = total_inv / (data['n_orders'] * data['n_timeslots'])
    max_inv = max(max(inv_data.values()) for inv_data in solution['inventory'].values())
    print(f"Total inventory-time: {total_inv}")
    print(f"Average inventory: {avg_inv:.2f}")
    print(f"Maximum inventory: {max_inv}")

    print("\n" + "="*80)


def print_detailed_schedule(solution, config, max_orders_to_show=10):
    """
    Print a detailed schedule of assignments.

    Args:
        solution: Solution dictionary
        config: Configuration parameters
        max_orders_to_show: Maximum number of orders to display in detail
    """
    print("\n" + "="*80)
    print("DETAILED SCHEDULE")
    print("="*80)

    time_slot_minutes = config['time_slot_minutes']

    # Sort assignments by start time
    sorted_assignments = sorted(solution['assignments'], key=lambda x: (x['start'], x['line']))

    print(f"\nShowing first {min(len(sorted_assignments), max_orders_to_show)} assignments:")
    print(f"\n{'Order':<8} {'Line':<6} {'Start':<8} {'End':<8} {'Duration':<10} {'Ship':<8} {'Due':<8} {'Status':<10}")
    print("-"*80)

    for idx, assignment in enumerate(sorted_assignments[:max_orders_to_show]):
        order_id = assignment['order']
        ship_info = solution['shipping'][order_id]

        start_time_hrs = assignment['start'] * time_slot_minutes / 60
        end_time_hrs = assignment['completion'] * time_slot_minutes / 60
        duration_hrs = assignment['processing_time'] * time_slot_minutes / 60

        status = "ON-TIME" if ship_info['on_time'] else "LATE"

        print(f"{order_id:<8} {assignment['line']:<6} "
              f"{assignment['start']:<8} {assignment['completion']:<8} "
              f"{duration_hrs:<10.1f} "
              f"{ship_info['ship_time']:<8} {ship_info['due_date']:<8} {status:<10}")

    if len(sorted_assignments) > max_orders_to_show:
        print(f"\n... and {len(sorted_assignments) - max_orders_to_show} more orders")

    print("="*80)


def main():
    """
    Run the configurable scenario example for Problem_4_1.
    """

    print("="*80)
    print("PROBLEM_4_1 CONFIGURABLE SCENARIO EXAMPLE")
    print("Flexible Problem Size Configuration")
    print("="*80)

    print("\nCURRENT CONFIGURATION:")
    print(f"  Lines: {CONFIG['n_lines']}")
    print(f"  Workers: {CONFIG['n_workers']}")
    print(f"  Orders: {CONFIG['n_orders']}")
    print(f"  Planning horizon: {CONFIG['n_days']} days")
    print(f"  Time slot: {CONFIG['time_slot_minutes']} minutes")

    n_timeslots = calculate_time_slots(CONFIG['n_days'], CONFIG['time_slot_minutes'])
    print(f"\n  This creates: {n_timeslots} time slots")
    print(f"  Problem scale: {CONFIG['n_orders']} orders × {CONFIG['n_lines']} lines × {n_timeslots} slots")

    estimated_vars = CONFIG['n_orders'] * CONFIG['n_lines'] * n_timeslots
    print(f"  Estimated assignment variables: ~{estimated_vars:,}")

    if estimated_vars > 1_000_000:
        print(f"\n  WARNING: Large problem size! May require significant time and memory.")
    elif estimated_vars > 100_000:
        print(f"\n  NOTE: Moderate problem size. Solving may take several minutes.")
    else:
        print(f"\n  NOTE: Small problem size. Should solve quickly (<1 minute).")

    # Create data
    print("\n[Step 1] Creating problem data from configuration...")
    start_time = time.time()
    data = create_configurable_data(CONFIG)
    data_time = time.time() - start_time
    print(f"\nData creation time: {data_time:.2f} seconds")

    # Build model
    print("\n[Step 2] Building Problem_4_1 optimization model...")
    build_start = time.time()
    model = PackingScheduleModelProblem41c(data)
    build_time = time.time() - build_start

    print(f"\nModel built successfully!")
    print(f"  Build time: {build_time:.2f} seconds")

    # Solve
    print(f"\n[Step 3] Solving optimization problem...")
    print(f"  Solver: HiGHS")
    print(f"  Time limit: {CONFIG['time_limit']} seconds")
    print(f"  MIP gap: {CONFIG['mip_gap']*100}%")
    print(f"\nSolving... (this may take a while for large problems)")

    solve_start = time.time()

    results = model.solve(
        solver_name='appsi_highs',
        tee=True,
        time_limit=CONFIG['time_limit'],
        mip_rel_gap=CONFIG['mip_gap']
    )

    solve_time = time.time() - solve_start

    print(f"\n\nSolver finished!")
    print(f"  Solve time: {solve_time:.2f} seconds")
    print(f"  Status: {results['status']}")

    if results['objective_value'] is not None:
        print(f"  Objective value: {results['objective_value']:.2f}")

        # Display solution
        print("\n[Step 4] Solution summary...")
        model.print_solution_summary()

        # Detailed analysis
        print_solution_analysis(model, data, CONFIG)

        # Detailed schedule
        print_detailed_schedule(model.get_solution(), CONFIG, max_orders_to_show=15)

        # Key insights
        print("\n" + "="*80)
        print("KEY INSIGHTS")
        print("="*80)
        solution = model.get_solution()
        on_time = sum(1 for _, s in solution['shipping'].items() if s['on_time'])

        print(f"\n  ✓ Achieved {on_time/data['n_orders']*100:.1f}% on-time delivery rate")
        print(f"  ✓ Optimized schedule across {CONFIG['n_lines']} lines with up to {solution['workforce_summary']['max']} workers")
        print(f"  ✓ Solved in {solve_time:.2f} seconds")
        print(f"  ✓ Workforce range: {solution['workforce_summary']['range']} (max-min workers)")

        if on_time == data['n_orders']:
            print(f"\n  🎉 Perfect! All orders delivered on time!")
        elif on_time / data['n_orders'] >= 0.9:
            print(f"\n  ✓ Excellent performance with >90% on-time delivery!")
        elif on_time / data['n_orders'] >= 0.7:
            print(f"\n  ⚠️ Good performance, but some orders are late. Consider:")
            print(f"     - Increasing number of lines")
            print(f"     - Increasing number of workers")
            print(f"     - Extending planning horizon")
        else:
            print(f"\n  ⚠️ Many orders are late. Consider:")
            print(f"     - Significantly increasing resources")
            print(f"     - Extending planning horizon")
            print(f"     - Relaxing due date constraints")

    else:
        print("\n❌ No solution found!")
        print("\nPossible reasons:")
        print("  - Time limit too short")
        print("  - Problem is infeasible (not enough capacity)")
        print("  - Due dates too tight")
        print("\nTry:")
        print("  - Increasing time_limit in CONFIG")
        print("  - Increasing n_lines or n_workers")
        print("  - Increasing n_days (planning horizon)")
        print("  - Reducing reserved_capacity")

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)

    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

    print("\nTO TRY DIFFERENT SCENARIOS:")
    print("  1. Edit the CONFIG dictionary at the top of this file")
    print("  2. Change n_lines, n_workers, n_orders, n_days, time_slot_minutes, etc.")
    print("  3. Run again to see how the model handles different scales!")
    print("\nEXPERIMENT SUGGESTIONS:")
    print("  - Try n_workers < n_lines to see resource constraints")
    print("  - Try n_orders > 20 with n_days = 1 to see tight scheduling")
    print("  - Try different time_slot_minutes (5, 10, 15, 30) to see granularity effects")


if __name__ == "__main__":
    main()
