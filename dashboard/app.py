"""Interactive Streamlit dashboard for the logistics engine."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from logistics_engine.dashboard.business_metrics import (
    calculate_business_metrics,
)

from logistics_engine.dashboard.data import (
    load_dashboard_data,
)

from logistics_engine.dashboard.metrics import (
    calculate_route_metrics,
)

from logistics_engine.dashboard.routing_analytics import (
    compare_routing_algorithms,
)

from logistics_engine.dashboard.visualization import (
    build_network_figure,
)

from logistics_engine.dashboard.validation import (
    render_system_validation,
)

from logistics_engine.graph import Graph

from logistics_engine.routing import a_star


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Logistics Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stMetric"] {
            background-color: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.15);
            padding: 18px;
            border-radius: 12px;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DASHBOARD DATA
# ============================================================

@st.cache_data
def get_dashboard_data():
    """Load dashboard data from the database."""

    return load_dashboard_data()


data = get_dashboard_data()


# ============================================================
# BUSINESS METRICS
# ============================================================

business_metrics = calculate_business_metrics(
    data.locations,
    data.roads,
    data.routes,
    data.optimization_results,
)


# ============================================================
# CREATE ROUTING GRAPH
# ============================================================

def create_graph(roads):
    """
    Create a routing graph from database road records.
    """

    graph = Graph()

    for road in roads:

        source = int(road.source)
        destination = int(road.destination)
        distance = float(road.distance)

        graph.add_edge(
            source,
            destination,
            distance,
            bidirectional=True,
        )

    return graph


routing_graph = create_graph(data.roads)


# ============================================================
# GET VALID ROUTING NODES
# ============================================================

def get_routing_node_ids(graph):
    """
    Return only nodes that actually exist in the routing graph.

    This deliberately does NOT use all database locations because
    a location may exist in the database without being connected
    to any road in the routing graph.

    Supports both:
        graph.nodes
    and:
        graph.nodes()
    """

    nodes = graph.nodes

    if callable(nodes):
        nodes = nodes()

    return sorted(
        int(node_id)
        for node_id in nodes
    )


routing_node_ids = get_routing_node_ids(
    routing_graph
)


# ============================================================
# NETWORK INTELLIGENCE
# ============================================================

def calculate_network_intelligence(
    locations,
    roads,
):
    """
    Calculate basic network statistics.
    """

    location_count = len(locations)
    road_count = len(roads)

    degree = {
        int(location.id): 0
        for location in locations
    }

    total_distance = 0.0

    for road in roads:

        source = int(road.source)
        destination = int(road.destination)
        distance = float(road.distance)

        degree[source] = (
            degree.get(source, 0) + 1
        )

        degree[destination] = (
            degree.get(destination, 0) + 1
        )

        total_distance += distance

    connected_location_count = sum(
        1
        for value in degree.values()
        if value > 0
    )

    if location_count > 0:

        average_degree = (
            sum(degree.values())
            / location_count
        )

    else:

        average_degree = 0.0

    maximum_degree = (
        max(degree.values())
        if degree
        else 0
    )

    if location_count > 0:

        connectivity_rate = (
            connected_location_count
            / location_count
            * 100
        )

    else:

        connectivity_rate = 0.0

    top_connected = sorted(
        degree.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    return {
        "location_count": location_count,
        "road_count": road_count,
        "connected_location_count": (
            connected_location_count
        ),
        "routing_node_count": len(
            routing_node_ids
        ),
        "average_degree": average_degree,
        "maximum_degree": maximum_degree,
        "connectivity_rate": connectivity_rate,
        "total_distance": total_distance,
        "top_connected": top_connected,
    }


network_info = calculate_network_intelligence(
    data.locations,
    data.roads,
)


# ============================================================
# SESSION STATE
# ============================================================

if "route_result" not in st.session_state:
    st.session_state.route_result = None

if "route_source" not in st.session_state:
    st.session_state.route_source = None

if "route_destination" not in st.session_state:
    st.session_state.route_destination = None

if "analytics_result" not in st.session_state:
    st.session_state.analytics_result = None

if "network_loaded" not in st.session_state:
    st.session_state.network_loaded = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🚚 Logistics Intelligence")

    st.caption(
        "Routing & Optimization Engine"
    )

    st.divider()

    st.subheader("Navigation")

    page = st.radio(
        "Select Section",
        [
            "Overview",
            "Route Planner",
            "Network Intelligence",
            "Algorithm Analytics",
            "Optimization",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.success("● SYSTEM ONLINE")

    st.write("Database Connected")
    st.write("Routing Engine Ready")
    st.write("Optimization Ready")

    st.divider()

    st.caption(
        "Intelligent Logistics Routing & "
        "Optimization Engine"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "🚚 Intelligent Logistics Routing & Optimization Engine"
)

st.caption(
    "Production-oriented routing, optimization, "
    "algorithm analytics, network intelligence, "
    "and logistics decision support."
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.header("Executive Overview")

    st.write(
        "Business and network indicators backed by "
        "the logistics database."
    )

    # --------------------------------------------------------
    # PRIMARY KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Locations",
        f"{business_metrics.location_count:,}",
    )

    col2.metric(
        "Roads",
        f"{business_metrics.road_count:,}",
    )

    col3.metric(
        "Stored Routes",
        f"{business_metrics.stored_route_count:,}",
    )

    col4.metric(
        "Optimization Runs",
        f"{business_metrics.optimization_run_count:,}",
    )

    # --------------------------------------------------------
    # NETWORK PERFORMANCE
    # --------------------------------------------------------

    st.subheader("Network Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Network Distance",
        f"{business_metrics.total_network_distance:,.2f}",
    )

    col2.metric(
        "Average Road Distance",
        f"{business_metrics.average_road_distance:,.2f}",
    )

    col3.metric(
        "Avg Optimization Runtime",
        f"{business_metrics.average_optimization_runtime:.6f}s",
    )

    col4.metric(
        "Optimization Success",
        f"{business_metrics.optimization_success_rate:.1f}%",
    )

    # --------------------------------------------------------
    # NETWORK HEALTH
    # --------------------------------------------------------

    st.subheader("Network Health")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Connected Locations",
        f"{network_info['connected_location_count']:,}",
    )

    col2.metric(
        "Routing Nodes",
        f"{network_info['routing_node_count']:,}",
    )

    col3.metric(
        "Average Degree",
        f"{network_info['average_degree']:.2f}",
    )

    col4.metric(
        "Maximum Degree",
        f"{network_info['maximum_degree']:,}",
    )

    st.success(
        "Dashboard data loaded successfully."
    )


# ============================================================
# ROUTE PLANNER
# ============================================================

elif page == "Route Planner":

    st.header("Route Planner")

    st.write(
        "Calculate and inspect the shortest path between "
        "two connected logistics locations."
    )

    # --------------------------------------------------------
    # ROUTING NODE VALIDATION
    # --------------------------------------------------------

    if len(routing_node_ids) < 2:

        st.error(
            "The routing graph contains fewer than two "
            "usable nodes."
        )

        st.stop()

    st.info(
        f"{len(routing_node_ids):,} locations are currently "
        "available as routing endpoints."
    )

    # --------------------------------------------------------
    # LOCATION SELECTION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        route_source = st.selectbox(
            "Origin Location",
            routing_node_ids,
            index=0,
        )

    with col2:

        route_destination = st.selectbox(
            "Destination Location",
            routing_node_ids,
            index=1,
        )

    # --------------------------------------------------------
    # CALCULATE ROUTE
    # --------------------------------------------------------

    if st.button(
        "⚡ Find Optimal Route",
        type="primary",
        width="stretch",
    ):

        if route_source == route_destination:

            st.error(
                "Origin and destination must be different."
            )

            st.session_state.route_result = None
            st.session_state.analytics_result = None

        elif not routing_graph.has_node(
            route_source
        ):

            st.error(
                f"Origin node {route_source} "
                "does not exist in the routing graph."
            )

            st.session_state.route_result = None

        elif not routing_graph.has_node(
            route_destination
        ):

            st.error(
                f"Destination node {route_destination} "
                "does not exist in the routing graph."
            )

            st.session_state.route_result = None

        else:

            try:

                result = a_star(
                    routing_graph,
                    data.locations,
                    route_source,
                    route_destination,
                    heuristic="zero",
                )

                if result is None:

                    st.warning(
                        "Both locations exist in the routing "
                        "graph, but no path exists between them."
                    )

                    st.session_state.route_result = None
                    st.session_state.analytics_result = None

                else:

                    st.session_state.route_result = result

                    st.session_state.route_source = (
                        route_source
                    )

                    st.session_state.route_destination = (
                        route_destination
                    )

                    st.session_state.analytics_result = None

                    st.success(
                        "Optimal route calculated successfully."
                    )

            except Exception as exc:

                st.error(
                    f"Route calculation failed: {exc}"
                )

                st.session_state.route_result = None
                st.session_state.analytics_result = None

    route_result = st.session_state.route_result

    # ========================================================
    # ROUTE RESULTS
    # ========================================================

    if route_result is not None:

        st.divider()

        st.header("Route Results")

        # ----------------------------------------------------
        # ROUTE KPIs
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Route Distance",
            f"{route_result.distance:,.2f}",
        )

        col2.metric(
            "Path Nodes",
            f"{len(route_result.path):,}",
        )

        col3.metric(
            "Nodes Explored",
            f"{route_result.nodes_explored:,}",
        )

        col4.metric(
            "Heap Operations",
            f"{route_result.heap_operations:,}",
        )

        # ----------------------------------------------------
        # SELECTED PATH
        # ----------------------------------------------------

        st.subheader("Selected Path")

        path_text = " → ".join(
            str(node)
            for node in route_result.path
        )

        st.code(
            path_text,
            language="text",
        )

        # ----------------------------------------------------
        # ROUTE METRICS
        # ----------------------------------------------------

        st.subheader("Route Metrics")

        route_metrics = calculate_route_metrics(
            st.session_state.route_source,
            st.session_state.route_destination,
            route_result.distance,
            route_result.path,
            route_result.nodes_explored,
            route_result.heap_operations,
        )

        if hasattr(
            route_metrics,
            "__dict__",
        ):

            metrics_dict = route_metrics.__dict__

        else:

            metrics_dict = route_metrics

        st.json(metrics_dict)

        # ----------------------------------------------------
        # ROUTE LEG INTELLIGENCE — M32.5
        # ----------------------------------------------------

        st.divider()

        st.subheader("Route Leg Intelligence")

        path = list(route_result.path)

        if len(path) >= 2:

            leg_rows = []

            cumulative_distance = 0.0
            cumulative_travel_time = 0.0

            # Build a road lookup from the database.
            # The routing graph is bidirectional, so both
            # directions are supported.
            road_lookup = {}

            for road in data.roads:

                source = int(road.source)
                destination = int(road.destination)

                road_lookup[(source, destination)] = road
                road_lookup[(destination, source)] = road

            missing_legs = []

            # Project-level fallback speed used only when the
            # road record does not contain travel-time data.
            average_speed = 40.0

            for leg_number, (from_node, to_node) in enumerate(
                zip(path, path[1:]),
                start=1,
            ):

                from_node = int(from_node)
                to_node = int(to_node)

                road = road_lookup.get(
                    (from_node, to_node)
                )

                if road is None:

                    missing_legs.append(
                        f"{from_node} → {to_node}"
                    )

                    continue

                leg_distance = float(
                    road.distance
                )

                cumulative_distance += (
                    leg_distance
                )

                if route_result.distance > 0:

                    route_percentage = (
                        leg_distance
                        / route_result.distance
                        * 100
                    )

                else:

                    route_percentage = 0.0

                # Use stored travel-time data when the road model
                # provides it. Otherwise use the existing project
                # estimate of 40 distance-units/hour.
                stored_travel_time = getattr(
                    road,
                    "travel_time",
                    None,
                )

                if stored_travel_time is not None:

                    try:

                        leg_travel_time = float(
                            stored_travel_time
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        leg_travel_time = (
                            leg_distance
                            / average_speed
                            * 60
                        )

                else:

                    leg_travel_time = (
                        leg_distance
                        / average_speed
                        * 60
                    )

                cumulative_travel_time += (
                    leg_travel_time
                )

                leg_rows.append(
                    {
                        "Leg": leg_number,
                        "From": from_node,
                        "To": to_node,
                        "Leg Distance": round(
                            leg_distance,
                            4,
                        ),
                        "Cumulative Distance": round(
                            cumulative_distance,
                            4,
                        ),
                        "Route Share (%)": round(
                            route_percentage,
                            2,
                        ),
                        "Travel Time (min)": round(
                            leg_travel_time,
                            2,
                        ),
                        "Cumulative Travel Time (min)": round(
                            cumulative_travel_time,
                            2,
                        ),
                    }
                )

            if missing_legs:

                st.warning(
                    "Some route legs could not be matched "
                    "to database road records: "
                    + ", ".join(missing_legs)
                )

            if leg_rows:

                # --------------------------------------------
                # LEG SUMMARY
                # --------------------------------------------

                total_legs = len(leg_rows)

                longest_leg = max(
                    leg_rows,
                    key=lambda row: row["Leg Distance"],
                )

                shortest_leg = min(
                    leg_rows,
                    key=lambda row: row["Leg Distance"],
                )

                # Use the full-precision cumulative distance rather than
                # summing the display-rounded leg values.
                # This prevents false precision warnings caused by rounding
                # each displayed leg distance to four decimal places.
                total_leg_distance = cumulative_distance

                total_travel_time = sum(
                    row["Travel Time (min)"]
                    for row in leg_rows
                )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Total Legs",
                    f"{total_legs:,}",
                )

                col2.metric(
                    "Longest Leg",
                    f"{longest_leg['Leg Distance']:.2f}",
                )

                col3.metric(
                    "Shortest Leg",
                    f"{shortest_leg['Leg Distance']:.2f}",
                )

                col4.metric(
                    "Total Travel Time",
                    f"{total_travel_time:.1f} min",
                )

                # --------------------------------------------
                # LEG BREAKDOWN
                # --------------------------------------------

                st.subheader("Route Leg Breakdown")

                st.dataframe(
                    leg_rows,
                    width="stretch",
                    hide_index=True,
                )

                # --------------------------------------------
                # ROUTE CONSISTENCY
                # --------------------------------------------

                st.subheader("Route Consistency Check")

                distance_difference = abs(
                    total_leg_distance
                    - route_result.distance
                )

                if distance_difference < 1e-6:

                    st.success(
                        "Route consistency verified: "
                        "individual road-leg distances match "
                        "the calculated route distance."
                    )

                else:

                    st.warning(
                        "A distance difference was detected "
                        f"between the route result and leg breakdown: "
                        f"{distance_difference:.6f}"
                    )

                # --------------------------------------------
                # ROUTE BREAKDOWN
                # --------------------------------------------

                st.subheader("Route Breakdown")

                time_source = (
                    "stored road travel-time data"
                    if any(
                        getattr(
                            road_lookup.get(
                                (
                                    int(row["From"]),
                                    int(row["To"]),
                                )
                            ),
                            "travel_time",
                            None,
                        )
                        is not None
                        for row in leg_rows
                    )
                    else
                    f"estimated at {average_speed:.0f} "
                    "distance-units/hour"
                )

                st.write(
                    f"""
                    The calculated route contains **{total_legs}**
                    road legs covering a total distance of
                    **{route_result.distance:.2f}**.

                    The longest individual leg is between nodes
                    **{longest_leg['From']} → {longest_leg['To']}**
                    with a distance of
                    **{longest_leg['Leg Distance']:.2f}**.

                    Total travel time is approximately
                    **{total_travel_time:.1f} minutes**, based on
                    **{time_source}**.
                    """
                )

            else:

                st.info(
                    "No individual road legs are available "
                    "for this route."
                )

        else:

            st.info(
                "The calculated route contains fewer than "
                "two nodes, so leg analysis is not available."
            )

        # ----------------------------------------------------
        # ROUTE PERFORMANCE & DECISION INTELLIGENCE — M32.7
        # ----------------------------------------------------

        st.divider()

        st.subheader("Route Performance & Decision Intelligence")

        # Reuse the calculated route result and build a compact
        # operational view without changing the routing algorithm.
        performance_path = [
            int(node_id)
            for node_id in route_result.path
        ]

        performance_legs = []
        performance_distance = 0.0
        performance_travel_time = 0.0

        performance_road_lookup = {}

        for road in data.roads:

            road_source = int(road.source)
            road_destination = int(road.destination)

            performance_road_lookup[
                (road_source, road_destination)
            ] = road

            performance_road_lookup[
                (road_destination, road_source)
            ] = road

        performance_average_speed = 40.0

        for from_node, to_node in zip(
            performance_path,
            performance_path[1:],
        ):

            road = performance_road_lookup.get(
                (from_node, to_node)
            )

            if road is None:
                continue

            leg_distance = float(road.distance)

            stored_travel_time = getattr(
                road,
                "travel_time",
                None,
            )

            if stored_travel_time is not None:

                try:
                    leg_time = float(stored_travel_time)
                except (TypeError, ValueError):
                    leg_time = (
                        leg_distance
                        / performance_average_speed
                        * 60
                    )

            else:
                leg_time = (
                    leg_distance
                    / performance_average_speed
                    * 60
                )

            performance_distance += leg_distance
            performance_travel_time += leg_time

            performance_legs.append(
                {
                    "from": from_node,
                    "to": to_node,
                    "distance": leg_distance,
                    "travel_time": leg_time,
                }
            )

        # Prefer the verified route distance from A* when available.
        # The leg total is used as an independent operational check.
        route_distance = float(route_result.distance)

        route_nodes = len(performance_path)
        total_legs = max(route_nodes - 1, 0)

        average_leg_distance = (
            performance_distance / len(performance_legs)
            if performance_legs
            else 0.0
        )

        longest_leg_distance = (
            max(
                leg["distance"]
                for leg in performance_legs
            )
            if performance_legs
            else 0.0
        )

        # Percentage of routing nodes examined by A*.
        # This is a descriptive search metric, not a quality score.
        routing_node_count = len(routing_node_ids)

        exploration_rate = (
            route_result.nodes_explored
            / routing_node_count
            * 100
            if routing_node_count > 0
            else 0.0
        )

        distance_difference = abs(
            performance_distance - route_distance
        )

        # ----------------------------------------------------
        # PERFORMANCE KPIs
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Distance",
            f"{route_distance:,.2f}",
        )

        col2.metric(
            "Travel Time",
            f"{performance_travel_time:,.1f} min",
        )

        col3.metric(
            "Route Stops",
            f"{route_nodes:,}",
        )

        col4.metric(
            "Nodes Explored",
            f"{route_result.nodes_explored:,}",
        )

        # ----------------------------------------------------
        # OPERATIONAL METRICS
        # ----------------------------------------------------

        st.subheader("Operational Metrics")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Legs",
            f"{total_legs:,}",
        )

        col2.metric(
            "Average Leg",
            f"{average_leg_distance:,.2f}",
        )

        col3.metric(
            "Longest Leg",
            f"{longest_leg_distance:,.2f}",
        )

        col4.metric(
            "Network Explored",
            f"{exploration_rate:.2f}%",
        )

        # ----------------------------------------------------
        # ROUTE VALIDATION
        # ----------------------------------------------------

        st.subheader("Route Validation")

        validation_col1, validation_col2 = st.columns(2)

        with validation_col1:

            if performance_legs:

                st.success(
                    "Route legs successfully mapped to the "
                    "network road records."
                )

            else:

                st.warning(
                    "No matching road records were found for "
                    "the calculated route."
                )

        with validation_col2:

            if distance_difference < 1e-6:

                st.success(
                    "A* distance and road-leg distance are consistent."
                )

            else:

                st.warning(
                    "A difference exists between the A* route "
                    f"distance and road-leg total: {distance_difference:.6f}."
                )

        # ----------------------------------------------------
        # DECISION SUMMARY
        # ----------------------------------------------------

        st.subheader("Operational Route Summary")

        origin_node = performance_path[0] if performance_path else "N/A"
        destination_node = (
            performance_path[-1]
            if performance_path
            else "N/A"
        )

        st.write(
            f"""
            The selected route runs from **Node {origin_node}** to
            **Node {destination_node}** across **{total_legs} road legs**.
            The calculated distance is **{route_distance:.2f}** with an
            estimated travel time of **{performance_travel_time:.1f} minutes**.

            A* examined **{route_result.nodes_explored:,}** routing nodes,
            representing **{exploration_rate:.2f}%** of the available routing
            network. The route contains **{route_nodes:,} path nodes** and an
            average leg distance of **{average_leg_distance:.2f}**.
            """
        )
        # ----------------------------------------------------
        # ROUTE RISK & BOTTLENECK INTELLIGENCE — M32.8
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "Route Risk & Bottleneck Intelligence"
        )

        st.caption(
            "Identifies route segments that contribute unusually large "
            "shares of distance or travel time. These are operational "
            "attention indicators, not live traffic or congestion measurements."
        )

        # ----------------------------------------------------
        # SEGMENT CONTRIBUTION ANALYSIS
        # ----------------------------------------------------

        segment_rows = []

        if performance_legs:

            expected_distance_share = (
                100.0 / len(performance_legs)
            )

            expected_time_share = (
                100.0 / len(performance_legs)
            )

            distance_attention_threshold = max(
                25.0,
                expected_distance_share * 1.5,
            )

            time_attention_threshold = max(
                25.0,
                expected_time_share * 1.5,
            )

            for leg_number, leg in enumerate(
                performance_legs,
                start=1,
            ):

                distance_share = (
                    leg["distance"]
                    / performance_distance
                    * 100
                    if performance_distance > 0
                    else 0.0
                )

                time_share = (
                    leg["travel_time"]
                    / performance_travel_time
                    * 100
                    if performance_travel_time > 0
                    else 0.0
                )

                attention_reasons = []

                if distance_share >= distance_attention_threshold:
                    attention_reasons.append(
                        "High distance contribution"
                    )

                if time_share >= time_attention_threshold:
                    attention_reasons.append(
                        "High travel-time contribution"
                    )

                if attention_reasons:
                    attention_level = "Attention"
                    reason = "; ".join(attention_reasons)
                else:
                    attention_level = "Normal"
                    reason = "Within route contribution threshold"

                segment_rows.append(
                    {
                        "Leg": leg_number,
                        "From": leg["from"],
                        "To": leg["to"],
                        "Distance": round(
                            leg["distance"],
                            4,
                        ),
                        "Distance Share (%)": round(
                            distance_share,
                            2,
                        ),
                        "Travel Time (min)": round(
                            leg["travel_time"],
                            2,
                        ),
                        "Time Share (%)": round(
                            time_share,
                            2,
                        ),
                        "Attention": attention_level,
                        "Reason": reason,
                    }
                )

            # ------------------------------------------------
            # BOTTLENECK SUMMARY
            # ------------------------------------------------

            attention_segments = [
                row
                for row in segment_rows
                if row["Attention"] == "Attention"
            ]

            highest_distance_segment = max(
                segment_rows,
                key=lambda row: row["Distance Share (%)"],
            )

            highest_time_segment = max(
                segment_rows,
                key=lambda row: row["Time Share (%)"],
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Attention Segments",
                f"{len(attention_segments):,}",
            )

            col2.metric(
                "Largest Distance Share",
                f"{highest_distance_segment['Distance Share (%)']:.2f}%",
            )

            col3.metric(
                "Largest Time Share",
                f"{highest_time_segment['Time Share (%)']:.2f}%",
            )

            # ------------------------------------------------
            # SEGMENT TABLE
            # ------------------------------------------------

            st.subheader("Segment Contribution Analysis")

            st.dataframe(
                segment_rows,
                width="stretch",
                hide_index=True,
            )

            # ------------------------------------------------
            # POTENTIAL BOTTLENECKS
            # ------------------------------------------------

            st.subheader("Potential Bottleneck Segments")

            if attention_segments:

                for row in attention_segments:

                    st.warning(
                        f"Leg {row['Leg']} — Node {row['From']} → "
                        f"Node {row['To']}: "
                        f"{row['Distance Share (%)']:.2f}% of route distance "
                        f"and {row['Time Share (%)']:.2f}% of route travel time. "
                        f"{row['Reason']}."
                    )

            else:

                st.success(
                    "No route segment crossed the defined contribution "
                    "thresholds."
                )

            # ------------------------------------------------
            # ROUTE CONCENTRATION
            # ------------------------------------------------

            distance_sorted = sorted(
                segment_rows,
                key=lambda row: row["Distance Share (%)"],
                reverse=True,
            )

            top_distance_count = max(
                1,
                int(len(distance_sorted) * 0.20),
            )

            top_distance_share = sum(
                row["Distance Share (%)"]
                for row in distance_sorted[:top_distance_count]
            )

            time_sorted = sorted(
                segment_rows,
                key=lambda row: row["Time Share (%)"],
                reverse=True,
            )

            top_time_count = max(
                1,
                int(len(time_sorted) * 0.20),
            )

            top_time_share = sum(
                row["Time Share (%)"]
                for row in time_sorted[:top_time_count]
            )

            st.subheader("Route Concentration")

            col1, col2 = st.columns(2)

            col1.metric(
                "Top Segment Distance Share",
                f"{top_distance_share:.2f}%",
            )

            col2.metric(
                "Top Segment Time Share",
                f"{top_time_share:.2f}%",
            )

            st.write(
                f"The highest-contribution segment is **Node "
                f"{highest_distance_segment['From']} → Node "
                f"{highest_distance_segment['To']}**, accounting for "
                f"**{highest_distance_segment['Distance Share (%)']:.2f}%** "
                f"of the route distance. The largest travel-time contribution "
                f"comes from **Node {highest_time_segment['From']} → Node "
                f"{highest_time_segment['To']}**, accounting for "
                f"**{highest_time_segment['Time Share (%)']:.2f}%** of total "
                f"route travel time."
            )

        else:

            st.info(
                "Route risk and bottleneck analysis requires at least "
                "one mapped road segment."
            )

        # ----------------------------------------------------
        # ROUTE ALTERNATIVES & SCENARIO ANALYSIS — M32.9
        # ----------------------------------------------------

        st.divider()

        st.subheader("Route Alternatives & Scenario Analysis")

        st.caption(
            "Builds a single-edge-avoidance alternative by rerunning "
            "A* while temporarily removing each road segment from the "
            "primary route. This is a scenario analysis, not a full "
            "K-shortest-paths implementation."
        )

        # ----------------------------------------------------
        # ALTERNATIVE ROUTE CALCULATION
        # ----------------------------------------------------

        def calculate_alternative_route(
            roads,
            locations,
            origin,
            destination,
            primary_path,
        ):
            """Find the shortest valid route after avoiding one
            primary-route road segment at a time.

            The original routing graph is never modified. A fresh graph
            is created for each edge-avoidance scenario, which keeps the
            primary routing result and previous milestones unchanged.
            """

            if len(primary_path) < 2:
                return None

            primary_edges = []
            seen_edges = set()

            for from_node, to_node in zip(
                primary_path,
                primary_path[1:],
            ):
                edge_key = tuple(
                    sorted(
                        (
                            int(from_node),
                            int(to_node),
                        )
                    )
                )

                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    primary_edges.append(edge_key)

            candidates = []

            for blocked_edge in primary_edges:

                scenario_graph = Graph()

                for road in roads:

                    road_source = int(road.source)
                    road_destination = int(road.destination)

                    road_edge = tuple(
                        sorted(
                            (
                                road_source,
                                road_destination,
                            )
                        )
                    )

                    if road_edge == blocked_edge:
                        continue

                    scenario_graph.add_edge(
                        road_source,
                        road_destination,
                        float(road.distance),
                        bidirectional=True,
                    )

                if not scenario_graph.has_node(origin):
                    continue

                if not scenario_graph.has_node(destination):
                    continue

                try:
                    scenario_result = a_star(
                        scenario_graph,
                        locations,
                        origin,
                        destination,
                        heuristic="zero",
                    )
                except Exception:
                    scenario_result = None

                if scenario_result is None:
                    continue

                scenario_path = [
                    int(node_id)
                    for node_id in scenario_result.path
                ]

                # The blocked primary edge guarantees that a valid
                # alternative should differ from the primary path.
                if scenario_path == [
                    int(node_id)
                    for node_id in primary_path
                ]:
                    continue

                candidates.append(
                    {
                        "blocked_edge": blocked_edge,
                        "result": scenario_result,
                    }
                )

            if not candidates:
                return None

            return min(
                candidates,
                key=lambda candidate: float(
                    candidate["result"].distance
                ),
            )

        alternative_candidate = calculate_alternative_route(
            data.roads,
            data.locations,
            performance_path[0],
            performance_path[-1],
            performance_path,
        )

        # ----------------------------------------------------
        # SCENARIO RESULT
        # ----------------------------------------------------

        if alternative_candidate is None:

            st.info(
                "No valid edge-avoidance alternative was found for "
                "the selected route. The primary route remains the "
                "only route identified by this scenario method."
            )

        else:

            alternative_result = alternative_candidate["result"]
            blocked_edge = alternative_candidate["blocked_edge"]

            alternative_path = [
                int(node_id)
                for node_id in alternative_result.path
            ]

            # Reuse the same road-time interpretation used by M32.7.
            alternative_distance = float(
                alternative_result.distance
            )

            alternative_travel_time = 0.0
            alternative_legs = 0
            alternative_road_lookup = {}

            for road in data.roads:

                road_source = int(road.source)
                road_destination = int(road.destination)

                alternative_road_lookup[
                    (road_source, road_destination)
                ] = road

                alternative_road_lookup[
                    (road_destination, road_source)
                ] = road

            for from_node, to_node in zip(
                alternative_path,
                alternative_path[1:],
            ):

                road = alternative_road_lookup.get(
                    (from_node, to_node)
                )

                if road is None:
                    continue

                leg_distance = float(road.distance)

                stored_travel_time = getattr(
                    road,
                    "travel_time",
                    None,
                )

                if stored_travel_time is not None:

                    try:
                        leg_time = float(stored_travel_time)
                    except (TypeError, ValueError):
                        leg_time = (
                            leg_distance
                            / performance_average_speed
                            * 60
                        )

                else:
                    leg_time = (
                        leg_distance
                        / performance_average_speed
                        * 60
                    )

                alternative_travel_time += leg_time
                alternative_legs += 1

            distance_delta = (
                alternative_distance - route_distance
            )

            time_delta = (
                alternative_travel_time
                - performance_travel_time
            )

            distance_delta_pct = (
                distance_delta
                / route_distance
                * 100
                if route_distance > 0
                else 0.0
            )

            time_delta_pct = (
                time_delta
                / performance_travel_time
                * 100
                if performance_travel_time > 0
                else 0.0
            )

            # ------------------------------------------------
            # COMPARISON KPIs
            # ------------------------------------------------

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Primary Distance",
                f"{route_distance:,.2f}",
            )

            col2.metric(
                "Alternative Distance",
                f"{alternative_distance:,.2f}",
                delta=f"{distance_delta:+,.2f}",
            )

            col3.metric(
                "Primary Travel Time",
                f"{performance_travel_time:,.1f} min",
            )

            col4.metric(
                "Alternative Travel Time",
                f"{alternative_travel_time:,.1f} min",
                delta=f"{time_delta:+,.1f} min",
            )

            # ------------------------------------------------
            # SCENARIO DETAILS
            # ------------------------------------------------

            st.subheader("Scenario Comparison")

            scenario_rows = [
                {
                    "Metric": "Distance",
                    "Primary Route": round(
                        route_distance,
                        2,
                    ),
                    "Alternative Route": round(
                        alternative_distance,
                        2,
                    ),
                    "Difference": round(
                        distance_delta,
                        2,
                    ),
                    "Difference (%)": round(
                        distance_delta_pct,
                        2,
                    ),
                },
                {
                    "Metric": "Travel Time (min)",
                    "Primary Route": round(
                        performance_travel_time,
                        2,
                    ),
                    "Alternative Route": round(
                        alternative_travel_time,
                        2,
                    ),
                    "Difference": round(
                        time_delta,
                        2,
                    ),
                    "Difference (%)": round(
                        time_delta_pct,
                        2,
                    ),
                },
                {
                    "Metric": "Road Legs",
                    "Primary Route": total_legs,
                    "Alternative Route": alternative_legs,
                    "Difference": alternative_legs - total_legs,
                    "Difference (%)": round(
                        (
                            (alternative_legs - total_legs)
                            / total_legs
                            * 100
                        )
                        if total_legs > 0
                        else 0.0,
                        2,
                    ),
                },
                {
                    "Metric": "Path Nodes",
                    "Primary Route": len(performance_path),
                    "Alternative Route": len(alternative_path),
                    "Difference": (
                        len(alternative_path)
                        - len(performance_path)
                    ),
                    "Difference (%)": round(
                        (
                            (
                                len(alternative_path)
                                - len(performance_path)
                            )
                            / len(performance_path)
                            * 100
                        )
                        if performance_path
                        else 0.0,
                        2,
                    ),
                },
                {
                    "Metric": "A* Nodes Explored",
                    "Primary Route": route_result.nodes_explored,
                    "Alternative Route": alternative_result.nodes_explored,
                    "Difference": (
                        alternative_result.nodes_explored
                        - route_result.nodes_explored
                    ),
                    "Difference (%)": round(
                        (
                            (
                                alternative_result.nodes_explored
                                - route_result.nodes_explored
                            )
                            / route_result.nodes_explored
                            * 100
                        )
                        if route_result.nodes_explored > 0
                        else 0.0,
                        2,
                    ),
                },
            ]

            st.dataframe(
                scenario_rows,
                width="stretch",
                hide_index=True,
            )

            # ------------------------------------------------
            # PATHS
            # ------------------------------------------------

            st.subheader("Route Scenario Paths")

            path_col1, path_col2 = st.columns(2)

            with path_col1:

                st.markdown("**Primary Route**")

                st.code(
                    " → ".join(
                        str(node_id)
                        for node_id in performance_path
                    ),
                    language="text",
                )

            with path_col2:

                st.markdown("**Alternative Route**")

                st.code(
                    " → ".join(
                        str(node_id)
                        for node_id in alternative_path
                    ),
                    language="text",
                )

            st.info(
                f"Scenario: temporarily avoid road segment "
                f"Node {blocked_edge[0]} → Node {blocked_edge[1]} "
                f"from the primary route. The resulting alternative "
                f"contains {alternative_legs} road legs and covers "
                f"{alternative_distance:.2f} distance units."
            )

            # ------------------------------------------------
            # OPERATIONAL INTERPRETATION
            # ------------------------------------------------

            st.subheader("Scenario Interpretation")

            if distance_delta > 0:
                distance_statement = (
                    f"The alternative adds {distance_delta:.2f} "
                    f"distance units ({distance_delta_pct:.2f}%) "
                    "relative to the primary route."
                )
            elif distance_delta < 0:
                distance_statement = (
                    f"The alternative is {abs(distance_delta):.2f} "
                    f"distance units ({abs(distance_delta_pct):.2f}%) "
                    "shorter than the primary route under this "
                    "edge-avoidance scenario."
                )
            else:
                distance_statement = (
                    "The alternative has the same calculated distance "
                    "as the primary route."
                )

            if time_delta > 0:
                time_statement = (
                    f"Travel time increases by {time_delta:.1f} minutes "
                    f"({time_delta_pct:.2f}%)."
                )
            elif time_delta < 0:
                time_statement = (
                    f"Travel time decreases by {abs(time_delta):.1f} minutes "
                    f"({abs(time_delta_pct):.2f}%)."
                )
            else:
                time_statement = (
                    "Estimated travel time remains unchanged."
                )

            st.write(
                f"{distance_statement} {time_statement} "
                f"The scenario changes the route from "
                f"{total_legs} to {alternative_legs} road legs."
            )


        # ----------------------------------------------------
        # ROUTE COST MODELING & BUSINESS IMPACT — M32.10
        # ----------------------------------------------------

        st.divider()

        st.subheader("Route Cost Modeling & Business Impact")

        st.caption(
            "Converts route distance and travel time into an illustrative "
            "operating-cost model. The assumptions are configurable and "
            "are not presented as actual fuel or fleet prices."
        )

        # ----------------------------------------------------
        # CONFIGURABLE COST ASSUMPTIONS
        # ----------------------------------------------------

        with st.expander("Cost Model Assumptions", expanded=False):

            cost_col1, cost_col2 = st.columns(2)

            with cost_col1:

                distance_cost_rate = st.number_input(
                    "Distance Cost / Unit",
                    min_value=0.0,
                    value=8.0,
                    step=0.5,
                    help=(
                        "Illustrative operating cost assigned to each "
                        "distance unit."
                    ),
                )

            with cost_col2:

                time_cost_rate = st.number_input(
                    "Time Cost / Minute",
                    min_value=0.0,
                    value=1.5,
                    step=0.1,
                    help=(
                        "Illustrative operating cost assigned to each "
                        "travel minute."
                    ),
                )

            st.write(
                f"Current model: **{distance_cost_rate:.2f} cost units per "
                f"distance unit** + **{time_cost_rate:.2f} cost units per "
                "travel minute**."
            )

        # ----------------------------------------------------
        # PRIMARY ROUTE COST
        # ----------------------------------------------------

        primary_distance_cost = (
            route_distance * distance_cost_rate
        )

        primary_time_cost = (
            performance_travel_time * time_cost_rate
        )

        primary_total_cost = (
            primary_distance_cost + primary_time_cost
        )

        # ----------------------------------------------------
        # COST FUNCTION
        # ----------------------------------------------------

        def calculate_route_cost(
            distance,
            travel_time,
            distance_rate,
            time_rate,
        ):
            """Calculate a configurable illustrative route operating cost."""

            distance_component = (
                float(distance) * float(distance_rate)
            )

            time_component = (
                float(travel_time) * float(time_rate)
            )

            total_cost = (
                distance_component + time_component
            )

            return {
                "distance_component": distance_component,
                "time_component": time_component,
                "total_cost": total_cost,
            }

        primary_cost = calculate_route_cost(
            route_distance,
            performance_travel_time,
            distance_cost_rate,
            time_cost_rate,
        )

        # ----------------------------------------------------
        # PRIMARY COST KPIs
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Distance Cost",
            f"{primary_cost['distance_component']:,.2f}",
        )

        col2.metric(
            "Time Cost",
            f"{primary_cost['time_component']:,.2f}",
        )

        col3.metric(
            "Total Route Cost",
            f"{primary_cost['total_cost']:,.2f}",
        )

        # ----------------------------------------------------
        # COST BREAKDOWN
        # ----------------------------------------------------

        st.subheader("Primary Route Cost Breakdown")

        primary_cost_rows = [
            {
                "Cost Component": "Distance",
                "Basis": round(route_distance, 2),
                "Rate": round(distance_cost_rate, 2),
                "Estimated Cost": round(
                    primary_cost["distance_component"],
                    2,
                ),
            },
            {
                "Cost Component": "Travel Time",
                "Basis": round(performance_travel_time, 2),
                "Rate": round(time_cost_rate, 2),
                "Estimated Cost": round(
                    primary_cost["time_component"],
                    2,
                ),
            },
            {
                "Cost Component": "Total",
                "Basis": None,
                "Rate": "—",
                "Estimated Cost": round(
                    primary_cost["total_cost"],
                    2,
                ),
            },
        ]

        st.dataframe(
            primary_cost_rows,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # ALTERNATIVE ROUTE BUSINESS IMPACT
        # ----------------------------------------------------

        if alternative_candidate is not None:

            alternative_cost = calculate_route_cost(
                alternative_distance,
                alternative_travel_time,
                distance_cost_rate,
                time_cost_rate,
            )

            cost_delta = (
                alternative_cost["total_cost"]
                - primary_cost["total_cost"]
            )

            cost_delta_pct = (
                cost_delta
                / primary_cost["total_cost"]
                * 100
                if primary_cost["total_cost"] > 0
                else 0.0
            )

            st.subheader("Primary vs Alternative Cost")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Primary Cost",
                f"{primary_cost['total_cost']:,.2f}",
            )

            col2.metric(
                "Alternative Cost",
                f"{alternative_cost['total_cost']:,.2f}",
                delta=f"{cost_delta:+,.2f}",
            )

            col3.metric(
                "Incremental Cost",
                f"{cost_delta:+,.2f}",
            )

            col4.metric(
                "Cost Difference",
                f"{cost_delta_pct:+.2f}%",
            )

            # ----------------------------------------------
            # BUSINESS IMPACT TABLE
            # ----------------------------------------------

            cost_comparison_rows = [
                {
                    "Metric": "Distance Cost",
                    "Primary Route": round(
                        primary_cost["distance_component"],
                        2,
                    ),
                    "Alternative Route": round(
                        alternative_cost["distance_component"],
                        2,
                    ),
                    "Difference": round(
                        alternative_cost["distance_component"]
                        - primary_cost["distance_component"],
                        2,
                    ),
                },
                {
                    "Metric": "Time Cost",
                    "Primary Route": round(
                        primary_cost["time_component"],
                        2,
                    ),
                    "Alternative Route": round(
                        alternative_cost["time_component"],
                        2,
                    ),
                    "Difference": round(
                        alternative_cost["time_component"]
                        - primary_cost["time_component"],
                        2,
                    ),
                },
                {
                    "Metric": "Total Cost",
                    "Primary Route": round(
                        primary_cost["total_cost"],
                        2,
                    ),
                    "Alternative Route": round(
                        alternative_cost["total_cost"],
                        2,
                    ),
                    "Difference": round(
                        cost_delta,
                        2,
                    ),
                },
            ]

            st.dataframe(
                cost_comparison_rows,
                width="stretch",
                hide_index=True,
            )

            # ----------------------------------------------
            # BUSINESS IMPACT INTERPRETATION
            # ----------------------------------------------

            st.subheader("Business Impact")

            if cost_delta > 0:

                st.write(
                    f"Under the current illustrative cost assumptions, "
                    f"the alternative route adds **{cost_delta:.2f} cost "
                    f"units ({cost_delta_pct:.2f}%)** compared with the "
                    "primary route. This additional cost is driven by the "
                    f"distance and time differences of the scenario."
                )

            elif cost_delta < 0:

                st.write(
                    f"Under the current illustrative cost assumptions, "
                    f"the alternative route reduces estimated operating "
                    f"cost by **{abs(cost_delta):.2f} cost units "
                    f"({abs(cost_delta_pct):.2f}%)** compared with the "
                    "primary route."
                )

            else:

                st.write(
                    "Under the current illustrative cost assumptions, "
                    "the primary and alternative routes have the same "
                    "estimated operating cost."
                )

        else:

            st.info(
                "No alternative route was identified, so a scenario cost "
                "comparison is not available. The primary route cost model "
                "is still available above."
            )

        # ----------------------------------------------------
        # COST MODEL TRANSPARENCY
        # ----------------------------------------------------

        st.caption(
            "Cost model note: these are configurable analytical cost units "
            "for the synthetic logistics network. They are not actual fuel "
            "prices, wages, tolls, or fleet operating costs."
        )



        # ----------------------------------------------------
        # MULTI-CRITERIA ROUTE SCORING — M32.11
        # ----------------------------------------------------

        st.divider()

        st.subheader("Multi-Criteria Route Scoring")

        st.caption(
            "Combines distance, travel time, illustrative operating cost, "
            "and A* search effort into a configurable 0–100 route score. "
            "Higher scores indicate a better fit for the selected weighting profile."
        )

        # ----------------------------------------------------
        # ROUTE CANDIDATES
        # ----------------------------------------------------

        primary_search_effort = float(route_result.nodes_explored)
        primary_score_cost = float(primary_cost["total_cost"])

        route_candidates = [
            {
                "name": "Primary Route",
                "distance": float(route_distance),
                "travel_time": float(performance_travel_time),
                "cost": primary_score_cost,
                "search_effort": primary_search_effort,
                "path": performance_path,
            }
        ]

        if alternative_candidate is not None:

            alternative_search_effort = float(
                alternative_result.nodes_explored
            )

            alternative_score_cost = float(
                alternative_cost["total_cost"]
            )

            route_candidates.append(
                {
                    "name": "Alternative Route",
                    "distance": float(alternative_distance),
                    "travel_time": float(alternative_travel_time),
                    "cost": alternative_score_cost,
                    "search_effort": alternative_search_effort,
                    "path": alternative_path,
                }
            )

        # ----------------------------------------------------
        # CONFIGURABLE WEIGHTS
        # ----------------------------------------------------

        with st.expander(
            "Scoring Weights",
            expanded=False,
        ):

            weight_col1, weight_col2 = st.columns(2)
            weight_col3, weight_col4 = st.columns(2)

            with weight_col1:

                distance_weight = st.slider(
                    "Distance Weight",
                    min_value=0,
                    max_value=100,
                    value=35,
                    step=5,
                    help=(
                        "Importance assigned to route distance."
                    ),
                )

            with weight_col2:

                time_weight = st.slider(
                    "Travel Time Weight",
                    min_value=0,
                    max_value=100,
                    value=30,
                    step=5,
                    help=(
                        "Importance assigned to estimated travel time."
                    ),
                )

            with weight_col3:

                cost_weight = st.slider(
                    "Operating Cost Weight",
                    min_value=0,
                    max_value=100,
                    value=25,
                    step=5,
                    help=(
                        "Importance assigned to the illustrative route cost."
                    ),
                )

            with weight_col4:

                search_weight = st.slider(
                    "Search Effort Weight",
                    min_value=0,
                    max_value=100,
                    value=10,
                    step=5,
                    help=(
                        "Importance assigned to A* nodes explored."
                    ),
                )

        raw_weights = {
            "Distance": float(distance_weight),
            "Travel Time": float(time_weight),
            "Operating Cost": float(cost_weight),
            "Search Effort": float(search_weight),
        }

        total_weight = sum(raw_weights.values())

        if total_weight <= 0:

            st.warning(
                "At least one scoring weight must be greater than zero. "
                "Using equal weights temporarily."
            )

            normalized_weights = {
                key: 0.25
                for key in raw_weights
            }

        else:

            normalized_weights = {
                key: value / total_weight
                for key, value in raw_weights.items()
            }

        st.write(
            "Normalized weighting profile: "
            + " · ".join(
                f"**{key} {value * 100:.1f}%**"
                for key, value in normalized_weights.items()
            )
        )

        # ----------------------------------------------------
        # SCORE NORMALIZATION
        # ----------------------------------------------------

        metric_keys = {
            "Distance": "distance",
            "Travel Time": "travel_time",
            "Operating Cost": "cost",
            "Search Effort": "search_effort",
        }

        metric_scores = {}

        for display_name, candidate_key in metric_keys.items():

            values = [
                float(candidate[candidate_key])
                for candidate in route_candidates
            ]

            minimum_value = min(values)
            maximum_value = max(values)

            if maximum_value == minimum_value:

                scores = [
                    100.0
                    for _ in values
                ]

            else:

                # Lower is better for all four criteria.
                scores = [
                    (
                        (maximum_value - value)
                        / (maximum_value - minimum_value)
                        * 100.0
                    )
                    for value in values
                ]

            metric_scores[display_name] = scores

        # ----------------------------------------------------
        # COMPOSITE SCORE
        # ----------------------------------------------------

        composite_scores = []

        for candidate_index in range(
            len(route_candidates)
        ):

            composite_score = sum(
                metric_scores[display_name][candidate_index]
                * normalized_weights[display_name]
                for display_name in metric_keys
            )

            composite_scores.append(
                composite_score
            )

        # ----------------------------------------------------
        # SCORE KPIs
        # ----------------------------------------------------

        score_columns = st.columns(
            len(route_candidates)
        )

        for index, candidate in enumerate(
            route_candidates
        ):

            with score_columns[index]:

                st.metric(
                    f"{candidate['name']} Score",
                    f"{composite_scores[index]:.2f} / 100",
                )

        # ----------------------------------------------------
        # SCORE COMPARISON TABLE
        # ----------------------------------------------------

        st.subheader("Route Score Comparison")

        score_rows = []

        for index, candidate in enumerate(
            route_candidates
        ):

            score_rows.append(
                {
                    "Route": candidate["name"],
                    "Distance": round(
                        candidate["distance"],
                        2,
                    ),
                    "Travel Time (min)": round(
                        candidate["travel_time"],
                        2,
                    ),
                    "Operating Cost": round(
                        candidate["cost"],
                        2,
                    ),
                    "A* Nodes Explored": int(
                        candidate["search_effort"]
                    ),
                    "Composite Score": round(
                        composite_scores[index],
                        2,
                    ),
                }
            )

        st.dataframe(
            score_rows,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # CRITERION-LEVEL SCORE BREAKDOWN
        # ----------------------------------------------------

        st.subheader("Criterion Score Breakdown")

        criterion_rows = []

        for index, candidate in enumerate(
            route_candidates
        ):

            criterion_rows.append(
                {
                    "Route": candidate["name"],
                    "Distance Score": round(
                        metric_scores["Distance"][index],
                        2,
                    ),
                    "Time Score": round(
                        metric_scores["Travel Time"][index],
                        2,
                    ),
                    "Cost Score": round(
                        metric_scores["Operating Cost"][index],
                        2,
                    ),
                    "Search Effort Score": round(
                        metric_scores["Search Effort"][index],
                        2,
                    ),
                }
            )

        st.dataframe(
            criterion_rows,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # DECISION INTERPRETATION
        # ----------------------------------------------------

        st.subheader("Scenario Interpretation")

        if len(route_candidates) >= 2:

            primary_composite = composite_scores[0]
            alternative_composite = composite_scores[1]
            score_difference = (
                alternative_composite
                - primary_composite
            )

            if score_difference > 0:

                interpretation = (
                    "Under the selected weighting profile, the "
                    "alternative receives a higher composite score. "
                    "This reflects the relative distance, travel-time, "
                    "cost, and search-effort values in this scenario."
                )

            elif score_difference < 0:

                interpretation = (
                    "Under the selected weighting profile, the primary "
                    "route receives a higher composite score. The score "
                    "reflects the relative distance, travel-time, cost, "
                    "and search-effort values in this scenario."
                )

            else:

                interpretation = (
                    "Under the selected weighting profile, the primary "
                    "and alternative routes receive the same composite score."
                )

            st.info(interpretation)

            st.caption(
                "The composite score is a configurable analytical score, "
                "not a prediction or guarantee of operational performance."
            )

        else:

            st.info(
                "Only the primary route is available for this scenario. "
                "The score is therefore shown as a baseline rather than "
                "a route-to-route comparison."
            )


        # ----------------------------------------------------
        # ROUTE DECISION DASHBOARD — M32.12
        # ----------------------------------------------------

        st.divider()

        st.subheader("Route Decision Dashboard")

        st.caption(
            "Consolidates route performance, risk indicators, scenario alternatives, "
            "cost impact, and the multi-criteria score into one operational decision view."
        )

        # ----------------------------------------------------
        # DECISION PROFILE
        # ----------------------------------------------------

        primary_candidate = route_candidates[0]
        primary_score = float(composite_scores[0])

        if len(route_candidates) >= 2:
            alternative_candidate = route_candidates[1]
            alternative_score = float(composite_scores[1])

            if alternative_score > primary_score:
                profile_route_name = "Alternative Route"
                profile_route = alternative_candidate
                profile_score = alternative_score
            elif alternative_score < primary_score:
                profile_route_name = "Primary Route"
                profile_route = primary_candidate
                profile_score = primary_score
            else:
                profile_route_name = "Primary Route / Alternative Route"
                profile_route = primary_candidate
                profile_score = primary_score

            score_gap = abs(primary_score - alternative_score)
        else:
            profile_route_name = "Primary Route"
            profile_route = primary_candidate
            profile_score = primary_score
            alternative_candidate = None
            alternative_score = None
            score_gap = None

        # ----------------------------------------------------
        # DECISION KPIs
        # ----------------------------------------------------

        decision_col1, decision_col2, decision_col3, decision_col4 = st.columns(4)

        decision_col1.metric(
            "Profile Route",
            profile_route_name,
        )

        decision_col2.metric(
            "Composite Score",
            f"{profile_score:.2f} / 100",
        )

        decision_col3.metric(
            "Distance",
            f"{profile_route['distance']:.2f}",
        )

        decision_col4.metric(
            "Travel Time",
            f"{profile_route['travel_time']:.1f} min",
        )

        # ----------------------------------------------------
        # DECISION FACTOR SUMMARY
        # ----------------------------------------------------

        st.subheader("Decision Factor Summary")

        decision_rows = []

        decision_rows.append(
            {
                "Factor": "Distance",
                "Primary Route": round(primary_candidate["distance"], 2),
                "Alternative Route": (
                    round(alternative_candidate["distance"], 2)
                    if alternative_candidate is not None
                    else None
                ),
                "Weight": f"{normalized_weights['Distance'] * 100:.1f}%",
            }
        )

        decision_rows.append(
            {
                "Factor": "Travel Time (min)",
                "Primary Route": round(primary_candidate["travel_time"], 2),
                "Alternative Route": (
                    round(alternative_candidate["travel_time"], 2)
                    if alternative_candidate is not None
                    else None
                ),
                "Weight": f"{normalized_weights['Travel Time'] * 100:.1f}%",
            }
        )

        decision_rows.append(
            {
                "Factor": "Operating Cost",
                "Primary Route": round(primary_candidate["cost"], 2),
                "Alternative Route": (
                    round(alternative_candidate["cost"], 2)
                    if alternative_candidate is not None
                    else None
                ),
                "Weight": f"{normalized_weights['Operating Cost'] * 100:.1f}%",
            }
        )

        decision_rows.append(
            {
                "Factor": "A* Nodes Explored",
                "Primary Route": int(primary_candidate["search_effort"]),
                "Alternative Route": (
                    int(alternative_candidate["search_effort"])
                    if alternative_candidate is not None
                    else None
                ),
                "Weight": f"{normalized_weights['Search Effort'] * 100:.1f}%",
            }
        )

        st.dataframe(
            decision_rows,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # ROUTE DECISION SUMMARY
        # ----------------------------------------------------

        st.subheader("Route Decision Summary")

        if alternative_candidate is not None:

            if alternative_score > primary_score:
                score_statement = (
                    f"Under the selected weighting profile, the alternative "
                    f"route has the higher composite score by "
                    f"{score_gap:.2f} points."
                )
            elif alternative_score < primary_score:
                score_statement = (
                    f"Under the selected weighting profile, the primary "
                    f"route has the higher composite score by "
                    f"{score_gap:.2f} points."
                )
            else:
                score_statement = (
                    "Under the selected weighting profile, both routes have "
                    "the same composite score."
                )

            st.write(
                f"The **{profile_route_name}** is the route represented by the "
                f"current multi-criteria profile, with a composite score of "
                f"**{profile_score:.2f}/100**. {score_statement}"
            )

            st.write(
                f"The selected profile assigns **{normalized_weights['Distance'] * 100:.1f}%** "
                f"to distance, **{normalized_weights['Travel Time'] * 100:.1f}%** "
                f"to travel time, **{normalized_weights['Operating Cost'] * 100:.1f}%** "
                f"to operating cost, and **{normalized_weights['Search Effort'] * 100:.1f}%** "
                f"to A* search effort."
            )

            st.write(
                f"The profile route covers **{profile_route['distance']:.2f}** "
                f"distance units, requires approximately **{profile_route['travel_time']:.1f} minutes**, "
                f"and has an illustrative operating cost of **{profile_route['cost']:.2f}**."
            )

        else:

            st.write(
                f"Only the primary route is available for this scenario. "
                f"It has a composite score of **{profile_score:.2f}/100** "
                f"under the selected weighting profile."
            )

        # ----------------------------------------------------
        # DECISION CHECKLIST
        # ----------------------------------------------------

        st.subheader("Operational Decision Checklist")

        checklist_col1, checklist_col2 = st.columns(2)

        with checklist_col1:

            if performance_legs:
                st.success("Route network mapping validated.")
            else:
                st.warning("Route network mapping requires review.")

            if distance_difference < 1e-6:
                st.success("Route distance consistency validated.")
            else:
                st.warning(
                    f"Route distance difference detected: {distance_difference:.6f}."
                )

            if attention_segments:
                st.warning(
                    f"{len(attention_segments)} route segment(s) exceed the configured "
                    "attention thresholds."
                )
            else:
                st.success("No route segment crossed the configured attention thresholds.")

        with checklist_col2:

            if alternative_candidate is not None:
                st.success("Alternative route scenario is available.")
            else:
                st.info("No valid alternative route was found for this scenario.")

            if primary_cost:
                st.success("Illustrative route cost model is available.")

            st.info(
                "The decision profile is analytical and depends on the selected "
                "weights and configured cost assumptions."
            )

        # ----------------------------------------------------
        # DECISION INTERPRETATION
        # ----------------------------------------------------

        st.subheader("Decision Interpretation")

        if alternative_candidate is not None:

            if alternative_score > primary_score:
                interpretation_text = (
                    "The current weighting profile gives the alternative route the "
                    "higher composite score. Review the distance, time, cost, and "
                    "search-effort differences before using the scenario operationally."
                )
            elif alternative_score < primary_score:
                interpretation_text = (
                    "The current weighting profile gives the primary route the "
                    "higher composite score. The alternative remains available as "
                    "an edge-avoidance scenario for contingency analysis."
                )
            else:
                interpretation_text = (
                    "The current weighting profile produces equal composite scores. "
                    "The route comparison should therefore be examined using the "
                    "individual distance, time, cost, and search-effort metrics."
                )

            st.info(interpretation_text)

        else:

            st.info(
                "The primary route is the only available scenario. The decision "
                "dashboard therefore reports its performance and scoring profile "
                "without an alternative-route comparison."
            )

        st.caption(
            "Decision dashboard note: this is a configurable analytical decision-support "
            "layer for the synthetic logistics network. It does not represent live traffic, "
            "real-time fleet conditions, or guaranteed operational outcomes."
        )

# ============================================================


        # ----------------------------------------------------
        # FINAL SYSTEM VALIDATION — M32.13
        # ----------------------------------------------------

        render_system_validation(
            route_result=route_result,
            performance_legs=performance_legs,
            distance_difference=distance_difference,
            alternative_candidate=alternative_candidate,
            primary_cost=primary_cost,
            composite_scores=composite_scores,
            profile_route_name=profile_route_name,
        )

# ============================================================
# NETWORK INTELLIGENCE
# ============================================================

elif page == "Network Intelligence":

    st.header("Network Intelligence")

    st.write(
        "Structural analysis of the logistics network."
    )

    # --------------------------------------------------------
    # NETWORK KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Locations",
        f"{network_info['location_count']:,}",
    )

    col2.metric(
        "Road Connections",
        f"{network_info['road_count']:,}",
    )

    col3.metric(
        "Routing Nodes",
        f"{network_info['routing_node_count']:,}",
    )

    col4.metric(
        "Average Degree",
        f"{network_info['average_degree']:.2f}",
    )

    # --------------------------------------------------------
    # CONNECTIVITY
    # --------------------------------------------------------

    st.subheader("Connectivity Analysis")

    col1, col2 = st.columns(2)

    col1.metric(
        "Connected Locations",
        f"{network_info['connected_location_count']:,}",
    )

    col2.metric(
        "Connectivity Rate",
        f"{network_info['connectivity_rate']:.2f}%",
    )

    # --------------------------------------------------------
    # TOP CONNECTED LOCATIONS
    # --------------------------------------------------------

    st.subheader(
        "Most Connected Locations"
    )

    top_connected_rows = [
        {
            "Location": location_id,
            "Connections": connection_count,
        }
        for location_id, connection_count
        in network_info["top_connected"]
    ]

    if top_connected_rows:

        st.dataframe(
            top_connected_rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No connection information is available."
        )

    # --------------------------------------------------------
    # NETWORK VISUALIZATION
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Interactive Logistics Network"
    )

    st.info(
        f"The network contains {len(data.locations):,} "
        "locations. Load the visualization only when needed."
    )

    if st.button(
        "Load Network Visualization",
        type="primary",
    ):

        st.session_state.network_loaded = True

    if st.session_state.network_loaded:

        try:

            route_path = None

            if (
                st.session_state.route_result
                is not None
            ):

                route_path = (
                    st.session_state.route_result.path
                )

            network_figure = build_network_figure(
                data.locations,
                data.roads,
                route_path=route_path,
            )

            st.plotly_chart(
                network_figure,
                width="stretch",
            )

        except Exception as exc:

            st.error(
                f"Network visualization failed: {exc}"
            )


# ============================================================
# ALGORITHM ANALYTICS
# ============================================================

elif page == "Algorithm Analytics":

    st.header("Routing Algorithm Analytics")

    st.write(
        "Compare A* and Dijkstra on the same routing graph."
    )

    if len(routing_node_ids) < 2:

        st.error(
            "The routing graph contains fewer than two "
            "usable nodes."
        )

        st.stop()

    # --------------------------------------------------------
    # ANALYTICS INPUT
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        analytics_source = st.selectbox(
            "Analytics Origin",
            routing_node_ids,
            index=0,
            key="analytics_source",
        )

    with col2:

        analytics_destination = st.selectbox(
            "Analytics Destination",
            routing_node_ids,
            index=1,
            key="analytics_destination",
        )

    # --------------------------------------------------------
    # RUN ANALYSIS
    # --------------------------------------------------------

    if st.button(
        "Run A* vs Dijkstra Analysis",
        type="primary",
        width="stretch",
    ):

        if (
            analytics_source
            == analytics_destination
        ):

            st.error(
                "Origin and destination must be different."
            )

        elif not routing_graph.has_node(
            analytics_source
        ):

            st.error(
                f"Origin node {analytics_source} "
                "does not exist in the routing graph."
            )

        elif not routing_graph.has_node(
            analytics_destination
        ):

            st.error(
                f"Destination node {analytics_destination} "
                "does not exist in the routing graph."
            )

        else:

            try:

                comparison = (
                    compare_routing_algorithms(
                        graph=routing_graph,
                        locations=data.locations,
                        source=analytics_source,
                        destination=analytics_destination,
                    )
                )

                st.session_state.analytics_result = (
                    comparison
                )

            except ValueError as exc:

                st.error(
                    f"Algorithm comparison failed: {exc}"
                )

                st.session_state.analytics_result = None

            except Exception as exc:

                st.error(
                    f"Unexpected analytics error: {exc}"
                )

                st.session_state.analytics_result = None

    comparison = st.session_state.analytics_result

    # ========================================================
    # ANALYTICS RESULTS
    # ========================================================

    if comparison is not None:

        st.divider()

        st.subheader("A* vs Dijkstra")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "A* Distance",
            f"{comparison.a_star_distance:,.4f}",
        )

        col2.metric(
            "Dijkstra Distance",
            f"{comparison.dijkstra_distance:,.4f}",
        )

        col3.metric(
            "A* Runtime",
            f"{comparison.a_star_runtime_seconds:.6f}s",
        )

        col4.metric(
            "Dijkstra Runtime",
            f"{comparison.dijkstra_runtime_seconds:.6f}s",
        )

        # ----------------------------------------------------
        # SEARCH PERFORMANCE
        # ----------------------------------------------------

        st.subheader("Search Performance")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "A* Nodes Explored",
            comparison.a_star_nodes_explored,
        )

        col2.metric(
            "A* Heap Operations",
            comparison.a_star_heap_operations,
        )

        col3.metric(
            "A* Path Nodes",
            comparison.a_star_path_nodes,
        )

        col4.metric(
            "Dijkstra Path Nodes",
            comparison.dijkstra_path_nodes,
        )

        # ----------------------------------------------------
        # CORRECTNESS
        # ----------------------------------------------------

        st.subheader(
            "Correctness Verification"
        )

        if (
            comparison.distance_difference
            < 1e-9
        ):

            st.success(
                "Correctness verified: A* and Dijkstra "
                "produced the same shortest-path distance."
            )

        else:

            st.error(
                "Correctness check failed: A* and Dijkstra "
                "produced different shortest-path distances."
            )

        st.metric(
            "Distance Difference",
            f"{comparison.distance_difference:.12f}",
        )

        # ----------------------------------------------------
        # RUNTIME COMPARISON
        # ----------------------------------------------------

        st.subheader("Runtime Comparison")

        if (
            comparison.a_star_runtime_seconds > 0
            and comparison.dijkstra_runtime_seconds > 0
        ):

            runtime_ratio = (
                comparison.dijkstra_runtime_seconds
                / comparison.a_star_runtime_seconds
            )

            st.write(
                "Dijkstra/A* runtime ratio: "
                f"**{runtime_ratio:.2f}×**"
            )

        else:

            st.info(
                "Runtime ratio cannot be calculated "
                "because one measurement is zero."
            )


# ============================================================
# OPTIMIZATION
# ============================================================

elif page == "Optimization":

    st.header("Optimization Results")

    st.write(
        "Historical optimization runs stored in the database."
    )

    if data.optimization_results:

        optimization_rows = []

        for result in data.optimization_results:

            optimization_rows.append(
                {
                    "Algorithm": result.algorithm,
                    "Objective Value": (
                        result.objective_value
                    ),
                    "Runtime (seconds)": (
                        result.runtime_seconds
                    ),
                    "Status": result.status,
                }
            )

        st.dataframe(
            optimization_rows,
            width="stretch",
            hide_index=True,
        )

        st.subheader("Optimization Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Optimization Runs",
            len(data.optimization_results),
        )

        successful_runs = sum(
            1
            for result
            in data.optimization_results
            if str(result.status).upper()
            == "SUCCESS"
        )

        col2.metric(
            "Successful Runs",
            successful_runs,
        )

        average_runtime = (
            sum(
                float(result.runtime_seconds)
                for result
                in data.optimization_results
            )
            / len(data.optimization_results)
        )

        col3.metric(
            "Average Runtime",
            f"{average_runtime:.6f}s",
        )

    else:

        st.info(
            "No optimization results are currently stored."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Intelligent Logistics Routing & Optimization Engine "
    "• Production Dashboard"
)