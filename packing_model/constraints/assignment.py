"""
Assignment Constraints

This module defines constraints related to order assignment to lines,
times, and workers.
"""

import pyomo.environ as pyo


def add_assignment_constraints(model, data):
    """
    Add assignment-related constraints to the model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: Each order assigned to exactly one line, one time, and one worker
    def one_assignment_rule(m, i):
        """
        Each order must be assigned exactly once.

        For each order i, sum over all possible line-time-worker combinations
        must equal 1, ensuring each order is scheduled exactly once.
        """
        return sum(
            m.x[i, j, t, w]
            for j in m.LINES
            for t in m.TIME
            for w in m.WORKERS
        ) == 1

    model.one_assignment = pyo.Constraint(
        model.ORDERS,
        rule=one_assignment_rule,
        doc="Each order assigned exactly once"
    )
