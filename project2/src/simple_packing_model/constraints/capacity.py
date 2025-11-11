"""
Capacity Constraints for Problem_3

Implements line capacity constraints to prevent overlapping orders on the same line.

From Problem_3.pdf Page 4:
- s(k) ≥ c(i) + s(i,k) - T_max * (3 - x(i,j) - x(k,j) - y(i,k))  ∀i < k ∀j
- s(i) ≥ c(k) + s(k,i) - T_max * (2 - x(i,j) - x(k,j) + y(i,k))  ∀i < k ∀j

These constraints ensure no overlap of orders on the same line, accounting for setup times.
"""

import pyomo.environ as pyo


def define_capacity_constraints(model):
    """
    Define line capacity constraints to prevent order overlaps.

    The constraints use a disjunctive formulation with binary variable y(i,k):
    - If both orders i and k are on line j, one must complete (with setup) before the other starts
    - y(i,k) = 1 means i is scheduled before k
    - y(i,k) = 0 means k is scheduled before i
    """

    def no_overlap_forward_rule(m, i, k, j):
        """
        If i is before k on the same line, k must start after i completes plus setup.

        s(k) ≥ c(i) + s(type(i), type(k)) - T_max * (3 - x(i,j) - x(k,j) - y(i,k))

        The constraint is active when:
        - x(i,j) = 1 (order i on line j)
        - x(k,j) = 1 (order k on line j)
        - y(i,k) = 1 (i before k)

        Then: s(k) ≥ c(i) + s(type(i), type(k))
        """
        if i >= k:
            return pyo.Constraint.Skip

        # Get the types for setup time lookup
        type_i = m.order_type[i]
        type_k = m.order_type[k]

        return m.start[k] >= (
            m.complete[i] + m.setup_time[type_i, type_k] -
            m.T_max_param * (3 - m.x[i, j] - m.x[k, j] - m.y[i, k])
        )

    model.no_overlap_forward = pyo.Constraint(
        model.ORDERS, model.ORDERS, model.LINES,
        rule=no_overlap_forward_rule,
        doc="Order k starts after order i completes (if i before k on same line)"
    )

    def no_overlap_backward_rule(m, i, k, j):
        """
        If k is before i on the same line, i must start after k completes plus setup.

        s(i) ≥ c(k) + s(type(k), type(i)) - T_max * (2 - x(i,j) - x(k,j) + y(i,k))

        The constraint is active when:
        - x(i,j) = 1 (order i on line j)
        - x(k,j) = 1 (order k on line j)
        - y(i,k) = 0 (k before i)

        Then: s(i) ≥ c(k) + s(type(k), type(i))
        """
        if i >= k:
            return pyo.Constraint.Skip

        # Get the types for setup time lookup
        type_i = m.order_type[i]
        type_k = m.order_type[k]

        return m.start[i] >= (
            m.complete[k] + m.setup_time[type_k, type_i] -
            m.T_max_param * (2 - m.x[i, j] - m.x[k, j] + m.y[i, k])
        )

    model.no_overlap_backward = pyo.Constraint(
        model.ORDERS, model.ORDERS, model.LINES,
        rule=no_overlap_backward_rule,
        doc="Order i starts after order k completes (if k before i on same line)"
    )

    return model
