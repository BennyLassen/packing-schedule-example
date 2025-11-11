"""
Configurable Scenario Example for Problem_4_1_c2 Model

This example allows easy configuration of problem dimensions to explore different
scales and scenarios. Simply change the configuration parameters in the CONFIG
section below to test different problem sizes.

EASY CONFIGURATION:
Modify the parameters in the CONFIG section below to create different scenarios:
- n_types: Number of unique product types
- n_lines: Number of production lines
- n_orders: Number of production orders to schedule
- n_demands: Number of shipping demands
- planning_horizon: Planning horizon in time units

DEFAULT SCENARIO:
- 2 product types
- 2 production lines
- 8 orders to produce
- 4 shipping demands
- 100 time unit planning horizon

WHAT THIS EXAMPLE DEMONSTRATES:
1. How to easily scale the problem for testing
2. Automatic generation of realistic input parameters
3. Impact of problem size on solving time
4. Flexibility of the Problem_4_1_c2 optimization model

KEY DIFFERENCES FROM PROBLEM_4_1:
- Uses continuous time (not discrete time slots)
- Models demands that ship at specific times
- Tracks inventory after each demand ships
- Each order produces exactly 1 unit of its product type

USE CASES:
- Quick prototyping and testing
- Educational demonstrations
- Benchmarking different problem sizes
- Exploring trade-offs between scale and solving time
- Testing different resource configurations

EXPERIMENT IDEAS:
Try these configurations to see different behaviors:

1. **Tiny scenario** (very fast solving, <30 seconds):
   - 1 type, 1 line, 2 orders, 1 demand, horizon 50

2. **Small scenario** (fast solving, <1 minute):
   - 2 types, 2 lines, 8 orders, 4 demands, horizon 100

3. **Medium scenario** (moderate solving, 1-5 minutes):
   - 3 types, 3 lines, 15 orders, 8 demands, horizon 150

4. **Large scenario** (longer solving, 5-15 minutes):
   - 4 types, 5 lines, 25 orders, 12 demands, horizon 200

5. **Type diversity** (test multiple product types):
   - 5 types, 3 lines, 20 orders, 10 demands, horizon 150

6. **Tight deadlines** (test time pressure):
   - 2 types, 2 lines, 10 orders, 5 demands, horizon 60

This example automatically generates:
- Processing times with realistic distributions by type and line
- Setup times for changing between product types
- Due dates distributed across the planning horizon
- Demand quantities that match order types
- Priority weights based on urgency
- Initial inventory (configurable)
- All required parameters for the Problem_4_1_c2 model
"""

import numpy as np
import time
from packing_model_problem_4_1_c2 import PackingScheduleModelProblem4_1_c2


# ============================================================================
# CONFIGURATION SECTION - CHANGE THESE PARAMETERS TO CREATE DIFFERENT SCENARIOS
# ============================================================================

n_orders_per_day_per_line = 5  # Number of orders per day per line
n_lines = 24          # Number of production lines
nr_days = 1  # Planning horizon in days

CONFIG = {
    # Problem dimensions
    'n_types': 2,              # Number of unique product types
    'n_lines': n_lines,              # Number of production lines
    'n_demands': n_orders_per_day_per_line * n_lines * nr_days,            # Number of shipping demands
    # NOTE: n_orders will be calculated automatically based on demands
    'planning_horizon': 100.0, # Planning horizon in time units

    # Processing time settings (in time units)
    'processing_time_min': 8.0,   # Minimum processing time
    'processing_time_max': 15.0,  # Maximum processing time

    # Setup time settings (in time units)
    'setup_time_same_type': 0.0,  # Setup time when switching to same type
    'setup_time_diff_type': 5.0,  # Setup time when switching to different type

    # Due date distribution
    'due_date_start_pct': 0.3,    # First due date at 30% of horizon
    'due_date_end_pct': 0.9,      # Last due date at 90% of horizon

    # Demand quantity settings
    'demand_qty_min': 1,          # Minimum quantity per demand
    'demand_qty_max': 1,          # Maximum quantity per demand

    # Priority settings
    'priority_min': 5,            # Minimum priority weight
    'priority_max': 20,           # Maximum priority weight

    # Initial inventory settings
    'initial_inventory_pct': 0.0, # Percentage of types with initial inventory (0.0 = none)
    'initial_inventory_max': 2,   # Maximum initial inventory per type

    # Objective function weights
    'objective_weights': {
        'beta': 1.0,     # WIP weight (work-in-progress / inventory)
        'gamma': 2.0,    # Workforce variability weight
        'delta': 0.5     # Unutilized capacity weight
    },

    # Solver settings
    'time_limit': 300,         # Solver time limit in seconds (5 minutes)
    'mip_gap': 0.01,          # MIP gap tolerance (1%)
    'random_seed': 42          # Random seed for reproducibility
}

# ============================================================================
# END OF CONFIGURATION SECTION
# ============================================================================


def generate_processing_times(n_types, n_lines, proc_min, proc_max, seed=42):
    """
    Generate realistic processing times for each product type on each line.

    Processing times vary by type and line (some lines faster for certain types).

    Args:
        n_types: Number of product types
        n_lines: Number of production lines
        proc_min: Minimum processing time
        proc_max: Maximum processing time
        seed: Random seed for reproducibility

    Returns:
        np.ndarray: Processing time matrix [types x lines]
    """
    np.random.seed(seed)

    processing_time = np.zeros((n_types, n_lines))

    for u in range(n_types):
        # Base processing time for this type
        base_time = np.random.uniform(proc_min, proc_max)

        for j in range(n_lines):
            # Add variation: some lines faster/slower for each type (±20%)
            variation = np.random.uniform(0.8, 1.2)
            processing_time[u, j] = max(proc_min, base_time * variation)

    return processing_time


def generate_setup_times(n_types, setup_same, setup_diff, seed=42):
    """
    Generate setup times for switching between product types.

    Args:
        n_types: Number of product types
        setup_same: Setup time for same type (typically 0)
        setup_diff: Setup time for different types
        seed: Random seed

    Returns:
        np.ndarray: Setup time matrix [types x types]
    """
    np.random.seed(seed + 1)

    setup_time = np.zeros((n_types, n_types))

    for u in range(n_types):
        for v in range(n_types):
            if u == v:
                setup_time[u, v] = setup_same
            else:
                # Add some variation to setup times (±20%)
                variation = np.random.uniform(0.8, 1.2)
                setup_time[u, v] = setup_diff * variation

    return setup_time


def generate_order_types_from_demands(demand_types, demand_quantities, seed=42):
    """
    Assign product type to each order based on demand requirements.

    Creates exactly the number of orders needed to fulfill all demands,
    with the correct distribution by type.

    Args:
        demand_types: Type of each demand
        demand_quantities: Quantity of each demand
        seed: Random seed

    Returns:
        np.ndarray: Type assignment for each order (1-indexed)
    """
    np.random.seed(seed + 2)

    # Calculate required orders per type
    type_orders_needed = {}
    for d in range(len(demand_types)):
        u = demand_types[d]
        if u not in type_orders_needed:
            type_orders_needed[u] = 0
        type_orders_needed[u] += demand_quantities[d]

    # Create order list
    order_types = []
    for u, count in sorted(type_orders_needed.items()):
        order_types.extend([u] * count)

    # Shuffle to randomize order sequence (but preserve type counts)
    np.random.shuffle(order_types)

    return np.array(order_types)


def generate_demands(n_demands, n_types, planning_horizon,
                     due_start_pct, due_end_pct, qty_min, qty_max, seed=42):
    """
    Generate shipping demands with due dates and quantities.

    Args:
        n_demands: Number of demands
        n_types: Number of product types
        planning_horizon: Total planning time
        due_start_pct: Earliest due date as percentage of horizon
        due_end_pct: Latest due date as percentage of horizon
        qty_min: Minimum quantity per demand
        qty_max: Maximum quantity per demand
        seed: Random seed

    Returns:
        tuple: (due_dates, demand_types, demand_quantities)
    """
    np.random.seed(seed + 3)

    # Generate due dates spread across the horizon
    due_start = planning_horizon * due_start_pct
    due_end = planning_horizon * due_end_pct

    due_dates = np.linspace(due_start, due_end, n_demands)

    # Add some randomness to due dates (±10% variation)
    variation = np.random.uniform(0.9, 1.1, n_demands)
    due_dates = due_dates * variation

    # Ensure within bounds
    due_dates = np.clip(due_dates, due_start, due_end)

    # Sort due dates
    due_dates = np.sort(due_dates)

    # Assign types to demands (distribute evenly)
    demand_types = []
    for u in range(1, n_types + 1):
        count = n_demands // n_types
        if u <= (n_demands % n_types):
            count += 1
        demand_types.extend([u] * count)

    # Shuffle types
    np.random.shuffle(demand_types)
    demand_types = np.array(demand_types[:n_demands])

    # Generate quantities
    demand_quantities = np.random.randint(qty_min, qty_max + 1, n_demands)

    return due_dates, demand_types, demand_quantities


def generate_priorities(n_orders, order_types, demand_types, due_dates,
                        priority_min, priority_max, seed=42):
    """
    Generate priority weights for orders based on demand urgency.

    Orders for types with earlier demands get higher priority.

    Args:
        n_orders: Number of orders
        order_types: Type of each order
        demand_types: Type of each demand
        due_dates: Due date of each demand
        priority_min: Minimum priority value
        priority_max: Maximum priority value
        seed: Random seed

    Returns:
        np.ndarray: Priority weights for each order
    """
    np.random.seed(seed + 4)

    priority = np.zeros(n_orders, dtype=int)

    # Find earliest due date for each type
    type_earliest_due = {}
    for d in range(len(demand_types)):
        u = demand_types[d]
        if u not in type_earliest_due or due_dates[d] < type_earliest_due[u]:
            type_earliest_due[u] = due_dates[d]

    max_due = max(due_dates)

    for i in range(n_orders):
        order_type = order_types[i]

        if order_type in type_earliest_due:
            # Priority inversely proportional to earliest due date for this type
            urgency_factor = 1 - (type_earliest_due[order_type] / max_due)
        else:
            urgency_factor = 0.5

        # Map urgency to priority range
        priority[i] = int(priority_min + urgency_factor * (priority_max - priority_min))

        # Add small random variation
        variation = np.random.randint(-2, 3)
        priority[i] = max(priority_min, min(priority_max, priority[i] + variation))

    return priority


def generate_initial_inventory(n_types, inventory_pct, inventory_max, seed=42):
    """
    Generate initial inventory for product types.

    Args:
        n_types: Number of product types
        inventory_pct: Percentage of types with initial inventory
        inventory_max: Maximum inventory per type
        seed: Random seed

    Returns:
        np.ndarray: Initial inventory for each type
    """
    np.random.seed(seed + 5)

    initial_inventory = np.zeros(n_types, dtype=int)

    if inventory_pct > 0:
        # Select types to have initial inventory
        n_with_inventory = max(1, int(n_types * inventory_pct))
        types_with_inv = np.random.choice(n_types, size=n_with_inventory, replace=False)

        for u in types_with_inv:
            initial_inventory[u] = np.random.randint(1, inventory_max + 1)

    return initial_inventory


def create_configurable_data(config):
    """
    Create problem data based on configuration parameters.

    Args:
        config: Configuration dictionary

    Returns:
        dict: Complete problem data for Problem_4_1_c2 optimization
    """
    print("\n" + "="*80)
    print("GENERATING PROBLEM DATA FROM CONFIGURATION")
    print("="*80)

    # Extract configuration
    n_types = config['n_types']
    n_lines = config['n_lines']
    n_demands = config['n_demands']
    T_max = config['planning_horizon']

    print(f"\nInitial Problem Dimensions:")
    print(f"  Product types: {n_types}")
    print(f"  Shipping demands: {n_demands}")
    print(f"  Production lines: {n_lines}")
    print(f"  Planning horizon: {T_max} time units")

    # Generate demands FIRST (before orders)
    print(f"\nGenerating shipping demands...")
    due_date, demand_type, demand_qty = generate_demands(
        n_demands, n_types, T_max,
        config['due_date_start_pct'],
        config['due_date_end_pct'],
        config['demand_qty_min'],
        config['demand_qty_max'],
        config['random_seed']
    )
    print(f"  Due date range: {due_date.min():.1f} to {due_date.max():.1f}")
    print(f"  Total demand quantity: {demand_qty.sum()} units")

    # Show demand breakdown by type
    print(f"\n  Demand by type:")
    for u in range(1, n_types + 1):
        type_demand = np.sum(demand_qty[demand_type == u])
        print(f"    Type {u}: {type_demand} units")

    # Calculate required number of orders based on demands
    n_orders = int(demand_qty.sum())
    print(f"\n  Calculated production orders needed: {n_orders} (= total demand quantity)")

    # Generate order types to match demand requirements exactly
    print(f"\nGenerating order assignments (matching demand requirements)...")
    order_type = generate_order_types_from_demands(
        demand_type, demand_qty, config['random_seed']
    )

    # Verify order type distribution
    for u in range(1, n_types + 1):
        count = np.sum(order_type == u)
        type_demand = np.sum(demand_qty[demand_type == u])
        print(f"  Type {u}: {count} orders (matches {type_demand} demand)")

    print(f"\n  Average orders per type: {n_orders / n_types:.1f}")
    print(f"  Average demands per type: {n_demands / n_types:.1f}")

    # Generate processing times
    print(f"\nGenerating processing times...")
    processing_time = generate_processing_times(
        n_types, n_lines,
        config['processing_time_min'],
        config['processing_time_max'],
        config['random_seed']
    )
    avg_proc_time = processing_time.mean()
    print(f"  Processing time range: {processing_time.min():.1f}-{processing_time.max():.1f} time units")
    print(f"  Average: {avg_proc_time:.1f} time units")

    # Generate setup times
    print(f"\nGenerating setup times...")
    setup_time = generate_setup_times(
        n_types,
        config['setup_time_same_type'],
        config['setup_time_diff_type'],
        config['random_seed']
    )
    avg_setup = np.mean(setup_time[setup_time > 0]) if np.any(setup_time > 0) else 0
    print(f"  Setup time (same type): {config['setup_time_same_type']:.1f} time units")
    print(f"  Setup time (different type): {avg_setup:.1f} time units (average)")

    # Generate initial inventory (optional, default is 0)
    print(f"\nGenerating initial inventory...")
    initial_inventory = generate_initial_inventory(
        n_types,
        config['initial_inventory_pct'],
        config['initial_inventory_max'],
        config['random_seed']
    )
    total_initial_inv = np.sum(initial_inventory)
    if total_initial_inv > 0:
        print(f"  Total initial inventory: {total_initial_inv} units")
        for u in range(n_types):
            if initial_inventory[u] > 0:
                print(f"    Type {u+1}: {initial_inventory[u]} units")
    else:
        print(f"  No initial inventory (all production from orders)")

    # Capacity check (should be perfect by construction)
    total_capacity_needed = demand_qty.sum()
    total_capacity_available = n_orders + total_initial_inv
    print(f"\n  Capacity verification:")
    print(f"    Total demand: {total_capacity_needed} units")
    print(f"    Production capacity: {n_orders} orders + {total_initial_inv} inventory = {total_capacity_available} units")

    if total_capacity_available < total_capacity_needed:
        print(f"    [ERROR] Insufficient capacity! Short by {total_capacity_needed - total_capacity_available} units")
        print(f"    This should not happen - check data generation logic!")
    elif total_capacity_available == total_capacity_needed:
        print(f"    [OK] Perfect match: Capacity exactly meets demand")
    else:
        print(f"    [OK] Excess capacity: {total_capacity_available - total_capacity_needed} units (from initial inventory)")

    # Verify by type
    print(f"\n  Capacity verification by type:")
    for u in range(1, n_types + 1):
        type_orders = np.sum(order_type == u)
        type_demand = np.sum(demand_qty[demand_type == u])
        type_inv = initial_inventory[u - 1]
        type_capacity = type_orders + type_inv
        status = "[OK]" if type_capacity >= type_demand else "[ERROR]"
        print(f"    Type {u}: {type_capacity} capacity ({type_orders} orders + {type_inv} inv) = {type_demand} demand {status}")

    # Generate priorities
    print(f"\nGenerating priority weights...")
    priority = generate_priorities(
        n_orders, order_type, demand_type, due_date,
        config['priority_min'],
        config['priority_max'],
        config['random_seed']
    )
    print(f"  Priority range: {priority.min()}-{priority.max()}")
    print(f"  Average priority: {priority.mean():.1f}")

    print(f"\nObjective weights:")
    for key, value in config['objective_weights'].items():
        print(f"  {key}: {value}")

    # Compile data
    data = {
        'n_unique_types': n_types,
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

    # Demand fulfillment
    print(f"\n--- DEMAND FULFILLMENT ---")
    on_time_count = sum(1 for d in solution['demands'] if d['ship_time'] <= d['due_date'])
    print(f"Demands on-time: {on_time_count}/{data['n_demands']} ({on_time_count/data['n_demands']*100:.1f}%)")

    total_demand = sum(d['quantity'] for d in solution['demands'])
    print(f"Total demand quantity: {total_demand} units (all fulfilled by model)")

    late_demands = [d['demand'] for d in solution['demands'] if d['ship_time'] > d['due_date']]
    if late_demands:
        print(f"Late demands: {late_demands}")

    # Resource utilization
    print(f"\n--- RESOURCE UTILIZATION ---")

    # Line usage
    lines_used = len(set(a['line'] for a in solution['assignments']))
    print(f"Lines used: {lines_used}/{data['n_lines']} ({lines_used/data['n_lines']*100:.1f}%)")

    # Orders assigned
    orders_assigned = len(solution['assignments'])
    print(f"Orders assigned: {orders_assigned}/{data['n_orders']} ({orders_assigned/data['n_orders']*100:.1f}%)")

    if orders_assigned < data['n_orders']:
        unassigned = data['n_orders'] - orders_assigned
        print(f"  WARNING: {unassigned} orders not assigned to any line!")

    # Worker usage summary
    ws = solution['workforce_summary']
    print(f"\nWorkers used:")
    print(f"  Maximum: {ws['max']} workers")
    print(f"  Minimum: {ws['min']} workers")
    print(f"  Range: {ws['range']} workers")

    # Time metrics
    if solution['assignments']:
        completion_times = [a['completion'] for a in solution['assignments']]
        latest_completion = max(completion_times)
        earliest_start = min(a['start'] for a in solution['assignments'])

        print(f"\n--- TIMELINE ---")
        print(f"First order starts: {earliest_start:.1f}")
        print(f"Latest completion: {latest_completion:.1f}")
        print(f"Planning horizon: {data['T_max']:.1f} time units")
        print(f"Utilization: {latest_completion/data['T_max']*100:.1f}% of available time")

        # Makespan
        makespan = latest_completion - earliest_start
        print(f"Makespan: {makespan:.1f} time units")

    # Inventory analysis
    print(f"\n--- INVENTORY METRICS ---")
    if solution['inventory']:
        # Calculate average inventory across all types and demands
        total_inv = 0
        count = 0
        for type_inv in solution['inventory'].values():
            total_inv += sum(type_inv.values())
            count += len(type_inv)

        if count > 0:
            avg_inv = total_inv / count
            print(f"Average inventory per (type, demand): {avg_inv:.2f} units")

        print(f"Total inventory-demand sum: {total_inv:.0f}")
    else:
        print(f"No inventory tracking data available")

    # Type distribution
    print(f"\n--- PRODUCTION BY TYPE ---")
    for u in range(1, data['n_unique_types'] + 1):
        orders_of_type = sum(1 for a in solution['assignments'] if a['type'] == u)
        demand_of_type = sum(d['quantity'] for d in solution['demands'] if d['type'] == u)
        inv_of_type = data['initial_inventory'][u - 1]

        print(f"Type {u}:")
        print(f"  Orders produced: {orders_of_type}")
        print(f"  Initial inventory: {inv_of_type}")
        print(f"  Total supply: {orders_of_type + inv_of_type}")
        print(f"  Total demand: {demand_of_type}")

        balance = (orders_of_type + inv_of_type) - demand_of_type
        if balance >= 0:
            print(f"  Balance: +{balance} (surplus)")
        else:
            print(f"  Balance: {balance} (shortage)")

    print("\n" + "="*80)


def print_detailed_schedule(solution, config, max_items_to_show=10):
    """
    Print a detailed schedule of assignments and demands.

    Args:
        solution: Solution dictionary
        config: Configuration parameters
        max_items_to_show: Maximum number of items to display in detail
    """
    print("\n" + "="*80)
    print("DETAILED SCHEDULE")
    print("="*80)

    # Sort assignments by start time
    sorted_assignments = sorted(solution['assignments'], key=lambda x: (x['start'], x['line']))

    print(f"\nORDER SCHEDULE (showing first {min(len(sorted_assignments), max_items_to_show)} orders):")
    print(f"\n{'Order':<8} {'Line':<6} {'Type':<6} {'Start':<10} {'Complete':<10} {'Duration':<10}")
    print("-"*60)

    for assignment in sorted_assignments[:max_items_to_show]:
        print(f"{assignment['order']:<8} {assignment['line']:<6} "
              f"{assignment['type']:<6} {assignment['start']:<10.1f} "
              f"{assignment['completion']:<10.1f} {assignment['duration']:<10.1f}")

    if len(sorted_assignments) > max_items_to_show:
        print(f"\n... and {len(sorted_assignments) - max_items_to_show} more orders")

    # Sort demands by due date
    sorted_demands = sorted(solution['demands'], key=lambda x: x['due_date'])

    print(f"\n\nDEMAND SCHEDULE (showing first {min(len(sorted_demands), max_items_to_show)} demands):")
    print(f"\n{'Demand':<8} {'Type':<6} {'Qty':<6} {'Due':<10} {'Ship':<10} {'Lateness':<10} {'Status':<10}")
    print("-"*70)

    for demand in sorted_demands[:max_items_to_show]:
        lateness = demand['ship_time'] - demand['due_date']
        status = "ON-TIME" if demand['ship_time'] <= demand['due_date'] else "LATE"

        print(f"{demand['demand']:<8} {demand['type']:<6} "
              f"{demand['quantity']:<6} {demand['due_date']:<10.1f} "
              f"{demand['ship_time']:<10.1f} {lateness:<10.1f} {status:<10}")

    if len(sorted_demands) > max_items_to_show:
        print(f"\n... and {len(sorted_demands) - max_items_to_show} more demands")

    print("="*80)


def main():
    """
    Run the configurable scenario example for Problem_4_1_c2.
    """

    print("="*80)
    print("PROBLEM_4_1_C2 CONFIGURABLE SCENARIO EXAMPLE")
    print("Flexible Problem Size Configuration (Continuous Time Formulation)")
    print("="*80)

    print("\nCURRENT CONFIGURATION:")
    print(f"  Product types: {CONFIG['n_types']}")
    print(f"  Shipping demands: {CONFIG['n_demands']}")
    print(f"  Production lines: {CONFIG['n_lines']}")
    print(f"  Planning horizon: {CONFIG['planning_horizon']} time units")
    print(f"\n  NOTE: Number of production orders will be calculated automatically")
    print(f"        based on demand quantities to ensure feasibility.")

    # Estimate problem complexity (rough estimate, will be recalculated after data generation)
    # Assume average demand quantity for estimation
    estimated_n_orders = CONFIG['n_demands'] * ((CONFIG['demand_qty_min'] + CONFIG['demand_qty_max']) / 2)
    estimated_n_orders = int(estimated_n_orders)

    estimated_binary_vars = (
        estimated_n_orders * CONFIG['n_lines'] +  # x(i,j)
        estimated_n_orders * estimated_n_orders +  # y(i,k)
        estimated_n_orders * CONFIG['n_demands'] +  # prodorder(i,d)
        CONFIG['n_demands'] * CONFIG['n_demands']   # shipped(d1,d)
    )

    estimated_continuous_vars = (
        estimated_n_orders * 2 +  # start(i), complete(i)
        CONFIG['n_types'] * CONFIG['n_demands'] +  # inv(u,d), prodbefore(u,d)
        CONFIG['n_demands']  # ship(d)
    )

    estimated_total_vars = estimated_binary_vars + estimated_continuous_vars

    print(f"\n  Estimated variables:")
    print(f"    Binary: ~{estimated_binary_vars:,}")
    print(f"    Continuous: ~{estimated_continuous_vars:,}")
    print(f"    Total: ~{estimated_total_vars:,}")

    if estimated_total_vars > 10000:
        print(f"\n  WARNING: Large problem size! May require significant time and memory.")
    elif estimated_total_vars > 1000:
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
    print("\n[Step 2] Building Problem_4_1_c2 optimization model...")
    build_start = time.time()
    model = PackingScheduleModelProblem4_1_c2(data)
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

    try:
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
            print_detailed_schedule(model.get_solution(), CONFIG, max_items_to_show=10)

            # Key insights
            print("\n" + "="*80)
            print("KEY INSIGHTS")
            print("="*80)
            solution = model.get_solution()
            on_time = sum(1 for d in solution['demands'] if d['ship_time'] <= d['due_date'])

            print(f"\n  [CHECK] Achieved {on_time/data['n_demands']*100:.1f}% on-time delivery rate")
            print(f"  [CHECK] Optimized schedule across {CONFIG['n_lines']} lines with up to {solution['workforce_summary']['max']} workers")
            print(f"  [CHECK] Solved in {solve_time:.2f} seconds")
            print(f"  [CHECK] Workforce range: {solution['workforce_summary']['range']} (max-min workers)")

            if on_time == data['n_demands']:
                print(f"\n  [SUCCESS] Perfect! All demands delivered on time!")
            elif on_time / data['n_demands'] >= 0.9:
                print(f"\n  [EXCELLENT] Excellent performance with >90% on-time delivery!")
            elif on_time / data['n_demands'] >= 0.7:
                print(f"\n  [WARNING] Good performance, but some demands are late. Consider:")
                print(f"     - Increasing number of lines")
                print(f"     - Increasing number of orders to boost production")
                print(f"     - Extending planning horizon")
            else:
                print(f"\n  [WARNING] Many demands are late. Consider:")
                print(f"     - Significantly increasing production capacity")
                print(f"     - Extending planning horizon")
                print(f"     - Relaxing due date constraints")

        else:
            print("\n[ERROR] No solution found!")
            print("\nPossible reasons:")
            print("  - Time limit too short")
            print("  - Problem is infeasible (not enough capacity)")
            print("  - Due dates too tight")
            print("  - Demand quantities exceed production capacity")
            print("\nTry:")
            print("  - Increasing time_limit in CONFIG")
            print("  - Increasing n_orders to boost production")
            print("  - Increasing n_lines")
            print("  - Extending planning_horizon")
            print("  - Increasing initial_inventory_pct")

    except RuntimeError as e:
        print(f"\n[ERROR] Solver encountered an error: {str(e)}")
        print("\nThis might indicate an infeasible model.")
        print("Try adjusting problem parameters or relaxing constraints.")

    print("\n" + "="*80)
    print("EXAMPLE COMPLETED")
    print("="*80)

    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

    print("\nTO TRY DIFFERENT SCENARIOS:")
    print("  1. Edit the CONFIG dictionary at the top of this file")
    print("  2. Change n_types, n_lines, n_orders, n_demands, planning_horizon, etc.")
    print("  3. Run again to see how the model handles different scales!")

    print("\nEXPERIMENT SUGGESTIONS:")
    print("  - Try n_orders < total demand qty to see shortage handling")
    print("  - Try more types with fewer orders per type")
    print("  - Try tight planning_horizon to see time pressure effects")
    print("  - Try different setup times to see impact of type changeovers")
    print("  - Try increasing initial_inventory_pct to see inventory usage")


if __name__ == "__main__":
    import pyomo.environ as pyo
    main()
