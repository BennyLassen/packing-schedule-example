"""
Workforce Constraints for Problem_4 (Simplified)

Simplified workforce tracking - counts active workers by number of
simultaneous orders, not explicit worker assignment.

KEY SIMPLIFICATION: No worker index on assignment variable x(i,j,t).
Workers are counted implicitly based on line utilization.
"""

import pyomo.environ as pyo


def define_workforce_constraints(model):
    """
    Define simplified workforce tracking constraints.

    Key simplification from Problem_3:
    - No explicit worker assignment
    - Workers counted by simultaneous active orders
    - Tracks min/max workforce levels
    - Objective minimizes workforce range (max - min)

    Constraints:
    1. Active workers per time slot (count simultaneous orders)
    2. Maximum workforce tracking
    3. Minimum workforce tracking
    4. Workforce range calculation
    """

    # ============================================
    # Active Workers Per Time Slot
    # ============================================

    def workers_used_rule(m, tau):
        """
        Count workers needed at time tau by counting active orders.

        Problem_4 Page 9:
        workersused(τ) = ∑_i ∑_j ∑_{t ≤ τ < t+p(i,j)} x(i,j,t)  ∀τ

        The number of workers needed equals the number of orders
        being processed simultaneously. Each active order requires one worker.

        This is the KEY SIMPLIFICATION: Workers are counted, not assigned.
        """
        return m.workersused[tau] == sum(
            m.x[i, j, t]
            for i in m.ORDERS
            for j in m.LINES
            for t in m.TIME
            if t <= tau and tau < t + m.p[i, j]
        )

    model.workers_used = pyo.Constraint(
        model.TIME,
        rule=workers_used_rule,
        doc="Count active workers at each time slot"
    )

    # ============================================
    # Maximum Workforce Tracking
    # ============================================

    def max_workforce_rule(m, t):
        """
        Track the maximum number of workers used in any time slot.

        Problem_4 Page 9:
        workersmax ≥ workersused(t)  ∀t

        workersmax must be at least as large as the workforce
        at any individual time slot.
        """
        return m.workersmax >= m.workersused[t]

    model.max_workforce = pyo.Constraint(
        model.TIME,
        rule=max_workforce_rule,
        doc="Track maximum workforce level"
    )

    # ============================================
    # Minimum Workforce Tracking
    # ============================================

    def min_workforce_rule(m, t):
        """
        Track the minimum number of workers used in any time slot.

        Problem_4 Page 9:
        workersused(t) ≥ workersmin  ∀t

        workersmin must be at most the workforce at any time slot.

        Note: This allows workersmin to "float down" to the minimum
        workforce level seen across all time slots.
        """
        return m.workersused[t] >= m.workersmin

    model.min_workforce = pyo.Constraint(
        model.TIME,
        rule=min_workforce_rule,
        doc="Track minimum workforce level"
    )

    # ============================================
    # Workforce Range
    # ============================================

    def workforce_range_rule(m):
        """
        Calculate the range of workforce utilization.

        Problem_4 Page 9:
        workforcerange = workersmax - workersmin

        The workforce range measures variability in workforce levels.
        Minimizing this encourages stable workforce utilization.
        """
        return m.workforcerange == m.workersmax - m.workersmin

    model.workforce_range = pyo.Constraint(
        rule=workforce_range_rule,
        doc="Calculate workforce range (max - min)"
    )

    return model
