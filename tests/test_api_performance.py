import json
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"
ROUTE_URL = f"{BASE_URL}/route"

# Known valid routing nodes from the current project.
TEST_REQUESTS = [
    {"source": 0, "destination": 3},
    {"source": 0, "destination": 4},
    {"source": 0, "destination": 10},
    {"source": 1, "destination": 3},
    {"source": 2, "destination": 8},
]

REQUESTS_PER_CASE = 20
TIMEOUT_SECONDS = 10


def send_route_request(source: int, destination: int):
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
                "success": True,
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


def main():
    print("=" * 70)
    print("M33.11 - API PERFORMANCE & LOAD VALIDATION")
    print("=" * 70)

    print("\nTarget:")
    print(ROUTE_URL)

    total_requests = len(TEST_REQUESTS) * REQUESTS_PER_CASE

    print(f"\nTest cases           : {len(TEST_REQUESTS)}")
    print(f"Requests per case    : {REQUESTS_PER_CASE}")
    print(f"Total requests       : {total_requests}")

    latencies = []
    successful = 0
    failed = 0
    status_codes = {}

    print("\nRunning benchmark...\n")

    benchmark_start = time.perf_counter()

    for source, destination in [
        (item["source"], item["destination"])
        for item in TEST_REQUESTS
    ]:
        case_latencies = []

        for _ in range(REQUESTS_PER_CASE):
            result = send_route_request(source, destination)

            status = result["status"]
            status_codes[status] = status_codes.get(status, 0) + 1

            if result["success"] and status == 200:
                successful += 1
                latencies.append(result["latency"])
                case_latencies.append(result["latency"])
            else:
                failed += 1

        if case_latencies:
            print(
                f"{source:>3} -> {destination:<3} | "
                f"requests={len(case_latencies):>2} | "
                f"avg={statistics.mean(case_latencies) * 1000:>8.3f} ms | "
                f"min={min(case_latencies) * 1000:>8.3f} ms | "
                f"max={max(case_latencies) * 1000:>8.3f} ms"
            )

    total_elapsed = time.perf_counter() - benchmark_start

    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)

    print(f"Total requests       : {total_requests}")
    print(f"Successful requests  : {successful}")
    print(f"Failed requests      : {failed}")

    if latencies:
        average_ms = statistics.mean(latencies) * 1000
        median_ms = statistics.median(latencies) * 1000
        minimum_ms = min(latencies) * 1000
        maximum_ms = max(latencies) * 1000

        sorted_latencies = sorted(latencies)

        p95_index = min(
            len(sorted_latencies) - 1,
            int(len(sorted_latencies) * 0.95)
        )

        p99_index = min(
            len(sorted_latencies) - 1,
            int(len(sorted_latencies) * 0.99)
        )

        p95_ms = sorted_latencies[p95_index] * 1000
        p99_ms = sorted_latencies[p99_index] * 1000

        throughput = successful / total_elapsed

        print(f"Average latency      : {average_ms:.3f} ms")
        print(f"Median latency       : {median_ms:.3f} ms")
        print(f"Minimum latency      : {minimum_ms:.3f} ms")
        print(f"Maximum latency      : {maximum_ms:.3f} ms")
        print(f"P95 latency          : {p95_ms:.3f} ms")
        print(f"P99 latency          : {p99_ms:.3f} ms")
        print(f"Throughput           : {throughput:.2f} requests/sec")

    print("\nHTTP status codes:")

    for status, count in sorted(status_codes.items(), key=lambda x: str(x[0])):
        print(f"  {status}: {count}")

    print("\n" + "-" * 70)

    if successful == total_requests and failed == 0:
        print("M33.11 BASIC PERFORMANCE TEST: PASS")
    else:
        print("M33.11 BASIC PERFORMANCE TEST: REVIEW REQUIRED")

    print("=" * 70)


if __name__ == "__main__":
    main()