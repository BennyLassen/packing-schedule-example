"""
WIP (Work-In-Progress) Constraints for Problem_4

Constraints for inventory management and flow time tracking.
"""

import pyomo.environ as pyo


def define_wip_constraints(model):
    """
    Define WIP and inventory-related constraints.

    Key constraints:
    1. Flow time calculation (ship time - start time)
    2. Number of units produced at each time
    3. Inventory balance equation
    4. Initial inventory condition
    """

    # ============================================
    # Flow Time Calculation
    # ============================================

    def flow_time_rule(m, i):
        """
        Flow time is the time from start to shipment.

        Problem_4 Page 8:
        timeflow(i) = timeship(i) - timestart(i)  ∀i

        This measures how long the order is in the system.
        """
        return m.timeflow[i] == m.timeship[i] - m.timestart[i]

    model.flow_time = pyo.Constraint(
        model.ORDERS,
        rule=flow_time_rule,
        doc="Calculate flow time for each order"
    )

    # ============================================
    # Production at Each Time Slot
    # ============================================

    def production_rule(m, i, t):
        """
        Number of units produced at time t for order i.

        Problem_4 Page 8 (matching Problem_3 Page 9):
        prod(i,t) = ∑_j x(i, j, t - p(i,j))

        An order completes at time t if it started at time t - p(i,j).
        We must check that t - p(i,j) >= 1 (valid time slot).

        CRITICAL FIX: Directly reference x[i, j, t - p(i,j)] with bounds checking,
        rather than iterating and checking conditions.
        """
        return m.prod[i, t] == sum(
            m.x[i, j, t - int(m.p[i, j])]
            for j in m.LINES
            if t - int(m.p[i, j]) >= 1  # Only sum if start time is valid
        )

    model.production = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=production_rule,
        doc="Calculate production completing at each time slot"
    )

    # ============================================
    # Inventory Balance Equation
    # ============================================

    def inventory_balance_rule(m, i, t):
        """
        Inventory balance: previous inventory + production - shipments.

        Problem_4 Page 8:
        inv(i,t) = inv(i,t-1) + prod(i,t) - ship(i,t)  ∀i, ∀t > 0

        Inventory at time t equals:
        - Inventory at previous time
        - Plus units produced at this time
        - Minus units shipped at this time
        """
        return m.inv[i, t] == m.inv[i, t-1] + m.prod[i, t] - m.ship[i, t]

    model.inventory_balance = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=inventory_balance_rule,
        doc="Inventory balance equation"
    )

    # ============================================
    # Initial Inventory
    # ============================================

    def initial_inventory_rule(m, i):
        """
        Set initial inventory for each order.

        Problem_4 Page 8:
        inv(i,0) = inv0(i)  ∀i

        At time 0, inventory equals the initial stock parameter.
        """
        return m.inv[i, 0] == m.inv0[i]

    model.initial_inventory = pyo.Constraint(
        model.ORDERS,
        rule=initial_inventory_rule,
        doc="Set initial inventory for each order"
    )

    return model
