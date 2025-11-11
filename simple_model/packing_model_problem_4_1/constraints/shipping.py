"""
Shipping Constraints for Problem_4_1

Constraints related to shipping and due dates.
"""

import pyomo.environ as pyo


def define_shipping_constraints(model):
    """
    Define shipping constraints for Problem_4_1.

    Two constraints (Problem_4_1 Pages 5, 7):
    1. Each order ships exactly once
    2. Ship no earlier than due time
    """

    def ship_once_rule(m, i):
        """
        Each order must ship exactly once.

        Problem_4_1 Page 5:
        ∑_t ship(i,t) = 1  ∀i

        This ensures every order is shipped exactly once during the planning horizon.
        """
        return sum(m.ship[i, t] for t in m.TIME) == 1

    model.ship_once = pyo.Constraint(
        model.ORDERS,
        rule=ship_once_rule,
        doc="Each order ships exactly once"
    )

    def ship_after_due_rule(m, i, t):
        """
        Ship no earlier than due time.

        Problem_4_1 Page 7:
        ship(i) ≥ due(i)

        This constraint is implemented as: if ship(i,t) = 1, then t ≥ due(i)
        Or equivalently: ship(i,t) = 0 for all t < due(i)
        """
        if t < m.due[i]:
            return m.ship[i, t] == 0
        else:
            return pyo.Constraint.Skip

    model.ship_after_due = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=ship_after_due_rule,
        doc="Ship no earlier than due time"
    )

    return model
