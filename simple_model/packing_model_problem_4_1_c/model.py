"""
Main Model Class for Problem_4_1_c Formulation (Relaxed/Continuous Version)

LP-relaxed packing schedule optimization based on Problem_4_1_c.pdf.
Integer variables (prod, inv, workers) are relaxed to continuous (real) variables.
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
    define_otif_constraints,
    define_wip_constraints,
    define_workforce_constraints
)
from .objective import define_objective


class PackingScheduleModelProblem41c:
    """
    Problem_4_1_c Packing Schedule Optimization Model (LP RELAXATION).

    Based on Problem_4_1_c.pdf formulation with LP relaxation:
    - Assignment variables x(i,j,t) (binary - unchanged)
    - Production tracking prod(i,t) (RELAXED TO REAL)
    - Workforce tracking workersused, workersmax, workersmin (RELAXED TO REAL)
    - WIP tracking inventory (RELAXED TO REAL) and shipping (binary)
    - 3-term objective (WIP, workforce, total_not_utilized)
    - Updated shipping constraint formulation

    KEY DIFFERENCES FROM Problem_4_1:
    1. Integer variables relaxed to continuous (real) variables
    2. New shipping constraint: ∑_t t * ship(i,t) ≥ due(i)
    3. Results in LP problem instead of MILP (faster to solve)
    """

    def __init__(self, data):
        """
        Initialize the Problem_4_1_c packing schedule model (relaxed version).

        Args:
            data: Dictionary containing problem data with keys:
                - n_orders: Number of packing orders
                - n_lines: Number of production lines
                - n_timeslots: Number of time slots
                - n_workers: Number of workers (for counting only)
                - processing_time: Array[n_orders, n_lines]
                - initial_inventory: Array[n_orders]
                - reserved_capacity: Float (fraction)
                - due_date: Array[n_orders]
                - priority: Array[n_orders]
                - objective_weights: Dict with beta, gamma, delta
        """
        self.data = data
        self.model = pyo.ConcreteModel(name="PackingScheduleProblem_4_1_c_Relaxed")

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
        define_otif_constraints(self.model)
        define_wip_constraints(self.model)
        define_workforce_constraints(self.model)

        # Define objective function
        define_objective(self.model, self.data)

    def solve(self, solver_name='appsi_highs', tee=True, time_limit=None, mip_rel_gap=None):
        """
        Solve the optimization model.

        Args:
            solver_name: Name of the solver ('appsi_highs', 'glpk', 'gurobi', etc.)
            tee: Whether to stream solver output
            time_limit: Time limit in seconds (None for no limit)
            mip_rel_gap: Relative MIP gap tolerance (None for default)

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
                - inventory: Inventory levels over time
                - workforce: Workforce utilization over time
                - shipping: Shipping times for orders
        """
        m = self.model

        # Extract order assignments
        assignments = []
        for i in m.ORDERS:
            for j in m.LINES:
                for t in m.TIME:
                    if pyo.value(m.x[i, j, t]) > 0.5:  # Binary variable is 1
                        assignments.append({
                            'order': i,
                            'line': j,
                            'start': t,
                            'processing_time': int(m.p[i, j]),
                            'completion': int(t + m.p[i, j])
                        })

        # Extract inventory levels
        inventory = {}
        for i in m.ORDERS:
            inventory[i] = {
                t: int(pyo.value(m.inv[i, t]))
                for t in m.TIME_WITH_ZERO
            }

        # Extract workforce utilization
        workforce = {
            t: int(pyo.value(m.workersused[t]))
            for t in m.TIME
        }

        workforce_summary = {
            'max': int(pyo.value(m.workersmax)),
            'min': int(pyo.value(m.workersmin)),
            'range': int(pyo.value(m.workforcerange))
        }

        # Extract shipping times
        shipping = {}
        for i in m.ORDERS:
            for t in m.TIME:
                if pyo.value(m.ship[i, t]) > 0.5:
                    shipping[i] = {
                        'ship_time': t,
                        'due_date': int(m.due[i]),
                        'on_time': t <= m.due[i]
                    }

        return {
            'assignments': assignments,
            'inventory': inventory,
            'workforce': workforce,
            'workforce_summary': workforce_summary,
            'shipping': shipping
        }

    def print_solution_summary(self):
        """Print a formatted summary of the solution."""
        if pyo.value(self.model.objective) is None:
            print("No solution available.")
            return

        solution = self.get_solution()

        print("\n" + "="*80)
        print("SOLUTION SUMMARY (Problem_4_1_c Model - LP Relaxation)")
        print("="*80)

        # Objective value
        print(f"\nObjective Value: {pyo.value(self.model.objective):.2f}")

        # Workforce Summary
        ws = solution['workforce_summary']
        print(f"\nWorkforce Utilization:")
        print(f"  Max workers: {ws['max']}")
        print(f"  Min workers: {ws['min']}")
        print(f"  Range: {ws['range']}")

        # Shipping Summary
        on_time = sum(1 for ship_info in solution['shipping'].values() if ship_info['on_time'])
        total = len(solution['shipping'])
        print(f"\nShipping Performance: {on_time}/{total} orders on-time ({on_time/total*100:.1f}%)")

        # Order Details
        print(f"\n{'Order':<8} {'Line':<6} {'Start':<8} {'Complete':<10} {'Ship':<6} {'Due':<6} {'Status':<10}")
        print("-"*80)

        for assignment in sorted(solution['assignments'], key=lambda x: x['start']):
            order_id = assignment['order']
            ship_info = solution['shipping'][order_id]
            status = "ON-TIME" if ship_info['on_time'] else "LATE"

            print(f"{order_id:<8} {assignment['line']:<6} "
                  f"{assignment['start']:<8} {assignment['completion']:<10} "
                  f"{ship_info['ship_time']:<6} {ship_info['due_date']:<6} {status:<10}")

        print("="*80)
