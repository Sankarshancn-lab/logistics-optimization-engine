"""
M33.5 - Performance Regression & Benchmark Validation

This suite validates the existing routing algorithms without importing the
Streamlit dashboard. It focuses on reproducible correctness and performance
sanity checks rather than brittle absolute runtime limits.

Run from:
    C:\\Users\\Asus\\src

Command:
    python -m unittest logistics_engine.tests.test_performance_regression -v
"""

import statistics
import time
import unittest


class TestPerformanceRegression(unittest.TestCase):
    """M33.5 routing performance and regression checks."""

    @staticmethod
    def build_graph(size):
        """Build a deterministic sparse logistics-style graph."""
        from logistics_engine.graph import Graph

        graph = Graph()

        # Main connected chain.
        for node in range(size - 1):
            graph.add_edge(node, node + 1, 1.0, bidirectional=True)

        # Short local shortcuts keep the graph sparse while providing
        # multiple candidate routes.
        for node in range(0, size - 2, 2):
            graph.add_edge(node, node + 2, 1.8, bidirectional=True)

        # Longer shortcuts create additional branching.
        step = max(10, size // 20)
        for node in range(0, size - step, step):
            graph.add_edge(node, node + step, float(step) * 0.95,
                           bidirectional=True)

        return graph

    @staticmethod
    def run_dijkstra(graph, source, destination):
        from logistics_engine.routing import dijkstra
        start = time.perf_counter()
        result = dijkstra(graph, source, destination)
        elapsed = time.perf_counter() - start
        return result, elapsed

    @staticmethod
    def run_a_star_zero(graph, source, destination):
        from logistics_engine.routing import a_star
        start = time.perf_counter()
        result = a_star(
            graph,
            [],
            source,
            destination,
            heuristic="zero",
        )
        elapsed = time.perf_counter() - start
        return result, elapsed

    def test_01_small_graph_correctness(self):
        """A* and Dijkstra return the same shortest distance."""
        graph = self.build_graph(50)

        a_result, _ = self.run_a_star_zero(graph, 0, 49)
        d_result, _ = self.run_dijkstra(graph, 0, 49)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertAlmostEqual(a_result.distance, d_result.distance)
        self.assertEqual(a_result.path, d_result.path)

    def test_02_medium_graph_correctness(self):
        """Correctness remains stable on a larger graph."""
        graph = self.build_graph(500)

        a_result, _ = self.run_a_star_zero(graph, 0, 499)
        d_result, _ = self.run_dijkstra(graph, 0, 499)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertAlmostEqual(a_result.distance, d_result.distance)
        self.assertEqual(a_result.path, d_result.path)

    def test_03_a_star_metrics_are_valid(self):
        """A* exposes meaningful search-performance counters."""
        graph = self.build_graph(500)

        result, elapsed = self.run_a_star_zero(graph, 0, 499)

        self.assertIsNotNone(result)
        self.assertGreaterEqual(elapsed, 0.0)
        self.assertGreater(result.nodes_explored, 0)
        self.assertGreaterEqual(result.heap_operations, result.nodes_explored)
        self.assertGreater(len(result.path), 1)
        self.assertGreater(result.distance, 0.0)

    def test_04_dijkstra_runtime_is_measurable(self):
        """Dijkstra completes and reports a finite runtime."""
        graph = self.build_graph(500)

        result, elapsed = self.run_dijkstra(graph, 0, 499)

        self.assertIsNotNone(result)
        self.assertGreaterEqual(elapsed, 0.0)
        self.assertGreater(result.distance, 0.0)

    def test_05_zero_heuristic_a_star_matches_dijkstra(self):
        """Zero-heuristic A* remains behaviorally equivalent to Dijkstra."""
        graph = self.build_graph(1000)

        a_result, _ = self.run_a_star_zero(graph, 0, 999)
        d_result, _ = self.run_dijkstra(graph, 0, 999)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertAlmostEqual(
            a_result.distance,
            d_result.distance,
            places=9,
        )
        self.assertEqual(a_result.path, d_result.path)

    def test_06_repeated_runtime_is_stable(self):
        """Repeated runs complete without pathological runtime variation."""
        graph = self.build_graph(1000)

        a_times = []
        d_times = []

        # Warm-up removes most one-time import/cache effects.
        self.run_a_star_zero(graph, 0, 999)
        self.run_dijkstra(graph, 0, 999)

        for _ in range(5):
            a_result, a_elapsed = self.run_a_star_zero(graph, 0, 999)
            d_result, d_elapsed = self.run_dijkstra(graph, 0, 999)

            self.assertIsNotNone(a_result)
            self.assertIsNotNone(d_result)

            a_times.append(a_elapsed)
            d_times.append(d_elapsed)

        a_median = statistics.median(a_times)
        d_median = statistics.median(d_times)

        self.assertGreater(a_median, 0.0)
        self.assertGreater(d_median, 0.0)

        # Extremely broad sanity bound. This is intentionally not a claim
        # that A* must be faster; hardware and graph shape affect timing.
        self.assertLess(max(a_times), max(1.0, a_median * 20.0))
        self.assertLess(max(d_times), max(1.0, d_median * 20.0))

        print("\nM33.5 repeated runtime benchmark")
        print(f"  A* median:       {a_median:.6f}s")
        print(f"  Dijkstra median: {d_median:.6f}s")
        print(f"  A* runs:         {[round(x, 6) for x in a_times]}")
        print(f"  Dijkstra runs:   {[round(x, 6) for x in d_times]}")

    def test_07_scalability_sanity(self):
        """Routing completes across increasing graph sizes."""
        sizes = [50, 500, 1000, 5000]
        rows = []

        for size in sizes:
            graph = self.build_graph(size)

            a_result, a_elapsed = self.run_a_star_zero(
                graph, 0, size - 1
            )
            d_result, d_elapsed = self.run_dijkstra(
                graph, 0, size - 1
            )

            self.assertIsNotNone(a_result)
            self.assertIsNotNone(d_result)
            self.assertAlmostEqual(
                a_result.distance,
                d_result.distance,
                places=9,
            )
            self.assertGreater(a_result.nodes_explored, 0)
            self.assertGreaterEqual(a_result.heap_operations, 0)

            rows.append(
                (
                    size,
                    a_elapsed,
                    d_elapsed,
                    a_result.nodes_explored,
                    a_result.heap_operations,
                )
            )

        print("\nM33.5 scalability benchmark")
        print(
            "  Nodes | A* Runtime | Dijkstra Runtime | "
            "A* Explored | A* Heap Ops"
        )
        print("  " + "-" * 72)

        for row in rows:
            print(
                f"  {row[0]:5d} | "
                f"{row[1]:10.6f}s | "
                f"{row[2]:16.6f}s | "
                f"{row[3]:11d} | "
                f"{row[4]:11d}"
            )

    def test_08_multiple_queries(self):
        """Multiple source/destination pairs remain correct."""
        graph = self.build_graph(1000)

        queries = [
            (0, 999),
            (10, 700),
            (100, 900),
            (250, 750),
            (400, 600),
        ]

        for source, destination in queries:
            a_result, _ = self.run_a_star_zero(
                graph, source, destination
            )
            d_result, _ = self.run_dijkstra(
                graph, source, destination
            )

            self.assertIsNotNone(a_result)
            self.assertIsNotNone(d_result)
            self.assertAlmostEqual(
                a_result.distance,
                d_result.distance,
                places=9,
            )
            self.assertEqual(a_result.path, d_result.path)

    def test_09_performance_metrics_do_not_degrade_to_invalid_values(self):
        """Performance counters never become negative or non-finite."""
        import math

        graph = self.build_graph(1000)

        a_result, a_elapsed = self.run_a_star_zero(graph, 0, 999)
        d_result, d_elapsed = self.run_dijkstra(graph, 0, 999)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)

        values = [
            a_elapsed,
            d_elapsed,
            float(a_result.distance),
            float(a_result.nodes_explored),
            float(a_result.heap_operations),
        ]

        for value in values:
            self.assertTrue(math.isfinite(value))
            self.assertGreaterEqual(value, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
