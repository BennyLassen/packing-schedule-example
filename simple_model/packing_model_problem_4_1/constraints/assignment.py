"""
Assignment Constraints for Problem_4_1

One assignment constraint: Each order assigned to exactly one line and one time slot.
"""

import pyomo.environ as pyo


def define_assignment_constraints(model):
    """
    Define assignment constraints for Problem_4_1.

    Constraint: Each order must be assigned to exactly one line at exactly one time.

    Mathematical formulation (Problem_4_1 Page 4):
        ∑_j ∑_t x(i,j,t) = 1  ∀i

    This ensures every order is scheduled exactly once.
    """

    def one_assignment_rule(m, i):
        """
        Each order i must be assigned to exactly one line and one start time.

        Problem_4_1 Page 4: ∑_j ∑_t x(i,j,t) = 1  ∀i
        """
        return sum(
            m.x[i, j, t]
            for j in m.LINES
            for t in m.TIME
        ) == 1

    model.one_assignment = pyo.Constraint(
        model.ORDERS,
        rule=one_assignment_rule,
        doc="Each order assigned to exactly one line and time"
    )

    return model
