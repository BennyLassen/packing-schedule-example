"""
Capacity Constraints for Problem_4

Line capacity constraints with setup times and reserved capacity.
"""

import pyomo.environ as pyo


def define_capacity_constraints(model):
    """
    Define line capacity and reserved capacity constraints.

    Key constraints:
    1. Line capacity: No overlap of orders on the same line
    2. Reserved capacity: Total utilization < (1-alpha) * total capacity
    3. Line in use: Track which lines are active
    """

    # ============================================
    # Line Capacity: No Overlap on Same Line
    # ============================================

    def line_capacity_rule(m, j, tau):
        """
        No overlap of orders on the same line (simplified formulation).

        For each line j and time tau, at most one order can be processing.
        We use a simplified approach: An order starting at time t occupies
        the line for p(i,j) time slots (processing only).

        Setup times are handled separately through sequencing constraints.
        This is a simplification from the PDF formulation to avoid
        non-linearities in the capacity constraint.
        """
        # Count orders active at time tau (processing only, no setup in this constraint)
        active_orders = sum(
            m.x[i, j, t]
            for i in m.ORDERS
            for t in m.TIME
            if t <= tau and tau < t + m.p[i, j]
        )
        return active_orders <= m.u[j]

    model.line_capacity = pyo.Constraint(
        model.LINES, model.TIME,
        rule=line_capacity_rule,
        doc="No overlap of orders on the same line"
    )

    # ============================================
    # Reserved Line Capacity
    # ============================================

    def reserved_capacity_rule(m):
        """
        Total line utilization must leave alpha fraction of capacity reserved (simplified).

        Total processing time across all lines must be less than
        (1 - alpha) * (number of lines) * (number of time slots).

        This counts each order's processing time when it's scheduled.
        """
        # Sum of processing times across all orders
        total_processing = sum(
            m.x[i, j, t] * m.p[i, j]
            for i in m.ORDERS
            for j in m.LINES
            for t in m.TIME
        )

        reserved_slots = (1 - m.alpha) * m.n_lines * m.n_timeslots

        return total_processing <= reserved_slots

    model.reserved_capacity = pyo.Constraint(
        rule=reserved_capacity_rule,
        doc="Reserve alpha fraction of total capacity"
    )

    # ============================================
    # Line In Use Indicator
    # ============================================

    def line_in_use_rule(m, j, tau):
        """
        Track which lines are being used.

        If any order is processing on line j at time tau, then u(j) must be 1.

        Problem_4 Page 5:
        ∑_i ∑_{t ≤ τ < t+p(i,j)} x(i,j,t) ≤ u(j)  ∀τ

        Note: This is a simpler version without setup time in the summation.
        """
        return sum(
            m.x[i, j, t]
            for i in m.ORDERS
            for t in m.TIME
            if t <= tau < t + m.p[i, j]
        ) <= m.u[j]

    model.line_in_use = pyo.Constraint(
        model.LINES, model.TIME,
        rule=line_in_use_rule,
        doc="Track which lines are being used"
    )

    return model
