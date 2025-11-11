"""
Configurable Scenario Example - Flexible Problem Size Configuration

This example allows easy configuration of problem dimensions to explore different
scales and scenarios. Simply change the configuration parameters at the top of the
script to test different problem sizes.

EASY CONFIGURATION:
Modify the parameters in the CONFIG section below to create different scenarios:
- n_lines: Number of production lines
- n_workers: Number of available workers
- n_orders: Number of orders to schedule
- n_days: Planning horizon in days
- time_slot_minutes: Duration of each time slot

DEFAULT SCENARIO:
- 2 production lines
- 2 workers (enables parallel processing)
- 10 orders to pack
- 2-day planning horizon
- 30-minute time slots (96 time slots total)

WHAT THIS EXAMPLE DEMONSTRATES:
1. How to easily scale the problem for testing
2. Automatic generation of realistic input parameters
3. Impact of problem size on solving time
4. Flexibility of the optimization model

USE CASES:
- Quick prototyping and testing
- Educational demonstrations
- Benchmarking different problem sizes
- Exploring trade-offs between scale and solving time
- Testing different resource configurations

EXPERIMENT IDEAS:
Try these configurations to see different behaviors:

1. **Small scenario** (fast solving, <1 minute):
   - 2 lines, 2 workers, 10 orders, 2 days

2. **Medium scenario** (moderate solving, 1-5 minutes):
   - 5 lines, 5 workers, 50 orders, 3 days

3. **Large scenario** (longer solving, 5-20 minutes):
   - 10 lines, 10 workers, 200 orders, 5 days

4. **Worker shortage** (test resource constraints):
   - 5 lines, 2 workers, 30 orders, 2 days

5. **Line shortage** (test capacity constraints):
   - 2 lines, 5 workers, 30 orders, 2 days

This example automatically generates:
- Processing times with realistic distributions
- Setup times based on product families
- Due dates distributed across the planning horizon
- Priority weights based on urgency
- Worker availability (24/7 by default)
- All required parameters for the optimization model
"""

import numpy as np
import sys
import os
import time

# Add src directory to path to import packing_model
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from packing_model import PackingScheduleModel


# ============================================================================
# CONFIGURATION SECTION - CHANGE THESE PARAMETERS TO CREATE DIFFERENT SCENARIOS
# ============================================================================
n_orders_per_day_per_line = 5  # Number of orders per day per line
n_lines = 1          # Number of production lines
nr_days = 2  # Planning horizon in days

CONFIG = {
    # Problem dimensions
    'n_lines': n_lines,              # Number of production lines
    'n_workers': n_lines,            # Number of available workers
    'n_orders': n_orders_per_day_per_line * n_lines * nr_days,            # Number of orders to schedule
    'n_days': nr_days,               # Planning horizon in days
    'time_slot_minutes': 15,   # Duration of each time slot in minutes

    # Processing time settings (in time slots)
    'processing_time_min': 1,  # Minimum processing time
    'processing_time_max': 6,  # Maximum processing time

    # Product family settings
    'n_product_families': 3,   # Number of product families for setup times
    'setup_time_same_family': 0,   # Setup time within same family (time slots)
    'setup_time_diff_family': 1,   # Setup time between different families (time slots)

    # Due date distribution (percentage of orders in each category)
    'urgent_orders_pct': 0.3,      # 30% urgent (early due dates)
    'standard_orders_pct': 0.5,    # 50% standard (middle due dates)
    'flexible_orders_pct': 0.2,    # 20% flexible (late due dates)

    # Priority settings
    'priority_min': 50,        # Minimum priority weight
    'priority_max': 100,       # Maximum priority weight

    # Workforce settings
    'workforce_target_pct': 0.7,   # Target workforce utilization (70%)
    'reserved_capacity': 0.10,     # Reserved capacity (10%)

    # Objective function weights
    'objective_weights': {
        'alpha': 5.0,    # OTIF weight (on-time delivery)
        'beta': 0.2,     # WIP weight (work-in-progress)
        'gamma': 0.1,    # Workforce variability weight
        'delta': 0.5,    # Line utilization weight
        'omega': 0.5     # Worker movement penalty
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


def generate_setup_times(n_orders, n_lines, n_families, same_family_setup, diff_family_setup, seed=42):
    """
    Generate setup times based on product families.

    Args:
        n_orders: Number of orders
        n_lines: Number of lines
        n_families: Number of product families
        same_family_setup: Setup time within same family (time slots)
        diff_family_setup: Setup time between different families (time slots)
        seed: Random seed

    Returns:
        tuple: (setup_time matrix, order_families array)
    """
    np.random.seed(seed + 1)

    # Assign each order to a product family
    order_families = np.random.randint(0, n_families, size=n_orders)

    # Create setup time matrix
    setup_time = np.zeros((n_orders, n_orders, n_lines))

    for i in range(n_orders):
        for k in range(n_orders):
            if i == k:
                setup_time[i, k, :] = 0  # No setup for same order
            elif order_families[i] == order_families[k]:
                setup_time[i, k, :] = same_family_setup  # Same family
            else:
                setup_time[i, k, :] = diff_family_setup  # Different family

    return setup_time, order_families


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
    urgent_range = (1, int(n_timeslots * 0.3))           # First 30% of time
    standard_range = (int(n_timeslots * 0.3), int(n_timeslots * 0.7))  # Middle 40%
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


def create_configurable_data(config):
    """
    Create problem data based on configuration parameters.

    Args:
        config: Configuration dictionary

    Returns:
        dict: Complete problem data for optimization
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

    # Generate setup times
    print(f"\nGenerating setup times ({config['n_product_families']} product families)...")
    setup_time, order_families = generate_setup_times(
        n_orders, n_lines,
        config['n_product_families'],
        config['setup_time_same_family'],
        config['setup_time_diff_family'],
        config['random_seed']
    )
    print(f"  Setup within family: {config['setup_time_same_family']} slots")
    print(f"  Setup between families: {config['setup_time_diff_family']} slots")

    # Product family distribution
    family_counts = {}
    for family in order_families:
        family_counts[family] = family_counts.get(family, 0) + 1
    print(f"  Orders per family: {dict(sorted(family_counts.items()))}")

    # Worker availability (24/7)
    print(f"\nSetting worker availability (24/7 operation)...")
    worker_availability = np.ones((n_workers, n_timeslots))

    # No initial inventory
    initial_inventory = np.zeros(n_orders, dtype=int)

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
    print(f"  Urgent orders: {int(n_orders * config['urgent_orders_pct'])}")
    print(f"  Standard orders: {int(n_orders * config['standard_orders_pct'])}")
    print(f"  Flexible orders: {int(n_orders * config['flexible_orders_pct'])}")

    # Generate priorities
    print(f"\nGenerating priority weights...")
    priority = generate_priorities(
        n_orders, due_date, n_timeslots,
        config['priority_min'],
        config['priority_max'],
        config['random_seed']
    )
    print(f"  Priority range: {priority.min()}-{priority.max()}")

    # Workforce target
    workforce_target = max(1, int(n_workers * config['workforce_target_pct']))
    print(f"\nWorkforce target: {workforce_target} workers ({config['workforce_target_pct']*100:.0f}% utilization)")

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
        'setup_time': setup_time,
        'worker_availability': worker_availability,
        'initial_inventory': initial_inventory,
        'reserved_capacity': config['reserved_capacity'],
        'due_date': due_date,
        'priority': priority,
        'workforce_target': workforce_target,
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
    on_time_count = sum(1 for _, metrics in solution['otif_metrics'].items()
                       if not metrics['late'])

    print(f"\n--- OTIF PERFORMANCE ---")
    print(f"Orders on-time: {on_time_count}/{data['n_orders']} ({on_time_count/data['n_orders']*100:.1f}%)")

    # Resource utilization
    print(f"\n--- RESOURCE UTILIZATION ---")

    # Line usage
    lines_used = len(set(a['line'] for a in solution['assignments']))
    print(f"Lines used: {lines_used}/{data['n_lines']} ({lines_used/data['n_lines']*100:.1f}%)")

    # Worker usage
    workers_used = len(set(a['worker'] for a in solution['assignments']))
    print(f"Workers used: {workers_used}/{data['n_workers']} ({workers_used/data['n_workers']*100:.1f}%)")

    # Time metrics
    completion_times = [a['completion'] for a in solution['assignments']]
    latest_completion = max(completion_times)
    time_slot_minutes = config['time_slot_minutes']

    print(f"\n--- TIMELINE ---")
    print(f"Latest completion: slot {latest_completion} ({latest_completion * time_slot_minutes / 60:.1f} hours)")
    print(f"Planning horizon: {data['n_timeslots']} slots ({data['n_timeslots'] * time_slot_minutes / 60:.0f} hours)")
    print(f"Utilization: {latest_completion/data['n_timeslots']*100:.1f}% of available time")

    print("\n" + "="*80)


def main():
    """
    Run the configurable scenario example.
    """

    print("="*80)
    print("CONFIGURABLE SCENARIO EXAMPLE")
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
    print(f"  Problem scale: {CONFIG['n_orders']} orders × {CONFIG['n_lines']} lines × {n_timeslots} slots × {CONFIG['n_workers']} workers")

    estimated_vars = CONFIG['n_orders'] * CONFIG['n_lines'] * n_timeslots * CONFIG['n_workers']
    print(f"  Estimated assignment variables: ~{estimated_vars:,}")

    if estimated_vars > 10_000_000:
        print(f"\n  WARNING: Large problem size! May require significant time and memory.")
    elif estimated_vars > 1_000_000:
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
    print("\n[Step 2] Building optimization model...")
    build_start = time.time()
    model = PackingScheduleModel(data)
    build_time = time.time() - build_start

    print(f"\nModel built successfully!")
    print(f"  Build time: {build_time:.2f} seconds")
    print(f"  Variables: {model.model.nvariables():,}")
    print(f"  Constraints: {model.model.nconstraints():,}")

    # Solve
    print(f"\n[Step 3] Solving optimization problem...")
    print(f"  Time limit: {CONFIG['time_limit']} seconds")
    print(f"  MIP gap: {CONFIG['mip_gap']*100}%")

    solve_start = time.time()

    results = model.solve(
        solver_name='appsi_highs',
        tee=False,
        time_limit=CONFIG['time_limit'],
        mip_rel_gap=CONFIG['mip_gap']
    )

    solve_time = time.time() - solve_start

    print(f"\nSolver finished!")
    print(f"  Solve time: {solve_time:.2f} seconds")
    print(f"  Status: {results['status']}")
    print(f"  Termination: {results['termination_condition']}")

    if results['objective_value'] is not None:
        print(f"  Objective value: {results['objective_value']:.2f}")

        # Display solution
        print("\n[Step 4] Solution summary...")
        model.print_solution_summary()

        # Custom analysis
        print_solution_analysis(model, data, CONFIG)

        print("\nKEY INSIGHTS:")
        solution = model.get_solution()
        on_time = sum(1 for _, m in solution['otif_metrics'].items() if not m['late'])
        print(f"  1. Achieved {on_time/data['n_orders']*100:.1f}% on-time delivery rate")
        print(f"  2. Optimized schedule across {CONFIG['n_lines']} lines with {CONFIG['n_workers']} workers")
        print(f"  3. Solved in {solve_time:.2f} seconds")

    else:
        print("\nNo solution found!")
        print("Try:")
        print("  - Increasing time limit")
        print("  - Relaxing constraints")
        print("  - Reducing problem size")

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)

    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

    print("\nTO TRY DIFFERENT SCENARIOS:")
    print("  Edit the CONFIG dictionary at the top of this file")
    print("  Change n_lines, n_workers, n_orders, n_days, etc.")
    print("  Run again to see how the model handles different scales!")


if __name__ == "__main__":
    main()
