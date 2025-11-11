"""
Shipping Constraints Module (NEW for Problem 2)

This module defines constraints related to shipping decisions,
which replaces the fixed shipping schedule from Problem 1.
"""

import pyomo.environ as pyo


def add_shipping_constraints(model, data):
    """
    Add shipping-related constraints.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: Each order ships exactly once
    def ship_once_rule(m, i):
        """Each order must ship exactly once across all time slots."""
        return sum(m.ship[i, t] for t in m.TIME) == 1

    model.ship_once = pyo.Constraint(
        model.ORDERS,
        rule=ship_once_rule,
        doc="Each order ships exactly once"
    )

    # Constraint: Calculate shipping time
    def shipping_time_rule(m, i):
        """Calculate when order i ships."""
        return m.time_ship[i] == sum(t * m.ship[i, t] for t in m.TIME)

    model.shipping_time_calc = pyo.Constraint(
        model.ORDERS,
        rule=shipping_time_rule,
        doc="Calculate shipping time for each order"
    )

    # Constraint: Cannot ship before completion
    def ship_after_completion_rule(m, i):
        """Order can only ship after it has been completed."""
        return m.time_ship[i] >= m.time_completion[i]

    model.ship_after_completion = pyo.Constraint(
        model.ORDERS,
        rule=ship_after_completion_rule,
        doc="Cannot ship before order completion"
    )

    # Big-M for indicator constraints
    BIG_M = data['n_timeslots'] * 1000  # Large enough constant

    # Constraint: Determine if ship is early
    def ship_early_indicator_1(m, i):
        """Force ship_early = 1 if time_ship < due date."""
        return m.time_ship[i] <= m.due[i] + BIG_M * (1 - m.ship_early[i])

    model.ship_early_ind_1 = pyo.Constraint(
        model.ORDERS,
        rule=ship_early_indicator_1,
        doc="Ship early indicator part 1"
    )

    def ship_early_indicator_2(m, i):
        """Force ship_early = 0 if time_ship >= due date."""
        return m.time_ship[i] >= m.due[i] - BIG_M * m.ship_early[i]

    model.ship_early_ind_2 = pyo.Constraint(
        model.ORDERS,
        rule=ship_early_indicator_2,
        doc="Ship early indicator part 2"
    )

    # Constraint: Determine if ship is late
    def ship_late_indicator_1(m, i):
        """Force ship_late = 1 if time_ship > due date."""
        return m.time_ship[i] >= m.due[i] + 1 - BIG_M * (1 - m.ship_late[i])

    model.ship_late_ind_1 = pyo.Constraint(
        model.ORDERS,
        rule=ship_late_indicator_1,
        doc="Ship late indicator part 1"
    )

    def ship_late_indicator_2(m, i):
        """Force ship_late = 0 if time_ship <= due date."""
        return m.time_ship[i] <= m.due[i] + BIG_M * m.ship_late[i]

    model.ship_late_ind_2 = pyo.Constraint(
        model.ORDERS,
        rule=ship_late_indicator_2,
        doc="Ship late indicator part 2"
    )

    # Constraint: Order is either early, on-time, or late
    def ship_timing_status_rule(m, i):
        """Order must be classified as early, on-time, or late."""
        return m.ship_early[i] + m.ship_late[i] <= 1

    model.ship_timing_status = pyo.Constraint(
        model.ORDERS,
        rule=ship_timing_status_rule,
        doc="Order timing classification"
    )
