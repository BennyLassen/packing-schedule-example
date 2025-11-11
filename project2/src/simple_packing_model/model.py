"""
Main Model Class for Problem_4_1_c2 Formulation

Implements the complete MILP model from Problem_4_1_c2.pdf with:
- Event-based workforce tracking
- Continuous time formulation
- Setup times and demand fulfillment
"""

import pyomo.environ as pyo
from pyomo.opt import SolverFactory, TerminationCondition
import numpy as np

from .parameters import define_parameters
from .variables import define_variables
from .constraints import (
    define_assignment_constraints,
    define_capacity_constraints,
    define_shipping_constraints,
    define_wip_constraints,
    define_workforce_constraints,
    define_otif_constraints
)
from .objective import define_objective


class PackingScheduleModelProblem4_1_c2:
    """
    Packing Schedule Optimization Model (Problem_4_1_c2).

    This formulation implements the problem from Problem_4_1_c2.pdf with:
    - Continuous time variables (not discretized)
    - Event-based workforce tracking
    - Setup times between product types
    - Demand fulfillment with inventory tracking
    - Workforce variability minimization

    Key differences from other formulations:
    - Uses events E = {s1, ..., sn, c1, ..., cn} for workforce tracking
    - Tracks order completion relative to demand shipping
    - No time discretization
    """

    def __init__(self, data):
        """
        Initialize the Problem_4_1_c2 packing schedule model.

        Args:
            data: Dictionary containing problem data with keys:
                - n_unique_types: Number of unique packing types (U)
                - n_orders: Number of production orders (I)
                - n_demands: Number of demand/shipping requirements (D)
                - n_lines: Number of production lines (J)
                - processing_time: Array[n_unique_types, n_lines] - p(u,j)
                - setup_time: Array[n_unique_types, n_unique_types] - s(u,v)
                - initial_inventory: Array[n_unique_types] - inv0(u)
                - T_max: Planning horizon (positive real)
                - order_type: Array[n_orders] - type(i)
                - due_date: Array[n_demands] - due(d)
                - demand_type: Array[n_demands] - prodtype(d)
                - demand_qty: Array[n_demands] - qty(d)
                - priority: Array[n_orders] - priority(i)
                - objective_weights: Dict with beta, gamma, delta
        """
        self.data = data
        self.model = pyo.ConcreteModel(name="PackingSchedule_Problem4_1_c2")

        # Build the model
        self._build_model()

    def _build_model(self):
        """Build the complete optimization model."""
        # Define parameters and sets
        define_parameters(self.model, self.data)

        # Define decision variables
        define_variables(self.model)

        # Define constraints
        define_assignment_constraints(self.model)
        define_capacity_constraints(self.model)
        define_shipping_constraints(self.model)
        define_wip_constraints(self.model)
        define_workforce_constraints(self.model)
        define_otif_constraints(self.model)

        # Define objective function
        define_objective(self.model, self.data)

    def solve(self, solver_name='appsi_highs', tee=True, time_limit=None, mip_rel_gap=None, highs_options=None):
        """
        Solve the optimization model.

        Args:
            solver_name: Name of the solver ('appsi_highs', 'glpk', 'gurobi', etc.)
            tee: Whether to stream solver output
            time_limit: Time limit in seconds (None for no limit)
            mip_rel_gap: Relative MIP gap tolerance (None for default)
            highs_options: Dictionary of additional HiGHS-specific options

        Returns:
            Dictionary with results:
                - status: Termination condition
                - objective_value: Optimal objective value (or None)
                - solve_time: Solution time in seconds
        """
        # Create solver
        solver = pyo.SolverFactory(solver_name)

        # Set solver options
        if time_limit is not None:
            if solver_name == 'appsi_highs':
                solver.config.time_limit = time_limit
            elif solver_name in ['gurobi', 'cplex']:
                solver.options['timelimit'] = time_limit

        if mip_rel_gap is not None:
            if solver_name == 'appsi_highs':
                solver.config.mip_gap = mip_rel_gap
            elif solver_name == 'gurobi':
                solver.options['MIPGap'] = mip_rel_gap
            elif solver_name == 'cplex':
                solver.options['mipgap'] = mip_rel_gap

        # Apply HiGHS-specific performance options
        if solver_name == 'appsi_highs' and highs_options:
            for key, value in highs_options.items():
                solver.highs_options[key] = value

        # Solve the model
        if solver_name == 'appsi_highs':
            solver.config.load_solution = False  # Don't auto-load if infeasible
            results = solver.solve(self.model, tee=tee)
        else:
            results = solver.solve(self.model, tee=tee, load_solutions=False)

        # Extract results
        termination = results.solver.termination_condition

        # Load solution if optimal or feasible
        if solver_name == 'appsi_highs':
            if termination in [TerminationCondition.optimal, TerminationCondition.feasible]:
                solver.load_vars()
        else:
            if termination in [TerminationCondition.optimal, TerminationCondition.feasible]:
                self.model.solutions.load_from(results)

        result_dict = {
            'status': str(termination),
            'objective_value': pyo.value(self.model.objective) if termination in [
                TerminationCondition.optimal, TerminationCondition.feasible
            ] else None,
            'solve_time': results.solver.time if hasattr(results.solver, 'time') else None
        }

        return result_dict

    def get_solution(self):
        """
        Extract the solution from the solved model.

        Returns:
            Dictionary with solution details:
                - assignments: List of order assignments
                - demands: Demand fulfillment details
                - inventory: Inventory levels per type and demand
                - workforce: Workforce utilization at events
                - events: Event times (start and completion)
        """
        m = self.model

        # Extract order assignments
        assignments = []
        for i in m.ORDERS:
            for j in m.LINES:
                if pyo.value(m.x[i, j]) > 0.5:  # Binary variable is 1
                    assignments.append({
                        'order': i,
                        'line': j,
                        'type': int(m.order_type[i]),
                        'start': float(pyo.value(m.start[i])),
                        'completion': float(pyo.value(m.complete[i])),
                        'duration': float(pyo.value(m.complete[i]) - pyo.value(m.start[i]))
                    })

        # Extract demand fulfillment
        demands = []
        for d in m.DEMANDS:
            demands.append({
                'demand': d,
                'type': int(m.prodtype[d]),
                'quantity': int(m.qty[d]),
                'due_date': float(m.due[d]),
                'ship_time': float(pyo.value(m.ship[d]))
            })

        # Extract inventory levels
        inventory = {}
        for u in m.TYPES:
            inventory[u] = {
                d: int(pyo.value(m.inv[u, d]))
                for d in m.DEMANDS
            }

        # Extract workforce utilization at events
        workforce_events = {
            e: float(pyo.value(m.workersused[e]))
            for e in m.EVENTS
        }

        workforce_summary = {
            'max': float(pyo.value(m.workersmax)),
            'min': float(pyo.value(m.workersmin)),
            'range': float(pyo.value(m.workforcerange))
        }

        # Extract event times
        event_times = {
            e: float(pyo.value(m.t_event[e]))
            for e in m.EVENTS
        }

        # Extract shipped variable (d1, d) - which demands shipped before/with each demand
        shipped = {}
        for d in m.DEMANDS:
            shipped[d] = []
            for d1 in m.DEMANDS:
                if pyo.value(m.shipped[d1, d]) > 0.5:  # Binary variable is 1
                    shipped[d].append(d1)

        # Extract OTIF variables
        otif_data = {}
        for d in m.DEMANDS:
            otif_data[d] = {
                'lateness': float(pyo.value(m.lateness[d])),
                'late': int(pyo.value(m.late[d]))
            }

        # Extract line utilization
        line_utilization = {}
        for j in m.LINES:
            line_utilization[j] = int(pyo.value(m.u[j]))

        return {
            'assignments': assignments,
            'demands': demands,
            'inventory': inventory,
            'workforce_events': workforce_events,
            'workforce_summary': workforce_summary,
            'event_times': event_times,
            'shipped': shipped,
            'otif': otif_data,
            'line_utilization': line_utilization
        }

    def print_solution_summary(self):
        """Print a formatted summary of the solution."""
        if pyo.value(self.model.objective) is None:
            print("No solution available.")
            return

        solution = self.get_solution()

        print("\n" + "="*80)
        print("SOLUTION SUMMARY (Problem_4_1_c2 Model)")
        print("="*80)

        # Objective value
        print(f"\nObjective Value: {pyo.value(self.model.objective):.2f}")

        # Workforce Summary
        ws = solution['workforce_summary']
        print(f"\nWorkforce Utilization:")
        print(f"  Max workers: {ws['max']:.1f}")
        print(f"  Min workers: {ws['min']:.1f}")
        print(f"  Range: {ws['range']:.1f}")

        # Order Assignments
        print(f"\n{'Order':<8} {'Line':<6} {'Type':<6} {'Start':<10} {'Complete':<10} {'Duration':<10}")
        print("-"*80)

        for assignment in sorted(solution['assignments'], key=lambda x: x['start']):
            print(f"{assignment['order']:<8} {assignment['line']:<6} "
                  f"{assignment['type']:<6} {assignment['start']:<10.2f} "
                  f"{assignment['completion']:<10.2f} {assignment['duration']:<10.2f}")

        # Demand Fulfillment
        print(f"\n{'Demand':<8} {'Type':<6} {'Qty':<6} {'Due':<10} {'Ship':<10} {'Status':<10}")
        print("-"*80)

        for demand in solution['demands']:
            status = "ON-TIME" if demand['ship_time'] <= demand['due_date'] else "LATE"
            print(f"{demand['demand']:<8} {demand['type']:<6} "
                  f"{demand['quantity']:<6} {demand['due_date']:<10.2f} "
                  f"{demand['ship_time']:<10.2f} {status:<10}")

        # Inventory Summary
        print(f"\nFinal Inventory by Type:")
        for u in solution['inventory']:
            final_inv = solution['inventory'][u][max(solution['inventory'][u].keys())]
            print(f"  Type {u}: {final_inv} units")

        # OTIF Summary
        print(f"\nOTIF (On-Time In-Full) Summary:")
        on_time_count = sum(1 for d, data in solution['otif'].items() if data['late'] == 0)
        late_count = sum(1 for d, data in solution['otif'].items() if data['late'] == 1)
        total_lateness = sum(data['lateness'] for data in solution['otif'].values())
        print(f"  On-time demands: {on_time_count}/{len(solution['otif'])} ({on_time_count/len(solution['otif'])*100:.1f}%)")
        print(f"  Late demands: {late_count}/{len(solution['otif'])}")
        print(f"  Total lateness: {total_lateness:.2f} time units")

        print("="*80)

    def print_shipped_matrix(self):
        """Print the shipped(d1,d) matrix showing which demands shipped before others."""
        if pyo.value(self.model.objective) is None:
            print("No solution available.")
            return

        solution = self.get_solution()
        m = self.model

        print("\n" + "="*80)
        print("SHIPPED MATRIX: shipped(d1, d) = 1 means d1 shipped before or with d")
        print("="*80)

        # Get all demands sorted by ship time
        demands_sorted = sorted(solution['demands'], key=lambda x: x['ship_time'])

        print(f"\nDemand Ship Times:")
        for demand in demands_sorted:
            lateness = solution['otif'][demand['demand']]['lateness']
            late_status = "LATE" if solution['otif'][demand['demand']]['late'] == 1 else "ON-TIME"
            print(f"  Demand {demand['demand']}: ship={demand['ship_time']:.2f}, due={demand['due_date']:.2f}, "
                  f"lateness={lateness:.2f}, status={late_status}")

        # Print the matrix
        print(f"\nShipped Matrix (rows: d1, columns: d):")
        print(f"  1 = d1 shipped before or at same time as d")
        print(f"  0 = d1 shipped after d\n")

        # Header
        header = "     d> |"
        for d in m.DEMANDS:
            header += f" {d:>4} |"
        print(header)
        print("  " + "-" * len(header))

        # Rows
        for d1 in m.DEMANDS:
            row = f"  d1={d1:>2} |"
            for d in m.DEMANDS:
                val = int(pyo.value(m.shipped[d1, d]))
                row += f"  {val}   |"
            print(row)

        # Show which demands shipped with each demand
        print(f"\nDemands Shipped Before/With Each Demand:")
        for d in m.DEMANDS:
            shipped_with = solution['shipped'][d]
            ship_time = next(dem['ship_time'] for dem in solution['demands'] if dem['demand'] == d)
            print(f"  Demand {d} (ship={ship_time:.2f}): {sorted(shipped_with)}")

        print("="*80)

    def print_inventory_matrix(self):
        """Print the inventory inv(u,d) matrix showing inventory levels after each demand ships."""
        if pyo.value(self.model.objective) is None:
            print("No solution available.")
            return

        solution = self.get_solution()
        m = self.model

        print("\n" + "="*80)
        print("INVENTORY MATRIX: inv(u, d) = inventory of type u after demand d ships")
        print("="*80)

        # Get all demands sorted by ship time
        demands_sorted = sorted(solution['demands'], key=lambda x: x['ship_time'])

        print(f"\nDemand Ship Times:")
        for demand in demands_sorted:
            print(f"  Demand {demand['demand']}: type={demand['type']}, qty={demand['quantity']}, "
                  f"due={demand['due_date']:.2f}, ship={demand['ship_time']:.2f}")

        # Print the inventory matrix for each type
        for u in m.TYPES:
            print(f"\n--- Type {u} Inventory ---")
            print(f"  Initial inventory: {int(m.inv0[u])} units")

            # Header
            header = "  Demand d> |"
            for d in m.DEMANDS:
                header += f" {d:>6} |"
            print(header)
            print("  " + "-" * len(header))

            # Inventory row
            row = f"  inv({u},d) |"
            for d in m.DEMANDS:
                val = int(pyo.value(m.inv[u, d]))
                row += f" {val:>6} |"
            print(row)

            # Production before row
            row = f"  prod(u,d) |"
            for d in m.DEMANDS:
                val = int(pyo.value(m.prodbefore[u, d]))
                row += f" {val:>6} |"
            print(row)

        # Show inventory trajectory for each type
        print(f"\nInventory Trajectory (by ship time):")
        for u in m.TYPES:
            print(f"\n  Type {u}:")
            print(f"    Initial: {int(m.inv0[u])} units")

            for demand in demands_sorted:
                d = demand['demand']
                inv_level = int(pyo.value(m.inv[u, d]))
                prod_before = int(pyo.value(m.prodbefore[u, d]))

                # Calculate what was shipped of this type by time d
                shipped_of_type = 0
                for d1 in m.DEMANDS:
                    if m.prodtype[d1] == u and pyo.value(m.shipped[d1, d]) > 0.5:
                        shipped_of_type += int(m.qty[d1])

                print(f"    After demand {d} ships (t={demand['ship_time']:.2f}): "
                      f"inv={inv_level}, produced_before={prod_before}, shipped_so_far={shipped_of_type}")

        print("="*80)

    def print_assignment_matrix(self):
        """Print the assignment x(i,j) matrix showing which orders are assigned to which lines."""
        if pyo.value(self.model.objective) is None:
            print("No solution available.")
            return

        solution = self.get_solution()
        m = self.model

        print("\n" + "="*80)
        print("ASSIGNMENT MATRIX: x(i, j) = 1 means order i assigned to line j")
        print("="*80)

        # Get order information
        print(f"\nOrder Information:")
        for i in m.ORDERS:
            order_type = int(m.order_type[i])
            # Find which line this order is assigned to
            assigned_line = None
            for j in m.LINES:
                if pyo.value(m.x[i, j]) > 0.5:
                    assigned_line = j
                    break

            if assigned_line is not None:
                start_time = pyo.value(m.start[i])
                complete_time = pyo.value(m.complete[i])
                print(f"  Order {i}: type={order_type}, line={assigned_line}, "
                      f"start={start_time:.2f}, complete={complete_time:.2f}")
            else:
                print(f"  Order {i}: type={order_type}, NOT ASSIGNED")

        # Print the assignment matrix
        print(f"\nAssignment Matrix (rows: orders, columns: lines):")
        print(f"  1 = order assigned to line")
        print(f"  0 = order not assigned to line\n")

        # Header
        header = "  Order i> |"
        for j in m.LINES:
            header += f" L{j:>3} |"
        print(header)
        print("  " + "-" * len(header))

        # Rows
        for i in m.ORDERS:
            row = f"  Order {i:>2} |"
            for j in m.LINES:
                val = int(pyo.value(m.x[i, j]))
                row += f"  {val}   |"
            print(row)

        # Show line utilization
        print(f"\nLine Utilization (u(j) variable):")
        for j in m.LINES:
            u_val = int(pyo.value(m.u[j]))
            status = "IN USE" if u_val == 1 else "NOT IN USE"
            assigned_orders = []
            for i in m.ORDERS:
                if pyo.value(m.x[i, j]) > 0.5:
                    assigned_orders.append(i)

            if assigned_orders:
                print(f"  Line {j}: u({j})={u_val} ({status}) - {len(assigned_orders)} orders assigned -> {assigned_orders}")
            else:
                print(f"  Line {j}: u({j})={u_val} ({status}) - No orders assigned")

        # Show by type
        print(f"\nAssignments by Type:")
        for u in m.TYPES:
            print(f"  Type {u}:")
            for j in m.LINES:
                type_orders = []
                for i in m.ORDERS:
                    if m.order_type[i] == u and pyo.value(m.x[i, j]) > 0.5:
                        type_orders.append(i)
                if type_orders:
                    print(f"    Line {j}: {len(type_orders)} orders -> {type_orders}")

        print("="*80)
