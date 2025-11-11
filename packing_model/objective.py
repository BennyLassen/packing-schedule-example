"""
Objective Function Module

This module defines the objective function for the packing schedule optimization.
The objective is a weighted sum of multiple components that can be easily extended.
"""

import pyomo.environ as pyo


class ObjectiveManager:
    """
    Manages the objective function definition.

    This class encapsulates objective function components and makes it easy to:
    - Add new objective terms
    - Adjust weights
    - Organize objective components
    """

    def __init__(self, model, data):
        """
        Initialize objective manager.

        Args:
            model: Pyomo ConcreteModel instance
            data: Dictionary containing problem data
        """
        self.model = model
        self.data = data
        self.weights = data.get('objective_weights', {
            'alpha': 1.0,
            'beta': 0.5,
            'gamma': 0.3,
            'delta': 0.2,
            'omega': 0.1  # Worker movement penalty (Problem_3)
        })

    def define_objective(self):
        """
        Define the complete objective function.

        The objective is a weighted sum of:
        - OTIF (On-Time In-Full) term
        - WIP (Work-In-Progress) term
        - Workforce management term
        - Line utilization term
        - Worker movement penalty term (Problem_3)
        """

        def objective_rule(m):
            """
            Combined objective function.

            Minimizes a weighted sum of penalty terms.
            """
            # Base objective terms
            obj_expr = (
                self.weights['alpha'] * self._otif_term(m) +
                self.weights['beta'] * self._wip_term(m) +
                self.weights['gamma'] * self._workforce_term(m) +
                self.weights['delta'] * self._line_utilization_term(m)
            )

            # Add worker movement penalty if omega weight is specified (Problem_3)
            if 'omega' in self.weights and self.weights['omega'] > 0:
                obj_expr += self.weights['omega'] * self._worker_movement_term(m)

            return obj_expr

        self.model.objective = pyo.Objective(
            rule=objective_rule,
            sense=pyo.minimize,
            doc="Minimize weighted multi-objective function"
        )

    def _otif_term(self, m):
        """
        OTIF (On-Time In-Full) objective term.

        Penalizes late orders heavily, with additional penalty
        proportional to the amount of lateness.

        Formula: sum over orders of priority * (7 * late + 3 * lateness)

        Args:
            m: Model instance

        Returns:
            Pyomo expression for OTIF term
        """
        return sum(
            m.priority[i] * (7 * m.late[i] + 3 * m.lateness[i])
            for i in m.ORDERS
        )

    def _wip_term(self, m):
        """
        WIP (Work-In-Progress) objective term.

        Minimizes both the number of orders in progress and
        the total flow time.

        Formula: 4 * sum(wip) + 6 * sum(flow_time)

        Args:
            m: Model instance

        Returns:
            Pyomo expression for WIP term
        """
        wip_count = sum(m.wip[t] for t in m.TIME)
        total_flow_time = sum(m.time_flow[i] for i in m.ORDERS)
        return 4 * wip_count + 6 * total_flow_time

    def _workforce_term(self, m):
        """
        Workforce management objective term.

        Minimizes:
        - Range of workforce levels (max - min)
        - Deviations from target workforce
        - Changes in workforce between periods

        Formula: 5 * range + 3 * total_deviation + 2 * total_changes

        Args:
            m: Model instance

        Returns:
            Pyomo expression for workforce term
        """
        # Workforce range (difference between max and min)
        workforce_range = m.workers_max - m.workers_min

        # Total deviation from target
        total_deviation = sum(
            m.deviation_above[t] + m.deviation_below[t]
            for t in m.TIME
        )

        # Total workforce changes
        total_changes = sum(
            m.workforce_change[t]
            for t in m.TIME
            if t > 1
        )

        return 5 * workforce_range + 3 * total_deviation + 2 * total_changes

    def _line_utilization_term(self, m):
        """
        Line utilization objective term.

        Minimizes the number of lines used to concentrate
        production on fewer lines.

        Formula: sum(u[j])

        Args:
            m: Model instance

        Returns:
            Pyomo expression for line utilization term
        """
        return sum(m.u[j] for j in m.LINES)

    def _worker_movement_term(self, m):
        """
        Worker movement penalty term (Problem_3).

        Minimizes the total number of worker movements between lines.
        A movement occurs when a worker switches from one line to another
        between consecutive time periods.

        Formula: sum over workers and time of m(w,t)

        Args:
            m: Model instance

        Returns:
            Pyomo expression for worker movement term
        """
        return sum(
            m.m[w, t]
            for w in m.WORKERS
            for t in m.TIME
        )


def add_objective(model, data):
    """
    Convenience function to add objective to a model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data and weights
    """
    obj_manager = ObjectiveManager(model, data)
    obj_manager.define_objective()
