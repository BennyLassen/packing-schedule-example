"""
Objective Function for Problem_4 Simplified Formulation

Four-term objective function (no worker movement penalty compared to Problem_3):
1. OTIF: On-time delivery with priority weighting
2. WIP: Work-in-progress inventory minimization
3. Workforce: Workforce variability (range: max - min)
4. Line utilization: Number of lines activated
"""

import pyomo.environ as pyo


class ObjectiveManager:
    """
    Manages the objective function for the simplified packing schedule model.

    Problem_4 Page 10:
    f = α*otif + β*wip_obj + γ*workforce + δ*total_not_utilized

    Key simplification from Problem_3:
    - NO worker movement penalty (omega term removed)
    - Workforce term is simply the range (workersmax - workersmin)
    """

    def __init__(self, data):
        """
        Initialize objective manager with user-specified weights.

        Args:
            data: Dictionary containing 'objective_weights' with keys:
                  - alpha: OTIF weight
                  - beta: WIP weight
                  - gamma: Workforce variability weight
                  - delta: Line utilization weight
        """
        # Default weights (Problem_4 simplified - no omega)
        self.weights = data.get('objective_weights', {
            'alpha': 1.0,   # OTIF weight
            'beta': 0.5,    # WIP weight
            'gamma': 0.3,   # Workforce variability weight
            'delta': 0.2    # Line utilization weight
        })

    def _otif_term(self, m):
        """
        OTIF term: Penalize late deliveries and lateness.

        Problem_4 Page 10:
        otif = ∑_i priority(i) * (7 * late(i) + 3 * lateness(i))

        Heavy penalty for being late (coefficient 7), plus proportional
        penalty for how late (coefficient 3).
        """
        return sum(
            m.priority[i] * (7 * m.late[i] + 3 * m.lateness[i])
            for i in m.ORDERS
        )

    def _wip_term(self, m):
        """
        WIP term: Minimize total inventory across all time periods.

        Problem_4 Page 10:
        wip_obj = ∑_t inv(t)

        Note: This sums inventory across all orders at each time.
        Lower WIP means faster flow through the system.
        """
        return sum(
            m.inv[i, t]
            for i in m.ORDERS
            for t in m.TIME
        )

    def _workforce_term(self, m):
        """
        Workforce term: Minimize workforce variability.

        Problem_4 Page 10:
        workforce = workersrange = workersmax - workersmin

        KEY SIMPLIFICATION: Instead of complex workforce variability
        calculations in Problem_3, we simply minimize the range.

        Lower range means more stable workforce utilization.
        """
        return m.workforcerange

    def _line_utilization_term(self, m):
        """
        Line utilization term: Minimize number of lines activated.

        Problem_4 Page 10:
        total_not_utilized = ∑_j u(j)

        Note: The name is somewhat misleading - this actually counts
        the number of lines USED, not unused. Minimizing this term
        encourages using fewer lines.
        """
        return sum(m.u[j] for j in m.LINES)

    def define_objective(self, model):
        """
        Define the complete objective function for the model.

        Problem_4 Page 10:
        minimize: α*otif + β*wip_obj + γ*workforce + δ*total_not_utilized

        Four terms weighted by user-specified parameters:
        1. OTIF (alpha): Priority-weighted late deliveries and lateness
        2. WIP (beta): Total inventory across time
        3. Workforce (gamma): Workforce range (max - min)
        4. Line utilization (delta): Number of lines activated
        """

        def objective_rule(m):
            """Calculate the weighted sum of all objective terms."""
            return (
                self.weights['alpha'] * self._otif_term(m) +
                self.weights['beta'] * self._wip_term(m) +
                self.weights['gamma'] * self._workforce_term(m) +
                self.weights['delta'] * self._line_utilization_term(m)
            )

        model.objective = pyo.Objective(
            rule=objective_rule,
            sense=pyo.minimize,
            doc="Minimize weighted sum of OTIF, WIP, workforce, and line utilization"
        )

        return model


def define_objective(model, data):
    """
    Convenience function to define the objective for a model.

    Args:
        model: Pyomo ConcreteModel
        data: Dictionary with input data including objective_weights

    Returns:
        model: Model with objective defined
    """
    obj_manager = ObjectiveManager(data)
    return obj_manager.define_objective(model)
