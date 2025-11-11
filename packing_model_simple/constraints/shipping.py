"""
Shipping Constraints for Problem_4

Constraints related to order shipping and inventory availability.
"""

import pyomo.environ as pyo


def define_shipping_constraints(model):
    """
    Define shipping-related constraints.

    Key constraints:
    1. Each order ships exactly once
    2. Shipping time calculation
    3. Cannot ship before order complete
    4. Has inventory indicator (Big-M)
    5. Can only ship when inventory is sufficient
    """

    # ============================================
    # Each Order Ships Exactly Once
    # ============================================

    def ship_once_rule(m, i):
        """
        Each order must be shipped exactly once during the planning horizon.

        Problem_4 Page 5:
        ∑_t ship(i,t) = 1  ∀i
        """
        return sum(m.ship[i, t] for t in m.TIME) == 1

    model.ship_once = pyo.Constraint(
        model.ORDERS,
        rule=ship_once_rule,
        doc="Each order ships exactly once"
    )

    # ============================================
    # Shipping Time Calculation
    # ============================================

    def shipping_time_rule(m, i):
        """
        Calculate the time slot when order i is shipped.

        Problem_4 Page 5:
        timeship(i) = ∑_t t * ship(i,t)  ∀i
        """
        return m.timeship[i] == sum(
            t * m.ship[i, t]
            for t in m.TIME
        )

    model.shipping_time = pyo.Constraint(
        model.ORDERS,
        rule=shipping_time_rule,
        doc="Calculate shipping time for each order"
    )

    # ============================================
    # Cannot Ship Before Completion
    # ============================================

    def ship_after_complete_rule(m, i):
        """
        Order cannot be shipped before it is completed.

        Problem_4 Page 7:
        timeship(i) ≥ timecompletion(i)  ∀i
        """
        return m.timeship[i] >= m.timecompletion[i]

    model.ship_after_complete = pyo.Constraint(
        model.ORDERS,
        rule=ship_after_complete_rule,
        doc="Cannot ship before order completion"
    )

    # ============================================
    # Has Inventory Indicator (Big-M Constraints)
    # ============================================

    def has_inventory_lower_rule(m, i, t):
        """
        If inventory is positive, hasinv(i,t) can be 1.

        Problem_4 Page 7:
        inv(i,t) ≥ due(i,t) - M * (1 - hasinv(i,t))  ∀i ∀t

        Note: This appears to have a typo in the PDF. It should be:
        inv(i,t) ≥ 1 - M * (1 - hasinv(i,t))

        When hasinv=1: inv ≥ 1 (has inventory)
        When hasinv=0: inv ≥ 1-M (constraint inactive, can be 0)
        """
        return m.inv[i, t] >= 1 - m.M * (1 - m.hasinv[i, t])

    model.has_inventory_lower = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=has_inventory_lower_rule,
        doc="Lower bound for has inventory indicator"
    )

    def has_inventory_upper_rule(m, i, t):
        """
        If inventory is zero, hasinv(i,t) must be 0.

        Problem_4 Page 7:
        inv(i,t) ≤ M * hasinv(i,t)  ∀i ∀t

        When hasinv=1: inv ≤ M (constraint inactive)
        When hasinv=0: inv ≤ 0 (no inventory)
        """
        return m.inv[i, t] <= m.M * m.hasinv[i, t]

    model.has_inventory_upper = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=has_inventory_upper_rule,
        doc="Upper bound for has inventory indicator"
    )

    # ============================================
    # Can Only Ship When Inventory Sufficient
    # ============================================

    def ship_requires_inventory_rule(m, i, t):
        """
        Can only ship order i at time t if there is available inventory.

        Problem_4 Page 7:
        ship(i,t) ≤ hasinv(i,t)  ∀i ∀t
        """
        return m.ship[i, t] <= m.hasinv[i, t]

    model.ship_requires_inventory = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=ship_requires_inventory_rule,
        doc="Can only ship when inventory is available"
    )

    return model
