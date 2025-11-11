"""
Assignment Constraints for Problem_4_1_c2

Implements:
- One assignment: Each order at most assigned to only one line
- Processing time relationship
- Time horizon constraints
- Line utilization: Track which lines are in use
"""

import pyomo.environ as pyo


def define_assignment_constraints(model):
    """
    Define assignment constraints for Problem_4_1_c2.

    From Problem_4_1_c2.pdf Page 4:
    1. One assignment: ∑_j x(i,j) ≤ 1  ∀i
    2. Processing time: c(i) = s(i) + ∑_j p(i,j) * x(i,j)  ∀i
    3. Time horizon: s(i) ≥ 0  ∀i
                     c(i) ≤ T_max  ∀i
    4. Line utilization: [u(j) = 1] ⇒ [∑_i x(i,j) > 0]  ∀j
                         [u(j) = 0] ⇒ [∑_i x(i,j) = 0]  ∀j
    """

    def one_assignment_rule(m, i):
        """
        Each order i is assigned to at most one line.

        ∑_j x(i,j) ≤ 1  ∀i

        Note: "at most" allows for orders not being scheduled if needed.
        """
        return sum(m.x[i, j] for j in m.LINES) <= 1

    model.one_assignment = pyo.Constraint(
        model.ORDERS,
        rule=one_assignment_rule,
        doc="Each order assigned to at most one line"
    )

    def processing_time_rule(m, i):
        """
        Completion time equals start time plus processing time.

        c(i) = s(i) + ∑_j p(type(i), j) * x(i,j)  ∀i

        Note: We need to use p(type(i), j) since processing time is by type.
        """
        order_type = m.order_type[i]
        return m.complete[i] == m.start[i] + sum(
            m.p[order_type, j] * m.x[i, j]
            for j in m.LINES
        )

    model.processing_time = pyo.Constraint(
        model.ORDERS,
        rule=processing_time_rule,
        doc="Completion time = start time + processing time"
    )

    def start_time_nonneg_rule(m, i):
        """
        Start time must be non-negative.

        s(i) ≥ 0  ∀i

        Note: This is already enforced by variable bounds, but included for clarity.
        """
        return m.start[i] >= 0

    model.start_time_nonneg = pyo.Constraint(
        model.ORDERS,
        rule=start_time_nonneg_rule,
        doc="Start times are non-negative"
    )

    def completion_within_horizon_rule(m, i):
        """
        Completion time must be within planning horizon.

        c(i) ≤ T_max  ∀i
        """
        return m.complete[i] <= m.T_max_param

    model.completion_within_horizon = pyo.Constraint(
        model.ORDERS,
        rule=completion_within_horizon_rule,
        doc="Completion times within planning horizon"
    )

    # ============================================
    # Line Utilization Constraints
    # ============================================

    def line_used_if_assigned_rule(m, j):
        """
        If line j is in use, at least one order must be assigned to it.

        [u(j) = 1] ⇒ [∑_i x(i,j) > 0]

        Reformulated as: ∑_i x(i,j) ≥ epsilon * u(j)

        This ensures that if u(j) = 1, then at least one order is assigned.
        We use epsilon (small positive value) instead of strict > 0.
        """
        return sum(m.x[i, j] for i in m.ORDERS) >= m.epsilon * m.u[j]

    model.line_used_if_assigned = pyo.Constraint(
        model.LINES,
        rule=line_used_if_assigned_rule,
        doc="If line in use, at least one order assigned"
    )

    def line_not_used_if_empty_rule(m, j):
        """
        If line j is not in use, no orders can be assigned to it.

        [u(j) = 0] ⇒ [∑_i x(i,j) = 0]

        Reformulated as: ∑_i x(i,j) ≤ M * u(j)

        This ensures that if u(j) = 0, then no orders are assigned.
        If u(j) = 1, the constraint is relaxed (up to M orders allowed).
        """
        # M can be the total number of orders as upper bound
        return sum(m.x[i, j] for i in m.ORDERS) <= m.n_orders * m.u[j]

    model.line_not_used_if_empty = pyo.Constraint(
        model.LINES,
        rule=line_not_used_if_empty_rule,
        doc="If line not in use, no orders assigned"
    )

    return model
