import json
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"
ROUTE_URL = f"{BASE_URL}/route"

# Valid routing nodes in the current routing graph.
ROUTE_CASES = [
    (0, 3),
    (0, 4),
    (0, 10),
    (1, 3),
    (2, 8),
    (3, 12),
    (4, 15),
    (5, 20),
    (10, 25),
    (15, 30),
]

REQUESTS_PER_CASE = 50
TIMEOUT_SECONDS = 10


def send_route_request(source, destination):
    payload = json.dumps(
        {
            "source": source,
            "destination": destination,
        }
    ).encode("utf-8")

    request = Request(
        ROUTE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
            elapsed = time.perf_counter() - start

            return {
                "success": response.status == 200,
                "status": response.status,
                "latency": elapsed,
                "body": json.loads(body),
            }

    except HTTPError as exc:
        elapsed = time.perf_counter() - start

        return {
            "success": False,
            "status": exc.code,
            "latency": elapsed,
            "body": exc.read().decode("utf-8"),
        }

    except URLError as exc:
        elapsed = time.perf_counter() - start

        return {
            "success": False,
            "status": None,
            "latency": elapsed,
            "body": str(exc),
        }


def percentile(values, percentage):
    if not values:
        return 0.0

    ordered = sorted(values)

    index = int((percentage / 100) * len(ordered))

    if index >= len(ordered):
        index = len(ordered) - 1

    return ordered[index]


def main():
    total_expected = len(ROUTE_CASES) * REQUESTS_PER_CASE

    print("=" * 75)
    print("M33.11 - SUSTAINED API LOAD VALIDATION")
    print("=" * 75)

    print(f"\nTarget API          : {ROUTE_URL}")
    print(f"Route combinations  : {len(ROUTE_CASES)}")
    print(f"Requests per route  : {REQUESTS_PER_CASE}")
    print(f"Total requests      : {total_expected}")

    print("\nRoute cases:")

    for source, destination in ROUTE_CASES:
        print(f"  {source:>3} -> {destination:<3}")

    print("\nStarting sustained load test...\n")

    latencies = []
    successful = 0
    failed = 0
    status_codes = {}

    benchmark_start = time.perf_counter()

    for source, destination in ROUTE_CASES:

        case_latencies = []
        case_success = 0
        case_failed = 0

        for _ in range(REQUESTS_PER_CASE):

            result = send_route_request(source, destination)

            status = result["status"]

            status_codes[status] = status_codes.get(status, 0) + 1

            if result["success"]:
                successful += 1
                case_success += 1
                latencies.append(result["latency"])
                case_latencies.append(result["latency"])
            else:
                failed += 1
                case_failed += 1

        if case_latencies:
            print(
                f"{source:>3} -> {destination:<3} | "
                f"success={case_success:>2} | "
                f"failed={case_failed:>2} | "
                f"avg={statistics.mean(case_latencies) * 1000:>8.3f} ms | "
                f"max={max(case_latencies) * 1000:>8.3f} ms"
            )

    total_elapsed = time.perf_counter() - benchmark_start

    print("\n" + "-" * 75)
    print("SUSTAINED LOAD RESULTS")
    print("-" * 75)

    print(f"Total requests       : {total_expected}")
    print(f"Successful requests  : {successful}")
    print(f"Failed requests      : {failed}")

    if latencies:

        average_ms = statistics.mean(latencies) * 1000
        median_ms = statistics.median(latencies) * 1000
        minimum_ms = min(latencies) * 1000
        maximum_ms = max(latencies) * 1000

        p90_ms = percentile(latencies, 90) * 1000
        p95_ms = percentile(latencies, 95) * 1000
        p99_ms = percentile(latencies, 99) * 1000

        throughput = successful / total_elapsed

        print(f"Average latency      : {average_ms:.3f} ms")
        print(f"Median latency       : {median_ms:.3f} ms")
        print(f"Minimum latency      : {minimum_ms:.3f} ms")
        print(f"Maximum latency      : {maximum_ms:.3f} ms")
        print(f"P90 latency          : {p90_ms:.3f} ms")
        print(f"P95 latency          : {p95_ms:.3f} ms")
        print(f"P99 latency          : {p99_ms:.3f} ms")
        print(f"Throughput           : {throughput:.2f} requests/sec")

    print("\nHTTP status codes:")

    for status, count in sorted(
        status_codes.items(),
        key=lambda item: str(item[0])
    ):
        print(f"  {status}: {count}")

    print("\n" + "-" * 75)

    if successful == total_expected and failed == 0:
        print("M33.11 SUSTAINED LOAD TEST: PASS")
    else:
        print("M33.11 SUSTAINED LOAD TEST: REVIEW REQUIRED")

    print("=" * 75)


if __name__ == "__main__":
    main()