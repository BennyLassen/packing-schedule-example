"""
Workforce Constraints for Problem_4_1

Workforce tracking and range constraints.
"""

import pyomo.environ as pyo


def define_workforce_constraints(model):
    """
    Define workforce constraints for Problem_4_1.

    Constraints (Problem_4_1 Page 9):
    1. Active workers per time slot
    2. Maximum workforce tracking
    3. Minimum workforce tracking
    4. Workforce range definition
    """

    def workers_used_rule(m, tau):
        """
        Active workers per time slot.

        Problem_4_1 Page 9:
        workersused(τ) = ∑_i ∑_j ∑_{t: t≤τ<t+p(i,j)} x(i,j,t)  ∀τ

        This counts the number of active orders at time tau,
        which equals the number of workers needed.
        """
        return m.workersused[tau] == sum(
            m.x[i, j, t]
            for i in m.ORDERS
            for j in m.LINES
            for t in m.TIME
            if t <= tau < t + m.p[i, j] and t + m.p[i, j] <= m.n_timeslots + 1
        )

    model.workers_used = pyo.Constraint(
        model.TIME,
        rule=workers_used_rule,
        doc="Active workers per time slot"
    )

    def max_workers_rule(m, t):
        """
        Maximum workforce tracking.

        Problem_4_1 Page 9:
        workersmax ≥ workersused(t)  ∀t

        Ensures workersmax captures the maximum workforce level.
        """
        return m.workersmax >= m.workersused[t]

    model.max_workers = pyo.Constraint(
        model.TIME,
        rule=max_workers_rule,
        doc="Maximum workforce tracking"
    )

    def min_workers_rule(m, t):
        """
        Minimum workforce tracking.

        Problem_4_1 Page 9:
        workersused(t) ≥ workersmin  ∀t

        Ensures workersmin captures the minimum workforce level.
        """
        return m.workersused[t] >= m.workersmin

    model.min_workers = pyo.Constraint(
        model.TIME,
        rule=min_workers_rule,
        doc="Minimum workforce tracking"
    )

    def workforce_range_rule(m):
        """
        Workforce range definition.

        Problem_4_1 Page 9:
        workforce_range = workersmax - workersmin

        Defines the workforce range variable.
        """
        return m.workforcerange == m.workersmax - m.workersmin

    model.workforce_range = pyo.Constraint(
        rule=workforce_range_rule,
        doc="Workforce range definition"
    )

    return model
