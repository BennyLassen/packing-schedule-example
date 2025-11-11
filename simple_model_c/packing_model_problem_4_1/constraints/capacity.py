"""
Capacity Constraints for Problem_4_1

Line capacity and reserved capacity constraints.
"""

import pyomo.environ as pyo


def define_capacity_constraints(model):
    """
    Define capacity constraints for Problem_4_1.

    Two constraints (Problem_4_1 Page 4):
    1. Line capacity: No overlap of orders on the same line
    2. Reserved line capacity: Reserve alpha fraction of total capacity
    """

    def line_capacity_rule(m, j, tau):
        """
        Line capacity constraint: No overlap of orders on the same line.

        Problem_4_1 Page 4:
        ∑_i ∑_{t: t≤τ<t+p(i,j)} x(i,j,t) ≤ 1  ∀j, ∀τ

        This ensures that at most one order is being processed on line j
        at any time tau.
        """
        return sum(
            m.x[i, j, t]
            for i in m.ORDERS
            for t in m.TIME
            if t <= tau < t + m.p[i, j] and t + m.p[i, j] <= m.n_timeslots + 1
        ) <= 1

    model.line_capacity = pyo.Constraint(
        model.LINES, model.TIME,
        rule=line_capacity_rule,
        doc="No overlap of orders on the same line"
    )

    def reserved_capacity_rule(m):
        """
        Reserved capacity constraint: Keep alpha fraction of capacity reserved.

        Problem_4_1 Page 4:
        ∑_i ∑_j ∑_τ ∑_{t: t≤τ<t+p(i,j)} x(i,j,t) ≤ (1-α) * m * T

        This ensures that we don't use more than (1-alpha) of the total
        available capacity (m lines × T time slots).
        """
        total_capacity = m.n_lines * m.n_timeslots

        return sum(
            m.x[i, j, t]
            for i in m.ORDERS
            for j in m.LINES
            for tau in m.TIME
            for t in m.TIME
            if t <= tau < t + m.p[i, j] and t + m.p[i, j] <= m.n_timeslots + 1
        ) <= (1 - m.alpha) * total_capacity

    model.reserved_capacity = pyo.Constraint(
        rule=reserved_capacity_rule,
        doc="Reserved capacity constraint"
    )

    return model
