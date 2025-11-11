"""
Capacity Constraints

This module defines constraints related to line capacity, ensuring no overlap
of orders on the same line and respecting capacity reservations.
"""

import pyomo.environ as pyo


def add_capacity_constraints(model, data):
    """
    Add capacity-related constraints to the model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: No overlap of orders on the same line
    def line_capacity_rule(m, j, tau):
        """
        Prevent overlapping orders on the same line.

        For each line j and time tau, ensure that at most one order
        is being processed. An order starting at time t is processing
        at time tau if t <= tau < t + processing_time.
        """
        expr = 0
        for i in m.ORDERS:
            for w in m.WORKERS:
                for t in m.TIME:
                    # Check if order starting at t would be processing at tau
                    if t <= tau < t + int(m.p[i, j]):
                        expr += m.x[i, j, t, w]
        return expr <= m.u[j]

    model.line_capacity = pyo.Constraint(
        model.LINES, model.TIME,
        rule=line_capacity_rule,
        doc="No overlap of orders on same line"
    )

    # Constraint: Reserved line capacity
    def reserved_line_capacity_rule(m):
        """
        Reserve a fraction of total line capacity.

        Total usage (processing time * assignments) should not exceed
        (1 - alpha) * total available capacity, where alpha is the
        reserved capacity fraction.
        """
        total_usage = sum(
            m.x[i, j, t, w] * m.p[i, j]
            for i in m.ORDERS
            for j in m.LINES
            for t in m.TIME
            for w in m.WORKERS
        )
        total_capacity = (1 - m.alpha) * data['n_lines'] * data['n_timeslots']
        return total_usage <= total_capacity

    model.reserved_line_capacity = pyo.Constraint(
        rule=reserved_line_capacity_rule,
        doc="Reserve fraction of line capacity"
    )

    # Constraint: Line in use indicator (upper bound)
    def line_in_use_rule(m, j):
        """
        Link line usage indicator to assignments (upper bound).

        If line j is used (u[j] = 1), allow assignments to it.
        If line j is not used (u[j] = 0), no assignments allowed.
        """
        return sum(
            m.x[i, j, t, w]
            for i in m.ORDERS
            for t in m.TIME
            for w in m.WORKERS
        ) <= m.u[j] * data['n_orders'] * data['n_timeslots']

    model.line_in_use = pyo.Constraint(
        model.LINES,
        rule=line_in_use_rule,
        doc="Line usage indicator upper bound"
    )

    # Constraint: Line in use indicator (lower bound)
    def line_in_use_lower_rule(m, j):
        """
        Link line usage indicator to assignments (lower bound).

        If any order is assigned to line j, then u[j] must be 1.
        This forces u[j] = 1 when the line has at least one assignment.
        """
        return m.u[j] <= sum(
            m.x[i, j, t, w]
            for i in m.ORDERS
            for t in m.TIME
            for w in m.WORKERS
        )

    model.line_in_use_lower = pyo.Constraint(
        model.LINES,
        rule=line_in_use_lower_rule,
        doc="Line usage indicator lower bound"
    )
