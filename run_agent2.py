import argparse
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from agent2 import SeverityClassifier

SAMPLE_CASES = [
    {'status': 'success', 'name': '1BWX_PG_hp', 'original_sequence': 'KFSQWNMINKVGHRVESARHLHVLQKDMENLESLALVGLSGNGSGGNGSG', 'anomaly_z_score': 0.26795491576194763, 'sequence_3di': 'kfsqwnminkvghrvesarhlhvlqkdmenleslalvglsgngsggngsg'}
]

def run_health_check():
    """Verify API connectivity."""
    print("Running API health check...")
    classifier = SeverityClassifier()
    ok = classifier.health_check()
    status = "PASS" if ok else "FAIL"
    print(f"Health check: {status}")
    return ok


def run_classification(sequence_3di: str, anomaly_z_score: float,
                    original_sequence: str | None = None, name: str = ""):
    """Run a single classification and print results."""
    classifier = SeverityClassifier()

    if name:
        print(f"\n{'-' * 60}")
        print(f"  Test Case: {name}")
        print(f"{'-' * 60}")

    print(f"  3Di Sequence : {sequence_3di[:50]}{'...' if len(sequence_3di) > 50 else ''}")
    print(f"  Z-Score      : {anomaly_z_score}")
    print()

    result = classifier.classify(
        sequence_3di=sequence_3di,
        anomaly_z_score=anomaly_z_score,
        original_sequence=original_sequence,
    )

    print(result)
    print()

    return result


def run_test_suite():


    results = []
    for case in SAMPLE_CASES:
        result = run_classification(
            sequence_3di=case["sequence_3di"],
            anomaly_z_score=case["anomaly_z_score"],
            original_sequence=case.get("original_sequence"),
            name=case["name"],
        )
        results.append({"name": case["name"], **result.to_dict()})

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"  {r['name']}")
        print(f"    -> {r['severity_label']} (confidence: {r['confidence']:.2%})")
    print("=" * 60)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Protein Misfolding Severity Classifier"
    )
    parser.add_argument("--health", action="store_true", help="Run API health check")
    parser.add_argument("--sequence", type=str, help="3Di structural sequence")
    parser.add_argument("--zscore", type=float, help="Anomaly Z-score from Agent 1")
    parser.add_argument("--original", type=str, default=None,
                        help="Original amino acid sequence (optional)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.health:
        ok = run_health_check()
        sys.exit(0 if ok else 1)

    if args.sequence and args.zscore is not None:
        result = run_classification(
            sequence_3di=args.sequence,
            anomaly_z_score=args.zscore,
            original_sequence=args.original,
        )
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0)

    if args.sequence or args.zscore is not None:
        parser.error("Both --sequence and --zscore are required together.")

    run_test_suite()


if __name__ == "__main__":
    main()
