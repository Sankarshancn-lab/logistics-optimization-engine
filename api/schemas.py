from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    """
    Request payload for route calculation.
    """

    source: int = Field(
        ...,
        ge=0,
        description="Source node ID in the routing network.",
        examples=[0],
    )

    destination: int = Field(
        ...,
        ge=0,
        description="Destination node ID in the routing network.",
        examples=[3],
    )


class RouteResponse(BaseModel):
    """
    Successful route calculation response.
    """

    source: int = Field(
        ...,
        description="Source node ID.",
        examples=[0],
    )

    destination: int = Field(
        ...,
        description="Destination node ID.",
        examples=[3],
    )

    distance: float = Field(
        ...,
        description="Total route distance.",
        examples=[26.02288393382464],
    )

    path: list[int] = Field(
        ...,
        description="Ordered list of node IDs forming the selected route.",
        examples=[[0, 4, 3]],
    )

    nodes_explored: int = Field(
        ...,
        ge=0,
        description="Number of graph nodes explored by the routing algorithm.",
        examples=[8],
    )

    heap_operations: int = Field(
        ...,
        ge=0,
        description="Number of priority-queue heap operations performed.",
        examples=[12],
    )


class HealthResponse(BaseModel):
    """
    API health and routing-data status.
    """

    status: str = Field(
        ...,
        description="Current API status.",
        examples=["healthy"],
    )

    routing_data_configured: bool = Field(
        ...,
        description="Whether routing data is currently loaded.",
        examples=[True],
    )

    locations: int = Field(
        ...,
        ge=0,
        description="Number of loaded location records.",
        examples=[10000],
    )

    roads: int = Field(
        ...,
        ge=0,
        description="Number of loaded road records.",
        examples=[157],
    )

    routing_nodes: int = Field(
        ...,
        ge=0,
        description="Number of nodes represented in the routing graph.",
        examples=[50],
    )