import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"
ROUTE_URL = f"{BASE_URL}/route"

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

TOTAL_REQUESTS = 200
MAX_WORKERS = 10
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
    ordered = sorted(values)

    if not ordered:
        return 0.0

    index = int((percentage / 100) * len(ordered))

    if index >= len(ordered):
        index = len(ordered) - 1

    return ordered[index]


def main():
    print("=" * 75)
    print("M33.11 - CONCURRENT API LOAD VALIDATION")
    print("=" * 75)

    print(f"\nTarget API       : {ROUTE_URL}")
    print(f"Total requests   : {TOTAL_REQUESTS}")
    print(f"Concurrent workers: {MAX_WORKERS}")

    print("\nRoute distribution:")

    requests = []

    for i in range(TOTAL_REQUESTS):
        source, destination = ROUTE_CASES[i % len(ROUTE_CASES)]
        requests.append((source, destination))

    for source, destination in ROUTE_CASES:
        count = sum(
            1
            for item in requests
            if item == (source, destination)
        )
        print(f"  {source:>3} -> {destination:<3}: {count} requests")

    print("\nStarting concurrent load test...\n")

    results = []

    benchmark_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(
                send_route_request,
                source,
                destination,
            )
            for source, destination in requests
        ]

        for future in as_completed(futures):
            results.append(future.result())

    total_elapsed = time.perf_counter() - benchmark_start

    successful = sum(
        1 for result in results if result["success"]
    )

    failed = len(results) - successful

    latencies = [
        result["latency"]
        for result in results
        if result["success"]
    ]

    status_codes = {}

    for result in results:
        status = result["status"]
        status_codes[status] = status_codes.get(status, 0) + 1

    print("-" * 75)
    print("CONCURRENT LOAD RESULTS")
    print("-" * 75)

    print(f"Total requests       : {len(results)}")
    print(f"Successful requests  : {successful}")
    print(f"Failed requests      : {failed}")

    print(f"Total test time      : {total_elapsed:.3f} sec")

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

    if successful == TOTAL_REQUESTS and failed == 0:
        print("M33.11 CONCURRENT LOAD TEST: PASS")
    else:
        print("M33.11 CONCURRENT LOAD TEST: REVIEW REQUIRED")

    print("=" * 75)


if __name__ == "__main__":
    main()