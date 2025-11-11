"""
Workforce Constraints

This module defines constraints for workforce management,
including tracking worker usage, deviations from targets, and workforce changes.
"""

import pyomo.environ as pyo


def add_workforce_constraints(model, data):
    """
    Add workforce-related constraints to the model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: Calculate total workers used at each time
    def workers_used_rule(m, t):
        """
        Calculate total workers active at time t.

        Sum the working indicator across all workers.
        """
        return m.workers_used[t] == sum(m.w_working[w, t] for w in m.WORKERS)

    model.workers_used_calc = pyo.Constraint(
        model.TIME,
        rule=workers_used_rule,
        doc="Calculate workers used at each time"
    )

    # Constraint: Track maximum workforce
    def workers_max_rule(m, t):
        """
        Track the maximum workforce level.

        workers_max must be >= workers_used for all time periods.
        """
        return m.workers_max >= m.workers_used[t]

    model.workers_max_calc = pyo.Constraint(
        model.TIME,
        rule=workers_max_rule,
        doc="Track maximum workforce"
    )

    # Constraint: Track minimum workforce
    def workers_min_rule(m, t):
        """
        Track the minimum workforce level.

        workers_min must be <= workers_used for all time periods.
        """
        return m.workers_used[t] >= m.workers_min

    model.workers_min_calc = pyo.Constraint(
        model.TIME,
        rule=workers_min_rule,
        doc="Track minimum workforce"
    )

    # Constraint: Workforce deviation from target
    def workforce_deviation_rule(m, t):
        """
        Calculate deviation from target workforce.

        workers_used = target + deviation_above - deviation_below

        The optimizer will choose to make only one deviation positive
        at any given time to minimize the objective.
        """
        return (
            m.workers_used[t] ==
            m.workforce_target + m.deviation_above[t] - m.deviation_below[t]
        )

    model.workforce_deviation = pyo.Constraint(
        model.TIME,
        rule=workforce_deviation_rule,
        doc="Workforce deviation from target"
    )

    # Constraint: Workforce change calculation for t>1
    def workforce_change_rule(m, t):
        """
        Calculate workforce change between consecutive periods.

        workers_used[t] = workers_used[t-1] + increase - decrease
        """
        if t == 1:
            return pyo.Constraint.Skip
        return (
            m.workers_used[t] ==
            m.workers_used[t-1] + m.workforce_increase[t] - m.workforce_decrease[t]
        )

    model.workforce_change_calc = pyo.Constraint(
        model.TIME,
        rule=workforce_change_rule,
        doc="Workforce change calculation"
    )

    # Constraint: Total workforce change (absolute value)
    def workforce_change_total_rule(m, t):
        """
        Calculate total absolute workforce change.

        workforce_change = increase + decrease

        This gives the absolute value of change between periods.
        """
        if t == 1:
            return pyo.Constraint.Skip
        return m.workforce_change[t] == m.workforce_increase[t] + m.workforce_decrease[t]

    model.workforce_change_total = pyo.Constraint(
        model.TIME,
        rule=workforce_change_total_rule,
        doc="Total absolute workforce change"
    )
