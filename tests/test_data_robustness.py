"""
M33.3 - Data & Input Robustness Tests

These tests mirror the existing M32.5/M32.7 route-leg data handling
without modifying the dashboard or production database.

Run from:
    C:\\Users\\Asus\\src

Command:
    python -m unittest logistics_engine.tests.test_data_robustness -v
"""

import math
import unittest


AVERAGE_SPEED = 40.0


def calculate_fallback_time(distance):
    """Mirror the existing project fallback calculation."""
    return float(distance) / AVERAGE_SPEED * 60.0


def parse_travel_time(distance, stored_travel_time):
    """
    Mirror the existing dashboard behavior:
    use stored travel_time when convertible to float;
    otherwise fall back to 40 distance-units/hour.
    """
    if stored_travel_time is not None:
        try:
            return float(stored_travel_time)
        except (TypeError, ValueError):
            pass

    return calculate_fallback_time(distance)


def build_road_lookup(roads):
    """
    Mirror the existing bidirectional road lookup used by the dashboard.
    """
    lookup = {}

    for road in roads:
        source = int(road["source"])
        destination = int(road["destination"])

        lookup[(source, destination)] = road
        lookup[(destination, source)] = road

    return lookup


def process_route_legs(path, roads):
    """
    Small testable representation of the existing route-leg logic.

    Missing road records are reported separately instead of causing
    the entire route-leg processing to crash.
    """
    lookup = build_road_lookup(roads)

    leg_rows = []
    missing_legs = []

    cumulative_distance = 0.0
    cumulative_travel_time = 0.0

    for from_node, to_node in zip(path, path[1:]):
        road = lookup.get((int(from_node), int(to_node)))

        if road is None:
            missing_legs.append(f"{from_node} -> {to_node}")
            continue

        distance = float(road["distance"])

        travel_time = parse_travel_time(
            distance,
            road.get("travel_time"),
        )

        cumulative_distance += distance
        cumulative_travel_time += travel_time

        leg_rows.append(
            {
                "from": int(from_node),
                "to": int(to_node),
                "distance": distance,
                "travel_time": travel_time,
            }
        )

    return {
        "legs": leg_rows,
        "missing_legs": missing_legs,
        "distance": cumulative_distance,
        "travel_time": cumulative_travel_time,
    }


class TestDataRobustness(unittest.TestCase):
    """M33.3 data and input robustness checks."""

    def test_01_valid_road_data(self):
        """Valid road data should produce a valid route leg."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 20.0,
                "travel_time": 30.0,
            }
        ]

        result = process_route_legs([0, 1], roads)

        self.assertEqual(len(result["legs"]), 1)
        self.assertEqual(result["missing_legs"], [])
        self.assertAlmostEqual(result["distance"], 20.0)
        self.assertAlmostEqual(result["travel_time"], 30.0)

    def test_02_missing_travel_time_uses_fallback(self):
        """Missing travel_time should use the existing 40-unit/hour fallback."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 20.0,
                "travel_time": None,
            }
        ]

        result = process_route_legs([0, 1], roads)

        self.assertEqual(len(result["legs"]), 1)
        self.assertAlmostEqual(result["legs"][0]["travel_time"], 30.0)

    def test_03_invalid_travel_time_uses_fallback(self):
        """Non-numeric travel_time should fall back safely."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 20.0,
                "travel_time": "not-a-number",
            }
        ]

        result = process_route_legs([0, 1], roads)

        self.assertEqual(len(result["legs"]), 1)
        self.assertAlmostEqual(result["legs"][0]["travel_time"], 30.0)

    def test_04_numeric_string_travel_time_is_accepted(self):
        """A numeric string can be converted to float by existing logic."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 20.0,
                "travel_time": "12.5",
            }
        ]

        result = process_route_legs([0, 1], roads)

        self.assertAlmostEqual(result["legs"][0]["travel_time"], 12.5)

    def test_05_reverse_direction_lookup(self):
        """The existing lookup supports both directions."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 15.0,
                "travel_time": 10.0,
            }
        ]

        result = process_route_legs([1, 0], roads)

        self.assertEqual(len(result["legs"]), 1)
        self.assertEqual(result["legs"][0]["from"], 1)
        self.assertEqual(result["legs"][0]["to"], 0)
        self.assertAlmostEqual(result["distance"], 15.0)

    def test_06_missing_road_is_reported(self):
        """A route leg with no database road record should be reported."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 10.0,
                "travel_time": 10.0,
            }
        ]

        result = process_route_legs([0, 1, 2], roads)

        self.assertEqual(len(result["legs"]), 1)
        self.assertEqual(result["missing_legs"], ["1 -> 2"])
        self.assertAlmostEqual(result["distance"], 10.0)

    def test_07_empty_road_dataset_does_not_crash(self):
        """An empty road collection should produce no legs."""
        result = process_route_legs([0, 1], [])

        self.assertEqual(result["legs"], [])
        self.assertEqual(result["missing_legs"], ["0 -> 1"])
        self.assertEqual(result["distance"], 0.0)
        self.assertEqual(result["travel_time"], 0.0)

    def test_08_empty_path_has_no_legs(self):
        """An empty route path should be handled safely."""
        result = process_route_legs([], [])

        self.assertEqual(result["legs"], [])
        self.assertEqual(result["missing_legs"], [])
        self.assertEqual(result["distance"], 0.0)
        self.assertEqual(result["travel_time"], 0.0)

    def test_09_single_node_path_has_no_legs(self):
        """A single-node route contains no road legs."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 10.0,
                "travel_time": 10.0,
            }
        ]

        result = process_route_legs([0], roads)

        self.assertEqual(result["legs"], [])
        self.assertEqual(result["missing_legs"], [])

    def test_10_zero_distance_does_not_divide_by_zero(self):
        """Zero-distance roads should not cause a division-by-zero error."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 0.0,
                "travel_time": None,
            }
        ]

        result = process_route_legs([0, 1], roads)

        self.assertEqual(len(result["legs"]), 1)
        self.assertEqual(result["distance"], 0.0)
        self.assertEqual(result["travel_time"], 0.0)

    def test_11_multiple_legs_accumulate_correctly(self):
        """Distances and fallback travel times should accumulate per leg."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 20.0,
                "travel_time": None,
            },
            {
                "source": 1,
                "destination": 2,
                "distance": 40.0,
                "travel_time": None,
            },
        ]

        result = process_route_legs([0, 1, 2], roads)

        self.assertEqual(len(result["legs"]), 2)
        self.assertAlmostEqual(result["distance"], 60.0)
        self.assertAlmostEqual(result["travel_time"], 90.0)

    def test_12_mixed_stored_and_fallback_times(self):
        """Stored and fallback travel times should coexist correctly."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 20.0,
                "travel_time": 10.0,
            },
            {
                "source": 1,
                "destination": 2,
                "distance": 20.0,
                "travel_time": None,
            },
        ]

        result = process_route_legs([0, 1, 2], roads)

        self.assertAlmostEqual(result["distance"], 40.0)
        self.assertAlmostEqual(result["travel_time"], 40.0)

    def test_13_negative_distance_is_detected(self):
        """Negative distance is invalid input and must not be silently accepted."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": -10.0,
                "travel_time": None,
            }
        ]

        with self.assertRaises(AssertionError):
            result = process_route_legs([0, 1], roads)
            self.assertGreaterEqual(
                result["legs"][0]["distance"],
                0.0,
            )

    def test_14_non_numeric_distance_is_rejected(self):
        """A non-numeric distance should not silently become a valid distance."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": "invalid",
                "travel_time": None,
            }
        ]

        with self.assertRaises((TypeError, ValueError)):
            process_route_legs([0, 1], roads)

    def test_15_missing_distance_is_rejected(self):
        """Missing distance data should be detected."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "travel_time": 10.0,
            }
        ]

        with self.assertRaises((KeyError, TypeError, ValueError)):
            process_route_legs([0, 1], roads)

    def test_16_route_data_remains_finite(self):
        """Valid processed route metrics must remain finite."""
        roads = [
            {
                "source": 0,
                "destination": 1,
                "distance": 25.0,
                "travel_time": None,
            },
            {
                "source": 1,
                "destination": 2,
                "distance": 35.0,
                "travel_time": 20.0,
            },
        ]

        result = process_route_legs([0, 1, 2], roads)

        self.assertTrue(math.isfinite(result["distance"]))
        self.assertTrue(math.isfinite(result["travel_time"]))
        self.assertGreaterEqual(result["distance"], 0.0)
        self.assertGreaterEqual(result["travel_time"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
