"""
OTIF (On-Time In-Full) Constraints

This module defines constraints for tracking order delivery performance,
including start times, completion times, lateness, and earliness.
"""

import pyomo.environ as pyo


def add_otif_constraints(model, data):
    """
    Add OTIF-related constraints to the model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: Calculate start time for each order
    def start_time_rule(m, i):
        """
        Calculate the start time for each order.

        The start time is determined by when the order is assigned.
        Sum over all assignments weighted by time.
        """
        return m.time_start[i] == sum(
            t * m.x[i, j, t, w]
            for j in m.LINES
            for w in m.WORKERS
            for t in m.TIME
        )

    model.start_time = pyo.Constraint(
        model.ORDERS,
        rule=start_time_rule,
        doc="Calculate start time for each order"
    )

    # Constraint: Calculate completion time for each order
    def completion_time_rule(m, i):
        """
        Calculate the completion time for each order.

        Completion time = start time + processing time.
        """
        return m.time_completion[i] == sum(
            (t + m.p[i, j]) * m.x[i, j, t, w]
            for j in m.LINES
            for w in m.WORKERS
            for t in m.TIME
        )

    model.completion_time = pyo.Constraint(
        model.ORDERS,
        rule=completion_time_rule,
        doc="Calculate completion time for each order"
    )

    # Constraint: Lateness lower bound
    def lateness_lower_rule(m, i):
        """
        Calculate lateness as max(0, completion_time - due_date).

        This constraint provides the lower bound for lateness.
        """
        return m.lateness[i] >= m.time_completion[i] - m.due[i]

    model.lateness_lower = pyo.Constraint(
        model.ORDERS,
        rule=lateness_lower_rule,
        doc="Lateness lower bound"
    )

    # Constraint: Lateness non-negativity
    def lateness_nonneg_rule(m, i):
        """
        Lateness must be non-negative.

        If order is early, lateness = 0.
        """
        return m.lateness[i] >= 0

    model.lateness_nonneg = pyo.Constraint(
        model.ORDERS,
        rule=lateness_nonneg_rule,
        doc="Lateness non-negative"
    )

    # Constraint: Earliness lower bound
    def early_lower_rule(m, i):
        """
        Calculate earliness as max(0, due_date - completion_time).

        This constraint provides the lower bound for earliness.
        """
        return m.early[i] >= m.due[i] - m.time_completion[i]

    model.early_lower = pyo.Constraint(
        model.ORDERS,
        rule=early_lower_rule,
        doc="Earliness lower bound"
    )

    # Constraint: Earliness non-negativity
    def early_nonneg_rule(m, i):
        """
        Earliness must be non-negative.

        If order is late, earliness = 0.
        """
        return m.early[i] >= 0

    model.early_nonneg = pyo.Constraint(
        model.ORDERS,
        rule=early_nonneg_rule,
        doc="Earliness non-negative"
    )

    # Constraint: Late indicator upper bound
    def late_indicator_upper_rule(m, i):
        """
        Force late indicator to 0 if lateness is 0.

        If late[i] = 0, then lateness[i] = 0.
        If late[i] = 1, then lateness[i] can be up to T.
        """
        return m.lateness[i] <= data['n_timeslots'] * m.late[i]

    model.late_indicator_upper = pyo.Constraint(
        model.ORDERS,
        rule=late_indicator_upper_rule,
        doc="Late indicator upper bound"
    )

    # Constraint: Late indicator lower bound
    def late_indicator_lower_rule(m, i):
        """
        Force late indicator to 1 if order is actually late.

        If completion_time > due_date, then late[i] must be 1.
        """
        return (
            m.time_completion[i] >=
            m.due[i] - data['n_timeslots'] * (1 - m.late[i])
        )

    model.late_indicator_lower = pyo.Constraint(
        model.ORDERS,
        rule=late_indicator_lower_rule,
        doc="Late indicator lower bound"
    )
