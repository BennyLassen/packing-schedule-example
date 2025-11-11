"""
Shipping Constraints for Problem_4_1_c (Relaxed Version)

Constraints related to shipping and due dates.
Updated formulation from Problem_4_1_c.pdf Page 7.
"""

import pyomo.environ as pyo


def define_shipping_constraints(model):
    """
    Define shipping constraints for Problem_4_1_c.

    Two constraints (Problem_4_1_c Pages 5, 7):
    1. Each order ships exactly once
    2. Ship no earlier than due time (UPDATED FORMULATION)
    """

    def ship_once_rule(m, i):
        """
        Each order must ship exactly once.

        Problem_4_1_c Page 7:
        ∑_t ship(i,t) = 1  ∀i

        This ensures every order is shipped exactly once during the planning horizon.
        """
        return sum(m.ship[i, t] for t in m.TIME) == 1

    model.ship_once = pyo.Constraint(
        model.ORDERS,
        rule=ship_once_rule,
        doc="Each order ships exactly once"
    )

    def ship_after_due_rule(m, i):
        """
        Ship no earlier than due time.

        Problem_4_1_c Page 7 (UPDATED FORMULATION):
        ∑_t t * ship(i,t) ≥ due(i)  ∀i

        This constraint ensures that the shipping time (weighted sum)
        is at least the due date. This is a different formulation from
        the original Problem_4_1 which enforced ship(i,t) = 0 for t < due(i).

        The new formulation is more flexible and works better with LP relaxation.
        """
        return sum(t * m.ship[i, t] for t in m.TIME) >= m.due[i]

    model.ship_after_due = pyo.Constraint(
        model.ORDERS,
        rule=ship_after_due_rule,
        doc="Ship no earlier than due time (weighted formulation)"
    )

    return model
