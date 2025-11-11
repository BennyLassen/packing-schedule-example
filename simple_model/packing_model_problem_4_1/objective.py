"""
Objective Function for Problem_4_1 Formulation

Based on Problem_4_1 Page 10:
Minimization objective function:
f = β * wip_obj + γ * workforce + δ * total_not_utilized

Note: This is a simplified 3-term objective compared to other formulations.
No explicit OTIF term in the objective (handled through constraints).
"""

import pyomo.environ as pyo


class ObjectiveManager:
    """
    Manages the objective function for the Problem_4_1 packing schedule model.

    Problem_4_1 Page 10:
    f = β * wip_obj + γ * workforce + δ * total_not_utilized

    Three-term objective:
    1. WIP: Work-in-progress inventory minimization
    2. Workforce: Workforce variability (range: max - min)
    3. Line utilization: Minimize unused capacity (not explicitly defined)

    Note: The third term "total_not_utilized" is not clearly defined in the PDF.
    Based on context, it likely refers to line utilization or a similar metric.
    For now, we'll interpret it as minimizing total inventory similar to WIP.
    """

    def __init__(self, data):
        """
        Initialize objective manager with user-specified weights.

        Args:
            data: Dictionary containing 'objective_weights' with keys:
                  - beta: WIP weight
                  - gamma: Workforce variability weight
                  - delta: Total not utilized weight (interpretation may vary)
        """
        # Default weights (Problem_4_1 simplified - 3 terms)
        self.weights = data.get('objective_weights', {
            'beta': 1.0,    # WIP weight
            'gamma': 0.5,   # Workforce variability weight
            'delta': 0.3    # Total not utilized weight
        })

    def _wip_term(self, m):
        """
        WIP term: Minimize total inventory across all time periods.

        Problem_4_1 Page 10:
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

        Problem_4_1 Page 10:
        workforce = workersrange = workersmax - workersmin

        This is already defined as a variable in the model.
        Lower range means more stable workforce utilization.
        """
        return m.workforcerange

    def _total_not_utilized_term(self, m):
        """
        Total not utilized term: Interpretation varies.

        Problem_4_1 Page 10 mentions this term but doesn't clearly define it.

        Possible interpretations:
        1. Unused line capacity
        2. Total slack/idle time
        3. Similar to WIP (redundant)

        For this implementation, we'll use a simple metric:
        Sum of (max_workers - workers_used) across all time periods,
        which represents unused worker capacity.
        """
        return sum(
            m.workersmax - m.workersused[t]
            for t in m.TIME
        )

    def define_objective(self, model):
        """
        Define the complete objective function for the model.

        Problem_4_1 Page 10:
        minimize: β*wip_obj + γ*workforce + δ*total_not_utilized

        Three terms weighted by user-specified parameters:
        1. WIP (beta): Total inventory across time
        2. Workforce (gamma): Workforce range (max - min)
        3. Total not utilized (delta): Unused capacity
        """

        def objective_rule(m):
            """Calculate the weighted sum of all objective terms."""
            return (
                self.weights['beta'] * self._wip_term(m) +
                self.weights['gamma'] * self._workforce_term(m) +
                self.weights['delta'] * self._total_not_utilized_term(m)
            )

        model.objective = pyo.Objective(
            rule=objective_rule,
            sense=pyo.minimize,
            doc="Minimize weighted sum of WIP, workforce, and unutilized capacity"
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
