"""
WIP (Work-In-Progress) Constraints for Problem_4_1

Inventory balance and production tracking constraints.
"""

import pyomo.environ as pyo


def define_wip_constraints(model):
    """
    Define WIP constraints for Problem_4_1.

    Constraints (Problem_4_1 Page 8):
    1. Number of packing orders produced
    2. Inventory balance equation
    3. Initial inventory
    """

    def production_rule(m, i, t):
        """
        Number of packing orders produced at time t.

        Problem_4_1 Page 8:
        prod(i,t) = ∑_j x(i, j, t - p(i,j))

        This means order i is completed at time t if it started at time t-p(i,j)
        on some line j.
        """
        return m.prod[i, t] == sum(
            m.x[i, j, t_start]
            for j in m.LINES
            for t_start in m.TIME
            if t_start + m.p[i, j] == t and t_start + m.p[i, j] <= m.n_timeslots
        )

    model.production = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=production_rule,
        doc="Production at time t"
    )

    def inventory_balance_rule(m, i, t):
        """
        Inventory balance equation.

        Problem_4_1 Page 8:
        inv(i,t) = inv(i,t-1) + prod(i,t) - ship(i,t)  ∀i, ∀t > 0

        This is the standard inventory flow equation:
        current inventory = previous inventory + production - shipments
        """
        if t == 0:
            return pyo.Constraint.Skip
        return m.inv[i, t] == m.inv[i, t-1] + m.prod[i, t] - m.ship[i, t]

    model.inventory_balance = pyo.Constraint(
        model.ORDERS, model.TIME_WITH_ZERO,
        rule=inventory_balance_rule,
        doc="Inventory balance equation"
    )

    def initial_inventory_rule(m, i):
        """
        Initial inventory condition.

        Problem_4_1 Page 8:
        inv(i,0) = inv0(i)  ∀i

        Sets the initial inventory for each order.
        """
        return m.inv[i, 0] == m.inv0[i]

    model.initial_inventory = pyo.Constraint(
        model.ORDERS,
        rule=initial_inventory_rule,
        doc="Initial inventory"
    )

    return model
