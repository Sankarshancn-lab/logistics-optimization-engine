"""
M33.6 - Resource & Memory Stability

This suite validates resource behavior of the existing routing engine without
changing the production algorithms or importing the Streamlit dashboard.

Run from:
    C:\\Users\\Asus\\src

Command:
    python -m unittest logistics_engine.tests.test_resource_stability -v
"""

import gc
import math
import time
import tracemalloc
import unittest


class TestResourceStability(unittest.TestCase):
    """M33.6 resource and memory stability checks."""

    @staticmethod
    def build_graph(node_count: int):
        from logistics_engine.graph import Graph

        graph = Graph()

        # A connected bidirectional backbone.
        for node in range(node_count - 1):
            graph.add_edge(
                node,
                node + 1,
                1.0,
                bidirectional=True,
            )

        # Add deterministic shortcuts without making the graph dense.
        step = max(10, node_count // 20)
        for node in range(0, node_count - step, step):
            graph.add_edge(
                node,
                node + step,
                float(step) + 0.5,
                bidirectional=True,
            )

        return graph

    @staticmethod
    def locations_for(node_count: int):
        # The current zero-heuristic routing path only requires a
        # positionally valid list for node-index validation.
        return list(range(node_count))

    def test_01_small_graph_resource_baseline(self):
        """A small graph can be created and routed repeatedly."""
        from logistics_engine.routing import a_star

        graph = self.build_graph(50)
        locations = self.locations_for(50)

        for _ in range(10):
            result = a_star(
                graph,
                locations,
                0,
                49,
                heuristic="zero",
            )

            self.assertIsNotNone(result)
            self.assertAlmostEqual(result.distance, 49.0)
            self.assertTrue(result.path)

    def test_02_graph_scales_without_memory_failure(self):
        """Graphs up to 5,000 nodes can be constructed under tracemalloc."""
        sizes = (50, 500, 1000, 5000)
        measurements = []

        for size in sizes:
            gc.collect()
            tracemalloc.start()

            graph = self.build_graph(size)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            self.assertGreater(len(graph.nodes()), 0)
            self.assertGreaterEqual(peak, current)
            self.assertTrue(math.isfinite(float(current)))
            self.assertTrue(math.isfinite(float(peak)))

            measurements.append((size, current, peak))

            del graph
            gc.collect()

        print("\nM33.6 graph memory measurements")
        print("Nodes | Current Bytes | Peak Bytes")
        print("-----------------------------------")
        for size, current, peak in measurements:
            print(
                f"{size:5d} | {current:13d} | {peak:10d}"
            )

    def test_03_large_graph_routes_successfully(self):
        """Routing remains valid on the 5,000-node graph."""
        from logistics_engine.routing import a_star, dijkstra

        size = 5000
        graph = self.build_graph(size)
        locations = self.locations_for(size)

        a_result = a_star(
            graph,
            locations,
            0,
            size - 1,
            heuristic="zero",
        )
        d_result = dijkstra(
            graph,
            0,
            size - 1,
        )

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertAlmostEqual(
            a_result.distance,
            d_result.distance,
        )
        self.assertEqual(
            a_result.path[0],
            0,
        )
        self.assertEqual(
            a_result.path[-1],
            size - 1,
        )

    def test_04_repeated_routing_does_not_accumulate_unbounded_memory(self):
        """Repeated routing remains within a conservative memory-growth bound."""
        from logistics_engine.routing import a_star

        graph = self.build_graph(1000)
        locations = self.locations_for(1000)

        gc.collect()
        tracemalloc.start()

        # Warm-up removes one-time allocation effects from the comparison.
        warmup = a_star(
            graph,
            locations,
            0,
            999,
            heuristic="zero",
        )
        self.assertIsNotNone(warmup)

        gc.collect()
        before_current, _ = tracemalloc.get_traced_memory()

        for _ in range(25):
            result = a_star(
                graph,
                locations,
                0,
                999,
                heuristic="zero",
            )
            self.assertIsNotNone(result)

        gc.collect()
        after_current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        retained_growth = max(0, after_current - before_current)

        # This is intentionally a broad guard against runaway retention,
        # not a micro-benchmark threshold.
        self.assertLess(
            retained_growth,
            5 * 1024 * 1024,
            msg=(
                "Repeated routing retained more than 5 MB after "
                "garbage collection."
            ),
        )

        self.assertGreaterEqual(peak, after_current)

        print(
            "\nM33.6 repeated-routing memory check:"
            f" retained_growth={retained_growth / 1024:.2f} KB,"
            f" peak={peak / 1024:.2f} KB"
        )

    def test_05_routing_results_remain_valid_after_repeated_execution(self):
        """Repeated routing does not corrupt later route results."""
        from logistics_engine.routing import a_star

        graph = self.build_graph(500)
        locations = self.locations_for(500)

        expected_distance = 499.0

        for index in range(30):
            source = 0
            destination = 499

            result = a_star(
                graph,
                locations,
                source,
                destination,
                heuristic="zero",
            )

            self.assertIsNotNone(result)
            self.assertAlmostEqual(
                result.distance,
                expected_distance,
            )
            self.assertEqual(result.path[0], source)
            self.assertEqual(result.path[-1], destination)

            if index == 29:
                self.assertGreaterEqual(
                    result.nodes_explored,
                    0,
                )
                self.assertGreaterEqual(
                    result.heap_operations,
                    0,
                )

    def test_06_garbage_collection_does_not_break_routing(self):
        """Explicit garbage collection between runs preserves correctness."""
        from logistics_engine.routing import a_star

        graph = self.build_graph(1000)
        locations = self.locations_for(1000)

        distances = []

        for _ in range(10):
            gc.collect()

            result = a_star(
                graph,
                locations,
                100,
                900,
                heuristic="zero",
            )

            self.assertIsNotNone(result)
            distances.append(result.distance)

        self.assertTrue(all(
            math.isfinite(float(distance))
            for distance in distances
        ))
        self.assertTrue(
            all(
                abs(distance - distances[0]) < 1e-9
                for distance in distances
            )
        )

    def test_07_resource_measurement_has_no_invalid_values(self):
        """Memory and runtime measurements remain finite and non-negative."""
        from logistics_engine.routing import a_star

        graph = self.build_graph(1000)
        locations = self.locations_for(1000)

        gc.collect()
        tracemalloc.start()
        start = time.perf_counter()

        result = a_star(
            graph,
            locations,
            0,
            999,
            heuristic="zero",
        )

        elapsed = time.perf_counter() - start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.assertIsNotNone(result)
        self.assertGreaterEqual(elapsed, 0.0)
        self.assertGreaterEqual(current, 0)
        self.assertGreaterEqual(peak, 0)

        self.assertTrue(math.isfinite(elapsed))
        self.assertTrue(math.isfinite(float(current)))
        self.assertTrue(math.isfinite(float(peak)))


if __name__ == "__main__":
    unittest.main()
