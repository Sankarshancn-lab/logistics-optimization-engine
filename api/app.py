from dataclasses import dataclass
import logging

from fastapi import Depends, FastAPI, HTTPException, Request

from logistics_engine.api.schemas import (
    HealthResponse,
    RouteRequest,
    RouteResponse,
)
from logistics_engine.dashboard.data import load_dashboard_data
from logistics_engine.graph import Graph
from logistics_engine.models import Location, Road
from logistics_engine.routing import a_star


logger = logging.getLogger(__name__)


api_app = FastAPI(
    title="Intelligent Logistics Routing Engine",
    description=(
        "Production-oriented logistics routing API using "
        "the validated A* routing engine."
    ),
    version="1.0.0",
)


@dataclass(frozen=True)
class RoutingDataset:
    locations: list[Location]
    roads: list[Road]


def configure_routing_data(
    app: FastAPI,
    locations: list[Location],
    roads: list[Road],
) -> None:
    """
    Configure the routing dataset used by the API.
    """

    app.state.routing_data = RoutingDataset(
        locations=list(locations),
        roads=list(roads),
    )


def get_routing_data(
    request: Request,
) -> RoutingDataset:
    """
    Retrieve the configured routing dataset.
    """

    dataset = getattr(
        request.app.state,
        "routing_data",
        None,
    )

    if dataset is None:
        raise HTTPException(
            status_code=503,
            detail="Routing data is not configured.",
        )

    return dataset


@api_app.on_event("startup")
def initialize_routing_data() -> None:
    """
    Load the project's existing routing data
    when the API starts.
    """

    try:
        data = load_dashboard_data()

        configure_routing_data(
            api_app,
            data.locations,
            data.roads,
        )

        logger.info(
            "Routing data initialized successfully: "
            "%d locations, %d roads.",
            len(data.locations),
            len(data.roads),
        )

    except Exception:
        logger.exception(
            "Failed to initialize routing data."
        )
        raise


def create_route_graph(
    roads: list[Road],
) -> Graph:
    """
    Build the routing graph from road records.
    """

    graph = Graph()

    for road in roads:
        graph.add_edge(
            road.source,
            road.destination,
            road.distance,
            bidirectional=True,
        )

    return graph


def calculate_route_for_data(
    request: RouteRequest,
    locations: list[Location],
    roads: list[Road],
) -> RouteResponse:
    """
    Calculate an optimal route using the supplied
    routing dataset.
    """

    if request.source < 0 or request.source >= len(locations):
        raise HTTPException(
            status_code=400,
            detail="Invalid source node.",
        )

    if (
        request.destination < 0
        or request.destination >= len(locations)
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid destination node.",
        )

    api_graph = create_route_graph(
        roads
    )

    routing_nodes = set(
        api_graph.nodes()
    )

    if request.source not in routing_nodes:
        raise HTTPException(
            status_code=400,
            detail="Invalid source node.",
        )

    if request.destination not in routing_nodes:
        raise HTTPException(
            status_code=400,
            detail="Invalid destination node.",
        )

    logger.info(
        "Route request: %s -> %s",
        request.source,
        request.destination,
    )

    result = a_star(
        api_graph,
        locations,
        request.source,
        request.destination,
    )

    if result is None:
        logger.warning(
            "No route found: %s -> %s",
            request.source,
            request.destination,
        )

        raise HTTPException(
            status_code=404,
            detail="No route found.",
        )

    response = RouteResponse(
        source=request.source,
        destination=request.destination,
        distance=float(result.distance),
        path=[
            int(node)
            for node in result.path
        ],
        nodes_explored=int(
            result.nodes_explored
        ),
        heap_operations=int(
            result.heap_operations
        ),
    )

    logger.info(
        "Route calculated successfully: "
        "%s -> %s | distance=%.6f | nodes=%d",
        request.source,
        request.destination,
        response.distance,
        response.nodes_explored,
    )

    return response


@api_app.get(
    "/health",
    response_model=HealthResponse,
    summary="API health check",
    description=(
        "Returns API availability and the current "
        "routing-data status."
    ),
)
def health_check(
    request: Request,
) -> HealthResponse:
    """
    Return API and routing-data health information.
    """

    dataset = getattr(
        request.app.state,
        "routing_data",
        None,
    )

    if dataset is None:
        return HealthResponse(
            status="degraded",
            routing_data_configured=False,
            locations=0,
            roads=0,
            routing_nodes=0,
        )

    routing_graph = create_route_graph(
        dataset.roads
    )

    routing_nodes = len(
        routing_graph.nodes()
    )

    return HealthResponse(
        status="healthy",
        routing_data_configured=True,
        locations=len(dataset.locations),
        roads=len(dataset.roads),
        routing_nodes=routing_nodes,
    )


@api_app.post(
    "/route",
    response_model=RouteResponse,
    summary="Calculate optimal route",
    description=(
        "Calculate a route between two nodes using "
        "the validated A* routing engine."
    ),
    responses={
        400: {
            "description": (
                "Invalid source or destination node."
            )
        },
        404: {
            "description": "No route exists between the nodes."
        },
        503: {
            "description": "Routing data is not configured."
        },
    },
)
def calculate_route(
    request: RouteRequest,
    dataset: RoutingDataset = Depends(
        get_routing_data
    ),
) -> RouteResponse:
    """
    Calculate an optimal route between two nodes.
    """

    return calculate_route_for_data(
        request,
        dataset.locations,
        dataset.roads,
    )