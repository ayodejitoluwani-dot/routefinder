"""
Route scoring and ranking algorithm.
Evaluates routes based on multiple criteria and sorts by overall score.
"""
from typing import List, Dict, Optional
from route_models import Route
from config import Config


class RouteScorer:
    """
    Scores routes based on user preferences.
    Routes are ranked by a weighted combination of duration, transfers, and walking.
    """

    @staticmethod
    def score_routes(
        routes: List[Route],
        weights: Optional[Dict[str, float]] = None
    ) -> List[Route]:
        """
        Score and sort a list of routes.

        Args:
            routes: List of Route objects to score
            weights: Dictionary with keys 'duration', 'transfers', 'walking' and float weights (sum to 1)
                     If None, uses Config.SCORING_WEIGHTS

        Returns:
            New list of Route objects with scores set, sorted by score (highest first)
        """
        if not routes:
            return []

        if weights is None:
            weights = Config.SCORING_WEIGHTS

        # Validate weights sum to ~1.0
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

        # Extract raw metrics for normalization
        durations = [r.total_duration_seconds for r in routes]
        transfers = [r.num_transfers for r in routes]
        walking_times = [
            sum(step.duration_seconds for step in r.steps if step.transport_mode == 'walking')
            for r in routes
        ]

        # Normalize each metric to 0-1 scale (0 = worst, 1 = best)
        for route in routes:
            walking_time = sum(step.duration_seconds for step in route.steps if step.transport_mode == 'walking')

            norm_duration = RouteScorer._normalize(route.total_duration_seconds, durations)
            norm_transfers = RouteScorer._normalize(route.num_transfers, transfers)
            norm_walking = RouteScorer._normalize(walking_time, walking_times)

            # Weighted sum (subtract from 1 because lower is better for raw metrics)
            # Higher score = better route
            route.score = (
                (1 - norm_duration) * weights['duration'] +
                (1 - norm_transfers) * weights['transfers'] +
                (1 - norm_walking) * weights['walking']
            )

        # Sort by score descending
        sorted_routes = sorted(routes, key=lambda r: r.score, reverse=True)

        return sorted_routes

    @staticmethod
    def _normalize(value: float, values: List[float]) -> float:
        """
        Min-max normalize a value to 0-1 range.

        Args:
            value: Value to normalize
            values: List of all values for min/max calculation

        Returns:
            Normalized value between 0 and 1
        """
        if not values:
            return 0.0

        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return 0.0  # All values equal, treat as worst case

        return (value - min_val) / (max_val - min_val)

    @staticmethod
    def get_ranking_explanation(route: Route) -> str:
        """
        Generate a human-readable explanation of why a route got its score.

        Args:
            route: The scored Route object

        Returns:
            String explaining the route's ranking
        """
        walking_time = sum(step.duration_seconds for step in route.steps if step.transport_mode == 'walking') // 60

        factors = []
        if route.num_transfers == 0:
            factors.append("no transfers")
        elif route.num_transfers == 1:
            factors.append("1 transfer")
        else:
            factors.append(f"{route.num_transfers} transfers")

        if walking_time < 5:
            factors.append("minimal walking")
        elif walking_time < 10:
            factors.append(f"{walking_time} min walking")
        else:
            factors.append(f"significant walking ({walking_time} min)")

        return f"Ranked by: {', '.join(factors)}"