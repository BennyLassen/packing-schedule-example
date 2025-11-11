"""
Main Model Class for Problem_4 Simplified Formulation

Simplified packing schedule optimization without explicit worker assignment.
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


class PackingScheduleModelSimple:
    """
    Simplified Packing Schedule Optimization Model (Problem_4).

    Key simplifications from Problem_3:
    - No explicit worker assignment (x(i,j,t) instead of x(i,j,t,w))
    - Workers counted by simultaneous orders
    - Batch indicators and setup sequencing
    - 4-term objective (no worker movement penalty)
    - Simplified workforce tracking (range-based)

    This formulation is suitable when:
    - Worker identity doesn't matter, only count
    - Explicit worker assignment not required
    - Simpler model structure desired
    - Focus on line scheduling over worker assignment
    """

    def __init__(self, data):
        """
        Initialize the simplified packing schedule model.

        Args:
            data: Dictionary containing problem data with keys:
                - n_orders: Number of packing orders
                - n_lines: Number of production lines
                - n_timeslots: Number of time slots
                - n_workers: Number of workers (for counting only)
                - processing_time: Array[n_orders, n_lines]
                - setup_time: Array[n_orders, n_orders, n_lines]
                - initial_inventory: Array[n_orders]
                - reserved_capacity: Float (fraction)
                - due_date: Array[n_orders]
                - priority: Array[n_orders]
                - objective_weights: Dict with alpha, beta, gamma, delta
        """
        self.data = data
        self.model = pyo.ConcreteModel(name="PackingScheduleSimple_Problem4")

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
                solver.config.mip_gap = mip_rel_gap  # Note: mip_gap not mipgap
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
                - otif_metrics: OTIF performance per order
                - inventory: Inventory levels over time
                - workforce: Workforce utilization over time
                - line_usage: Which lines are used
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
                            'completion': int(pyo.value(m.timecompletion[i])),
                            'ship': int(pyo.value(m.timeship[i])),
                            'processing_time': int(m.p[i, j])
                        })

        # Extract OTIF metrics
        otif_metrics = {}
        for i in m.ORDERS:
            otif_metrics[i] = {
                'due_date': int(m.due[i]),
                'completion_time': int(pyo.value(m.timecompletion[i])),
                'ship_time': int(pyo.value(m.timeship[i])),
                'late': bool(pyo.value(m.late[i]) > 0.5),
                'lateness': int(pyo.value(m.lateness[i])),
                'priority': int(m.priority[i])
            }

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

        # Extract line usage
        line_usage = {
            j: bool(pyo.value(m.u[j]) > 0.5)
            for j in m.LINES
        }

        return {
            'assignments': assignments,
            'otif_metrics': otif_metrics,
            'inventory': inventory,
            'workforce': workforce,
            'workforce_summary': workforce_summary,
            'line_usage': line_usage
        }

    def print_solution_summary(self):
        """Print a formatted summary of the solution."""
        if pyo.value(self.model.objective) is None:
            print("No solution available.")
            return

        solution = self.get_solution()

        print("\n" + "="*80)
        print("SOLUTION SUMMARY (Problem_4 Simplified Model)")
        print("="*80)

        # Objective value
        print(f"\nObjective Value: {pyo.value(self.model.objective):.2f}")

        # OTIF Performance
        on_time_orders = sum(1 for _, m in solution['otif_metrics'].items() if not m['late'])
        total_orders = len(solution['otif_metrics'])
        print(f"\nOTIF Performance: {on_time_orders}/{total_orders} orders on-time ({on_time_orders/total_orders*100:.1f}%)")

        # Workforce Summary
        ws = solution['workforce_summary']
        print(f"\nWorkforce Utilization:")
        print(f"  Max workers: {ws['max']}")
        print(f"  Min workers: {ws['min']}")
        print(f"  Range: {ws['range']}")

        # Line Usage
        active_lines = sum(1 for used in solution['line_usage'].values() if used)
        print(f"\nLine Usage: {active_lines}/{self.data['n_lines']} lines activated")

        # Order Details
        print(f"\n{'Order':<8} {'Line':<6} {'Start':<8} {'Complete':<10} {'Ship':<6} {'Due':<6} {'Status':<10}")
        print("-"*80)

        for assignment in sorted(solution['assignments'], key=lambda x: x['start']):
            order_id = assignment['order']
            metrics = solution['otif_metrics'][order_id]
            status = "LATE" if metrics['late'] else "ON-TIME"

            print(f"{order_id:<8} {assignment['line']:<6} "
                  f"{assignment['start']:<8} {assignment['completion']:<10} "
                  f"{assignment['ship']:<6} {metrics['due_date']:<6} {status:<10}")

        print("="*80)
