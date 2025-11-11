"""
Main Model Module

This module provides the main PackingScheduleModel class that coordinates
all components of the optimization model.
"""

import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import numpy as np

from .parameters import add_parameters
from .variables import add_variables
from .constraints import add_all_constraints
from .objective import add_objective


class PackingScheduleModel:
    """
    Main class for the packing schedule optimization problem.

    This class coordinates all model components:
    - Sets (indices)
    - Parameters (input data)
    - Variables (decision variables)
    - Constraints (feasibility conditions)
    - Objective (optimization goal)

    The modular design makes it easy to extend each component independently.
    """

    def __init__(self, data):
        """
        Initialize the model with input data.

        Args:
            data (dict): Dictionary containing all input parameters
                Required keys:
                - n_orders: Number of packing orders
                - n_lines: Number of production lines
                - n_timeslots: Number of time slots
                - n_workers: Number of workers
                - processing_time: Processing time matrix [i, j]
                - setup_time: Setup time tensor [i, k, j]
                - worker_availability: Worker availability matrix [w, t]
                - initial_inventory: Initial inventory vector [i]
                - shipping_schedule: Shipping schedule matrix [i, t]
                - reserved_capacity: Reserved capacity fraction (alpha)
                - due_date: Due date vector [i]
                - demand: Demand vector [i]
                - priority: Priority weight vector [i]
                - workforce_target: Target workforce level
                - objective_weights: Dict with keys alpha, beta, gamma, delta
        """
        self.data = data
        self.model = pyo.ConcreteModel(name="Packing_Schedule_Optimization")

        # Build model components in order
        self._define_sets()
        add_parameters(self.model, data)
        add_variables(self.model, data)
        add_all_constraints(self.model, data)
        add_objective(self.model, data)

    def _define_sets(self):
        """
        Define all index sets for the model.

        Sets define the indices used throughout the model.
        """
        model = self.model

        # Primary index sets
        model.ORDERS = pyo.RangeSet(1, self.data['n_orders'])
        model.LINES = pyo.RangeSet(1, self.data['n_lines'])
        model.TIME = pyo.RangeSet(1, self.data['n_timeslots'])
        model.WORKERS = pyo.RangeSet(1, self.data['n_workers'])

    def solve(self, solver_name='appsi_highs', tee=True, **solver_options):
        """
        Solve the optimization model.

        Args:
            solver_name (str): Name of the solver to use
                Options: 'appsi_highs', 'highs', 'gurobi', 'cplex', 'glpk'
            tee (bool): If True, display solver output
            **solver_options: Additional options to pass to the solver
                Examples:
                - time_limit: Time limit in seconds
                - mip_rel_gap: Relative MIP gap tolerance
                - threads: Number of threads to use

        Returns:
            dict: Solution results including:
                - status: Solver status
                - termination_condition: Termination condition
                - objective_value: Objective function value (if optimal)
                - solve_time: Time taken to solve
        """
        # Create solver instance
        solver = SolverFactory(solver_name)

        # Set solver options
        for key, value in solver_options.items():
            solver.options[key] = value

        # Solve the model
        print("Starting optimization...")
        results = solver.solve(self.model, tee=tee)

        # Package results
        solution_info = {
            'status': results.solver.status,
            'termination_condition': results.solver.termination_condition,
            'objective_value': None,
            'solve_time': results.solver.time if hasattr(results.solver, 'time') else None
        }

        # Extract objective value if optimal
        if results.solver.termination_condition == pyo.TerminationCondition.optimal:
            solution_info['objective_value'] = pyo.value(self.model.objective)
            print(f"\nOptimal solution found!")
            print(f"Objective value: {solution_info['objective_value']:.2f}")
        else:
            print(f"\nSolver terminated with condition: {results.solver.termination_condition}")

        return solution_info

    def get_solution(self):
        """
        Extract solution values from the solved model.

        Returns:
            dict: Dictionary containing solution values organized by category:
                - assignments: List of order assignments
                - otif_metrics: OTIF performance by order
                - workforce_metrics: Workforce usage over time
                - wip_metrics: WIP levels over time
                - line_usage: Line utilization status
        """
        model = self.model

        solution = {
            'assignments': [],
            'otif_metrics': {},
            'workforce_metrics': {},
            'wip_metrics': {},
            'line_usage': []
        }

        # Extract assignment decisions
        for i in model.ORDERS:
            for j in model.LINES:
                for t in model.TIME:
                    for w in model.WORKERS:
                        if pyo.value(model.x[i, j, t, w]) > 0.5:
                            solution['assignments'].append({
                                'order': i,
                                'line': j,
                                'time': t,
                                'worker': w,
                                'start': pyo.value(model.time_start[i]),
                                'completion': pyo.value(model.time_completion[i])
                            })

        # Extract OTIF metrics
        for i in model.ORDERS:
            solution['otif_metrics'][i] = {
                'late': pyo.value(model.late[i]) > 0.5,
                'lateness': pyo.value(model.lateness[i]),
                'early': pyo.value(model.early[i]),
                'due_date': pyo.value(model.due[i])
            }

        # Extract workforce metrics
        for t in model.TIME:
            solution['workforce_metrics'][t] = {
                'workers_used': pyo.value(model.workers_used[t]),
                'deviation_above': pyo.value(model.deviation_above[t]),
                'deviation_below': pyo.value(model.deviation_below[t])
            }

        # Extract WIP metrics
        for t in model.TIME:
            solution['wip_metrics'][t] = {
                'wip_count': pyo.value(model.wip[t])
            }

        # Extract line usage
        for j in model.LINES:
            solution['line_usage'].append({
                'line': j,
                'used': pyo.value(model.u[j]) > 0.5
            })

        return solution

    def print_solution_summary(self):
        """
        Print a formatted summary of the solution.

        This provides a quick overview of the key solution metrics.
        """
        solution = self.get_solution()

        print("\n" + "="*80)
        print("SOLUTION SUMMARY")
        print("="*80)

        # Order assignments
        print("\n--- ORDER ASSIGNMENTS ---")
        for assignment in solution['assignments']:
            print(f"Order {assignment['order']:2d} -> Line {assignment['line']:2d} | "
                  f"Start: t={assignment['start']:3.0f} | "
                  f"Complete: t={assignment['completion']:3.0f} | "
                  f"Worker: {assignment['worker']:2d}")

        # OTIF performance
        print("\n--- OTIF PERFORMANCE ---")
        late_orders = sum(1 for metrics in solution['otif_metrics'].values() if metrics['late'])
        total_orders = len(solution['otif_metrics'])
        otif_rate = (1 - late_orders / total_orders) * 100 if total_orders > 0 else 0
        print(f"On-Time Rate: {otif_rate:.1f}% ({total_orders - late_orders}/{total_orders} orders)")
        print(f"Late Orders: {late_orders}")

        # Workforce utilization
        print("\n--- WORKFORCE UTILIZATION ---")
        workers_per_time = [m['workers_used'] for m in solution['workforce_metrics'].values()]
        print(f"Average Workers: {np.mean(workers_per_time):.1f}")
        print(f"Peak Workers: {np.max(workers_per_time):.0f}")
        print(f"Min Workers: {np.min(workers_per_time):.0f}")

        # Line utilization
        print("\n--- LINE UTILIZATION ---")
        for line_info in solution['line_usage']:
            status = "USED" if line_info['used'] else "UNUSED"
            print(f"Line {line_info['line']:2d}: {status}")

        print("\n" + "="*80)

    def export_solution(self, filename='solution.txt'):
        """
        Export detailed solution to a text file.

        Args:
            filename (str): Output filename
        """
        solution = self.get_solution()

        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PACKING SCHEDULE OPTIMIZATION - DETAILED SOLUTION\n")
            f.write("="*80 + "\n\n")

            # Assignments
            f.write("ORDER ASSIGNMENTS\n")
            f.write("-" * 80 + "\n")
            for assignment in solution['assignments']:
                f.write(f"Order {assignment['order']:2d} -> Line {assignment['line']:2d} | "
                       f"Start: t={assignment['start']:3.0f} | "
                       f"Complete: t={assignment['completion']:3.0f} | "
                       f"Worker: {assignment['worker']:2d}\n")

            # OTIF details
            f.write("\n\nOTIF METRICS\n")
            f.write("-" * 80 + "\n")
            for order_id, metrics in solution['otif_metrics'].items():
                status = "LATE" if metrics['late'] else "ON-TIME"
                f.write(f"Order {order_id:2d}: {status:8s} | "
                       f"Due: t={metrics['due_date']:3.0f} | "
                       f"Lateness: {metrics['lateness']:3.0f} | "
                       f"Earliness: {metrics['early']:3.0f}\n")

            # Workforce timeline
            f.write("\n\nWORKFORCE TIMELINE\n")
            f.write("-" * 80 + "\n")
            for time, metrics in solution['workforce_metrics'].items():
                f.write(f"t={time:2d}: {metrics['workers_used']:2.0f} workers | "
                       f"Above target: {metrics['deviation_above']:2.0f} | "
                       f"Below target: {metrics['deviation_below']:2.0f}\n")

        print(f"\nSolution exported to {filename}")
