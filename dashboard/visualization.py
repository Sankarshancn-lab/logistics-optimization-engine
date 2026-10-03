"""Interactive visualizations for the logistics dashboard."""

import plotly.graph_objects as go


def build_network_figure(
    locations,
    roads,
    route_path=None,
):
    """Build an interactive logistics network graph.

    Parameters
    ----------
    locations:
        Location records containing id, x and y.

    roads:
        Road records containing source and destination.

    route_path:
        Optional ordered list of node IDs representing a calculated route.
    """

    # --------------------------------------------------
    # LOCATION LOOKUP
    # --------------------------------------------------

    location_lookup = {
        int(location.id): location
        for location in locations
    }

    # Normalize route IDs so comparisons are reliable.
    normalized_route = []

    if route_path:
        for node_id in route_path:
            try:
                normalized_route.append(int(node_id))
            except (TypeError, ValueError):
                continue

    route_node_set = set(normalized_route)

    # --------------------------------------------------
    # NETWORK EDGES
    # --------------------------------------------------

    edge_x = []
    edge_y = []

    for road in roads:
        source = location_lookup.get(int(road.source))
        destination = location_lookup.get(int(road.destination))

        if source is None or destination is None:
            continue

        edge_x.extend(
            [
                float(source.x),
                float(destination.x),
                None,
            ]
        )

        edge_y.extend(
            [
                float(source.y),
                float(destination.y),
                None,
            ]
        )

    # --------------------------------------------------
    # NETWORK NODES
    # --------------------------------------------------

    node_x = [
        float(location.x)
        for location in locations
    ]

    node_y = [
        float(location.y)
        for location in locations
    ]

    node_ids = [
        int(location.id)
        for location in locations
    ]

    # --------------------------------------------------
    # FIGURE
    # --------------------------------------------------

    figure = go.Figure()

    # --------------------------------------------------
    # BASE ROAD NETWORK
    # --------------------------------------------------

    figure.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            name="Road Network",
            hoverinfo="skip",
            line=dict(
                width=1,
            ),
        )
    )

    # --------------------------------------------------
    # ALL LOCATIONS
    # --------------------------------------------------

    figure.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            name="Locations",
            text=[
                f"Location {node_id}"
                for node_id in node_ids
            ],
            customdata=node_ids,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "X: %{x:.2f}<br>"
                "Y: %{y:.2f}"
                "<extra></extra>"
            ),
            marker=dict(
                size=7,
            ),
        )
    )

    # --------------------------------------------------
    # SELECTED ROUTE
    # --------------------------------------------------

    if len(normalized_route) >= 2:

        route_x = []
        route_y = []
        valid_route_nodes = []

        for node_id in normalized_route:

            location = location_lookup.get(node_id)

            if location is None:
                continue

            route_x.append(float(location.x))
            route_y.append(float(location.y))
            valid_route_nodes.append(node_id)

        # --------------------------------------------------
        # ROUTE LINE
        # --------------------------------------------------

        if len(route_x) >= 2:

            route_text = [
                (
                    f"Route position: {index + 1}<br>"
                    f"Node ID: {node_id}"
                )
                for index, node_id
                in enumerate(valid_route_nodes)
            ]

            figure.add_trace(
                go.Scatter(
                    x=route_x,
                    y=route_y,
                    mode="lines+markers",
                    name="Selected Route",
                    text=route_text,
                    hovertemplate=(
                        "<b>%{text}</b>"
                        "<extra></extra>"
                    ),
                    line=dict(
                        width=5,
                    ),
                    marker=dict(
                        size=9,
                    ),
                )
            )

        # --------------------------------------------------
        # ORIGIN NODE
        # --------------------------------------------------

        origin_id = valid_route_nodes[0]

        origin_location = location_lookup.get(origin_id)

        if origin_location is not None:

            figure.add_trace(
                go.Scatter(
                    x=[float(origin_location.x)],
                    y=[float(origin_location.y)],
                    mode="markers+text",
                    name="Origin",
                    text=["ORIGIN"],
                    textposition="top center",
                    hovertemplate=(
                        "<b>Origin</b><br>"
                        f"Node ID: {origin_id}"
                        "<extra></extra>"
                    ),
                    marker=dict(
                        size=16,
                        symbol="circle",
                    ),
                )
            )

        # --------------------------------------------------
        # DESTINATION NODE
        # --------------------------------------------------

        destination_id = valid_route_nodes[-1]

        destination_location = location_lookup.get(
            destination_id
        )

        if destination_location is not None:

            figure.add_trace(
                go.Scatter(
                    x=[float(destination_location.x)],
                    y=[float(destination_location.y)],
                    mode="markers+text",
                    name="Destination",
                    text=["DESTINATION"],
                    textposition="top center",
                    hovertemplate=(
                        "<b>Destination</b><br>"
                        f"Node ID: {destination_id}"
                        "<extra></extra>"
                    ),
                    marker=dict(
                        size=16,
                        symbol="diamond",
                    ),
                )
            )

        # --------------------------------------------------
        # INTERMEDIATE ROUTE NODES
        # --------------------------------------------------

        if len(valid_route_nodes) > 2:

            intermediate_ids = valid_route_nodes[1:-1]

            intermediate_x = []
            intermediate_y = []
            intermediate_text = []

            for position, node_id in enumerate(
                intermediate_ids,
                start=2,
            ):

                location = location_lookup.get(node_id)

                if location is None:
                    continue

                intermediate_x.append(
                    float(location.x)
                )

                intermediate_y.append(
                    float(location.y)
                )

                intermediate_text.append(
                    (
                        f"<b>Route Stop {position}</b><br>"
                        f"Node ID: {node_id}<br>"
                        f"Route position: {position}"
                    )
                )

            if intermediate_x:

                figure.add_trace(
                    go.Scatter(
                        x=intermediate_x,
                        y=intermediate_y,
                        mode="markers",
                        name="Route Stops",
                        hovertemplate=(
                            "%{text}"
                            "<extra></extra>"
                        ),
                        text=intermediate_text,
                        marker=dict(
                            size=11,
                        ),
                    )
                )

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    figure.update_layout(
        title="Logistics Network & Selected Route",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        hovermode="closest",
        height=650,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(
            l=20,
            r=20,
            t=80,
            b=20,
        ),
    )

    # --------------------------------------------------
    # AXIS SETTINGS
    # --------------------------------------------------

    figure.update_xaxes(
        showgrid=True,
        zeroline=False,
    )

    figure.update_yaxes(
        showgrid=True,
        zeroline=False,
        scaleanchor="x",
        scaleratio=1,
    )

    return figure