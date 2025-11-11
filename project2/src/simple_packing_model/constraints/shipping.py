"""
Shipping/Demand Constraints for Problem_3

Implements demand tracking and shipping constraints.

From Problem_3.pdf Page 6:
- Tracking produced items for demand
- Each order ships exactly once
- Ship no earlier than due time
"""

import pyomo.environ as pyo


def define_shipping_constraints(model):
    """
    Define shipping and demand constraints for Problem_3.

    From Page 6:
    1. Tracking produced items: prodbefore(u,d) = ∑_{i:type(i)=u} prodorder(i,d)
    2. Order timing and assignment: [prodorder(i,d) = 1] ⇒ [c(i) ≤ ship(d) ∧ x(i,j) = 1]
                                    [prodorder(i,d) = 0] ⇒ [c(i) ≥ ship(d) + ε]
    3. Ship time bounds: ship(d) ≤ T_max  ∀d
    4. Ship no earlier: ship(d) ≥ due(d)  ∀d
    """

    def track_produced_items_rule(m, u, d):
        """
        Track how many units of type u are produced before demand d ships.

        prodbefore(u,d) = ∑_{i:type(i)=u} prodorder(i,d)

        This sums up all orders of type u that complete before demand d.
        """
        return m.prodbefore[u, d] == sum(
            m.prodorder[i, d]
            for i in m.ORDERS
            if m.order_type[i] == u
        )

    model.track_produced_items = pyo.Constraint(
        model.TYPES, model.DEMANDS,
        rule=track_produced_items_rule,
        doc="Count units of type u produced before demand d"
    )

    def order_before_shipping_rule(m, i, d):
        """
        If order i is produced before demand d, it must complete before shipping.

        [prodorder(i,d) = 1] ⇒ [c(i) ≤ ship(d)]

        Reformulated as: c(i) ≤ ship(d) + M * (1 - prodorder(i,d))
        """
        return m.complete[i] <= m.ship[d] + m.M * (1 - m.prodorder[i, d])

    model.order_before_shipping = pyo.Constraint(
        model.ORDERS, model.DEMANDS,
        rule=order_before_shipping_rule,
        doc="If order produced before demand, it completes before shipping"
    )

    def order_assignment_required_rule(m, i, d):
        """
        If order i is produced before demand d, it must be assigned to a line.

        Updated from Problem_3.pdf Page 6:
        [prodorder(i,d) = 1] ⇒ [c(i) ≤ ship(d) ∧ x(i,j) = 1]

        The assignment part is reformulated as:
        ∑_j x(i,j) ≥ prodorder(i,d)

        This ensures that if prodorder(i,d) = 1, then the order must be assigned
        to at least one line. If prodorder(i,d) = 0, this constraint is trivially satisfied.
        """
        return sum(m.x[i, j] for j in m.LINES) >= m.prodorder[i, d]

    model.order_assignment_required = pyo.Constraint(
        model.ORDERS, model.DEMANDS,
        rule=order_assignment_required_rule,
        doc="If order produced before demand, it must be assigned to a line"
    )

    def order_after_shipping_rule(m, i, d):
        """
        If order i is NOT produced before demand d, it must complete after shipping.

        [prodorder(i,d) = 0] ⇒ [c(i) ≥ ship(d) + ε]

        Reformulated as: c(i) ≥ ship(d) + epsilon - M * prodorder(i,d)
        """
        return m.complete[i] >= m.ship[d] + m.epsilon - m.M * m.prodorder[i, d]

    model.order_after_shipping = pyo.Constraint(
        model.ORDERS, model.DEMANDS,
        rule=order_after_shipping_rule,
        doc="If order not produced before demand, it completes after shipping"
    )

    def ship_within_horizon_rule(m, d):
        """
        Each demand must ship within the planning horizon.

        ship(d) ≤ T_max  ∀d
        """
        return m.ship[d] <= m.T_max_param

    model.ship_within_horizon = pyo.Constraint(
        model.DEMANDS,
        rule=ship_within_horizon_rule,
        doc="Shipping times within planning horizon"
    )

    def ship_no_earlier_than_due_rule(m, d):
        """
        Ship no earlier than due date.

        ship(d) ≥ due(d)  ∀d

        This ensures we don't ship before the customer wants it.
        """
        return m.ship[d] >= m.due[d]

    model.ship_no_earlier_than_due = pyo.Constraint(
        model.DEMANDS,
        rule=ship_no_earlier_than_due_rule,
        doc="Ship no earlier than due date"
    )

    return model
