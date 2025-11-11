"""
WIP (Work-in-Progress) Constraints for Problem_3

Implements inventory balance equations.

From Problem_3.pdf Page 7:
- Inventory balance equation tracking WIP levels
- Shipped timing constraints
"""

import pyomo.environ as pyo


def define_wip_constraints(model):
    """
    Define WIP tracking constraints for Problem_3.

    Shipped timing:
    [shipped(d1,d) = 1] ⇒ [ship(d1) ≤ ship(d)]
    [shipped(d1,d) = 0] ⇒ [ship(d1) > ship(d)]
    """

    def inventory_balance_rule(m, u, d):
        """
        Inventory balance: starting inventory + produced - shipped = remaining inventory.

        inv(u,d) = inv0(u) + prodbefore(u,d) - ∑_{d1:prodtype(d1)=u} shipped(d1,d) * qty(d1)

        For each product type u and demand d, we track:
        - Initial inventory: inv0(u)
        - Production before demand d ships: prodbefore(u,d)
        - Demands shipped by time d: ∑_{d1:prodtype(d1)=u} shipped(d1,d) * qty(d1)

        The shipped(d1,d) binary variable indicates if demand d1 has shipped by the time
        demand d ships, so we only subtract the quantities that have actually been shipped.
        """
        # Calculate shipped demand for type u by time demand d ships
        shipped_demand = sum(
            m.shipped[d1, d] * m.qty[d1]
            for d1 in m.DEMANDS
            if m.prodtype[d1] == u
        )

        return m.inv[u, d] == m.inv0[u] + m.prodbefore[u, d] - shipped_demand

    model.inventory_balance = pyo.Constraint(
        model.TYPES, model.DEMANDS,
        rule=inventory_balance_rule,
        doc="Inventory balance equation for WIP tracking"
    )

    def inventory_nonnegative_rule(m, u, d):
        """
        Inventory must be non-negative (feasibility constraint).

        inv(u,d) ≥ 0  ∀u ∀d

        This ensures we don't go into negative inventory.
        """
        return m.inv[u, d] >= 0

    model.inventory_nonnegative = pyo.Constraint(
        model.TYPES, model.DEMANDS,
        rule=inventory_nonnegative_rule,
        doc="Inventory must be non-negative"
    )

    def shipped_before_rule(m, d1, d):
        """
        If shipped(d1,d) = 1, then demand d1 ships before or at the same time as demand d.

        [shipped(d1,d) = 1] ⇒ [ship(d1) ≤ ship(d)]

        Reformulated as: ship(d1) ≤ ship(d) + M * (1 - shipped(d1,d))
        """
        return m.ship[d1] <= m.ship[d] + m.M * (1 - m.shipped[d1, d])

    model.shipped_before = pyo.Constraint(
        model.DEMANDS, model.DEMANDS,
        rule=shipped_before_rule,
        doc="If shipped(d1,d)=1, then ship(d1) <= ship(d)"
    )

    def shipped_after_rule(m, d1, d):
        """
        If shipped(d1,d) = 0, then demand d1 ships after demand d.

        [shipped(d1,d) = 0] ⇒ [ship(d1) > ship(d)]

        Reformulated as: ship(d1) ≥ ship(d) + epsilon - M * shipped(d1,d)

        Note: We use epsilon to enforce strict inequality (ship(d1) > ship(d)).
        """
        return m.ship[d1] >= m.ship[d] + m.epsilon - m.M * m.shipped[d1, d]

    model.shipped_after = pyo.Constraint(
        model.DEMANDS, model.DEMANDS,
        rule=shipped_after_rule,
        doc="If shipped(d1,d)=0, then ship(d1) > ship(d)"
    )

    return model
