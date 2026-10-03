"""
M33.4 - Regression & Integration Testing

This suite checks that the core routing stack and the production-hardening
modules continue to work together without importing the Streamlit dashboard
itself. The dashboard app performs database loading at import time, so it is
intentionally not imported here.

Run from:
    C:\\Users\\Asus\\src

Command:
    python -m unittest logistics_engine.tests.test_integration -v
"""

import unittest


class TestCoreRoutingIntegration(unittest.TestCase):
    """M33.4 integration checks for the routing core."""

    @staticmethod
    def build_graph():
        from logistics_engine.graph import Graph

        graph = Graph()

        graph.add_edge(0, 1, 5.0, bidirectional=True)
        graph.add_edge(1, 2, 3.0, bidirectional=True)
        graph.add_edge(0, 2, 12.0, bidirectional=True)
        graph.add_edge(2, 3, 2.0, bidirectional=True)
        graph.add_edge(1, 3, 20.0, bidirectional=True)

        return graph

    def test_01_graph_construction(self):
        """The routing graph can be constructed from valid road data."""
        graph = self.build_graph()

        nodes = graph.nodes() if callable(graph.nodes) else graph.nodes

        self.assertIn(0, nodes)
        self.assertIn(1, nodes)
        self.assertIn(2, nodes)
        self.assertIn(3, nodes)

    def test_02_graph_is_bidirectional(self):
        """The dashboard's bidirectional road construction remains valid."""
        graph = self.build_graph()

        self.assertTrue(any(neighbor == 1 for neighbor, _ in graph.adjacency_list[0]))
        self.assertTrue(any(neighbor == 0 for neighbor, _ in graph.adjacency_list[1]))
        self.assertTrue(any(neighbor == 3 for neighbor, _ in graph.adjacency_list[2]))
        self.assertTrue(any(neighbor == 2 for neighbor, _ in graph.adjacency_list[3]))

    def test_03_a_star_returns_expected_route(self):
        """A* still returns the expected shortest route."""
        from logistics_engine.routing import a_star

        graph = self.build_graph()

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 2, 3])
        self.assertAlmostEqual(result.distance, 10.0)

    def test_04_dijkstra_returns_expected_route(self):
        """Dijkstra still returns the expected shortest route."""
        from logistics_engine.routing import dijkstra

        graph = self.build_graph()

        result = dijkstra(graph, 0, 3)

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 2, 3])
        self.assertAlmostEqual(result.distance, 10.0)

    def test_05_a_star_matches_dijkstra(self):
        """The A* zero-heuristic route remains distance-consistent with Dijkstra."""
        from logistics_engine.routing import a_star, dijkstra

        graph = self.build_graph()

        a_star_result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )
        dijkstra_result = dijkstra(graph, 0, 3)

        self.assertIsNotNone(a_star_result)
        self.assertIsNotNone(dijkstra_result)

        self.assertAlmostEqual(
            a_star_result.distance,
            dijkstra_result.distance,
        )
        self.assertEqual(
            a_star_result.path,
            dijkstra_result.path,
        )

    def test_06_route_result_metrics_are_valid(self):
        """The routing result exposes the metrics consumed by the dashboard."""
        from logistics_engine.routing import a_star

        graph = self.build_graph()

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.distance, 0.0)
        self.assertGreaterEqual(result.nodes_explored, 1)
        self.assertGreaterEqual(result.heap_operations, 0)
        self.assertGreaterEqual(len(result.path), 2)

    def test_07_unreachable_route_returns_none(self):
        """A disconnected destination remains a handled no-route scenario."""
        from logistics_engine.graph import Graph
        from logistics_engine.routing import a_star

        graph = Graph()

        graph.add_edge(0, 1, 5.0)
        graph.add_edge(2, 3, 5.0)

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNone(result)

    def test_08_production_validation_module_imports(self):
        """The extracted M33.1 validation layer remains importable."""
        from logistics_engine.dashboard.validation import (
            render_system_validation,
        )

        self.assertTrue(callable(render_system_validation))

    def test_09_dashboard_support_modules_import(self):
        """Core dashboard support modules remain importable."""
        from logistics_engine.dashboard.business_metrics import (
            calculate_business_metrics,
        )
        from logistics_engine.dashboard.data import load_dashboard_data
        from logistics_engine.dashboard.metrics import calculate_route_metrics
        from logistics_engine.dashboard.routing_analytics import (
            compare_routing_algorithms,
        )
        from logistics_engine.dashboard.visualization import build_network_figure

        self.assertTrue(callable(calculate_business_metrics))
        self.assertTrue(callable(load_dashboard_data))
        self.assertTrue(callable(calculate_route_metrics))
        self.assertTrue(callable(compare_routing_algorithms))
        self.assertTrue(callable(build_network_figure))

    def test_10_m33_data_robustness_module_imports(self):
        """The M33.3 robustness test module is importable."""
        from logistics_engine.tests import test_data_robustness

        self.assertTrue(
            hasattr(
                test_data_robustness,
                "process_route_legs",
            )
        )

    def test_11_m33_edge_case_module_imports(self):
        """The M33.2 edge-case test module remains importable."""
        from logistics_engine.tests import test_edge_cases

        self.assertTrue(
            hasattr(
                test_edge_cases,
                "TestRoutingEdgeCases",
            )
        )

    def test_12_routing_modules_share_the_same_graph_contract(self):
        """A graph produced for A* can also be consumed by Dijkstra."""
        from logistics_engine.routing import a_star, dijkstra

        graph = self.build_graph()

        a_result = a_star(
            graph,
            [],
            0,
            2,
            heuristic="zero",
        )
        d_result = dijkstra(graph, 0, 2)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertAlmostEqual(a_result.distance, 8.0)
        self.assertAlmostEqual(d_result.distance, 8.0)

    def test_13_zero_distance_route_is_stable(self):
        """A zero-distance edge does not break the routing pipeline."""
        from logistics_engine.graph import Graph
        from logistics_engine.routing import a_star

        graph = Graph()
        graph.add_edge(0, 1, 0.0)
        graph.add_edge(1, 2, 5.0)

        result = a_star(
            graph,
            [],
            0,
            2,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 2])
        self.assertAlmostEqual(result.distance, 5.0)

    def test_14_multiple_routes_select_lowest_distance(self):
        """The routing stack selects the lowest-cost path among alternatives."""
        from logistics_engine.graph import Graph
        from logistics_engine.routing import a_star

        graph = Graph()
        graph.add_edge(0, 1, 2.0)
        graph.add_edge(1, 3, 2.0)
        graph.add_edge(0, 2, 1.0)
        graph.add_edge(2, 3, 10.0)

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 3])
        self.assertAlmostEqual(result.distance, 4.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
