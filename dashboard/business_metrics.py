"""Business-oriented KPIs for logistics operations."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class BusinessMetrics:
    location_count: int
    road_count: int
    stored_route_count: int
    optimization_run_count: int
    total_network_distance: float
    average_road_distance: float
    average_optimization_runtime: float
    average_optimization_objective: float
    optimization_success_rate: float


def calculate_business_metrics(
    locations: Sequence,
    roads: Sequence,
    routes: Sequence,
    optimization_results: Sequence,
) -> BusinessMetrics:
    """Calculate executive-level logistics KPIs."""

    location_count = len(locations)
    road_count = len(roads)
    stored_route_count = len(routes)
    optimization_run_count = len(optimization_results)

    total_network_distance = sum(
        float(road.distance)
        for road in roads
    )

    average_road_distance = (
        total_network_distance / road_count
        if road_count
        else 0.0
    )

    average_optimization_runtime = (
        sum(
            float(result.runtime_seconds)
            for result in optimization_results
        )
        / optimization_run_count
        if optimization_run_count
        else 0.0
    )

    average_optimization_objective = (
        sum(
            float(result.objective_value)
            for result in optimization_results
        )
        / optimization_run_count
        if optimization_run_count
        else 0.0
    )

    if optimization_run_count:

        successful_runs = sum(
            1
            for result in optimization_results
            if str(result.status).lower()
            in {"success", "optimal", "completed", "pass"}
        )

        optimization_success_rate = (
            successful_runs
            / optimization_run_count
            * 100.0
        )

    else:
        optimization_success_rate = 0.0

    return BusinessMetrics(
        location_count=location_count,
        road_count=road_count,
        stored_route_count=stored_route_count,
        optimization_run_count=optimization_run_count,
        total_network_distance=total_network_distance,
        average_road_distance=average_road_distance,
        average_optimization_runtime=average_optimization_runtime,
        average_optimization_objective=average_optimization_objective,
        optimization_success_rate=optimization_success_rate,
    )
