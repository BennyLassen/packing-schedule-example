"""
OTIF (On-Time In-Full) Constraints for Problem_4

Constraints to track order completion, lateness, and on-time delivery.
"""

import pyomo.environ as pyo


def define_otif_constraints(model):
    """
    Define OTIF-related constraints.

    Key constraints:
    1. Start time calculation
    2. Completion time calculation
    3. Lateness calculation (max of 0 and completion - due)
    4. Late order identification (binary indicator)
    """

    # ============================================
    # Start Time Calculation
    # ============================================

    def start_time_rule(m, i):
        """
        Calculate the start time for order i.

        Problem_4 Page 6:
        timestart(i) = ∑_j ∑_t t * x(i,j,t)  ∀i

        The start time is the weighted sum of time slots where x(i,j,t)=1.
        """
        return m.timestart[i] == sum(
            t * m.x[i, j, t]
            for j in m.LINES
            for t in m.TIME
        )

    model.start_time = pyo.Constraint(
        model.ORDERS,
        rule=start_time_rule,
        doc="Calculate start time for each order"
    )

    # ============================================
    # Completion Time Calculation
    # ============================================

    def completion_time_rule(m, i):
        """
        Calculate the completion time for order i.

        Problem_4 Page 6:
        timecompletion(i) = ∑_j ∑_t (t + p(i,j)) * x(i,j,t)  ∀i

        Completion time = start time + processing time on the assigned line.
        """
        return m.timecompletion[i] == sum(
            (t + m.p[i, j]) * m.x[i, j, t]
            for j in m.LINES
            for t in m.TIME
        )

    model.completion_time = pyo.Constraint(
        model.ORDERS,
        rule=completion_time_rule,
        doc="Calculate completion time for each order"
    )

    # ============================================
    # Lateness Calculation
    # ============================================

    # def lateness_lower_rule(m, i):
    #     """
    #     Lateness is at least the difference between completion and due date.

    #     Problem_4 Page 6:
    #     lateness(i) ≥ timecompletion(i) - due(i)  ∀i
    #     """
    #     return m.lateness[i] >= m.timecompletion[i] - m.due[i]

    # model.lateness_lower = pyo.Constraint(
    #     model.ORDERS,
    #     rule=lateness_lower_rule,
    #     doc="Lateness lower bound (completion - due)"
    # )

    # def lateness_nonneg_rule(m, i):
    #     """
    #     Lateness is always non-negative (0 if on-time).

    #     Problem_4 Page 6:
    #     lateness(i) ≥ 0  ∀i
    #     """
    #     return m.lateness[i] >= 0

    # model.lateness_nonneg = pyo.Constraint(
    #     model.ORDERS,
    #     rule=lateness_nonneg_rule,
    #     doc="Lateness is non-negative"
    # )

    # # ============================================
    # # Late Order Identification
    # # ============================================

    # def late_indicator_upper_rule(m, i):
    #     """
    #     Force late(i)=1 if lateness > 0.

    #     Problem_4 Page 6:
    #     lateness(i) ≤ T * late(i)  ∀i

    #     If lateness > 0, then late must be 1.
    #     If lateness = 0, then late can be 0 (minimization will force it to 0).
    #     """
    #     return m.lateness[i] <= m.n_timeslots * m.late[i]

    # model.late_indicator_upper = pyo.Constraint(
    #     model.ORDERS,
    #     rule=late_indicator_upper_rule,
    #     doc="Force late indicator if lateness > 0"
    # )

    # def late_indicator_lower_rule(m, i):
    #     """
    #     Force late(i)=1 if completion > due date.

    #     Problem_4 Page 6:
    #     timecompletion(i) > due(i) - T * (1 - late(i))  ∀i

    #     This is equivalent to:
    #     timecompletion(i) + T * (1 - late(i)) > due(i)

    #     When late=1: timecompletion ≥ due (can be late or on-time)
    #     When late=0: timecompletion ≥ due - T (forces timecompletion < due when due > 0)

    #     Note: The ">" constraint is implemented as ">=" in MILP.
    #     """
    #     return m.timecompletion[i] >= m.due[i] - m.n_timeslots * (1 - m.late[i])

    # model.late_indicator_lower = pyo.Constraint(
    #     model.ORDERS,
    #     rule=late_indicator_lower_rule,
    #     doc="Force late indicator if completion > due"
    # )

    return model
