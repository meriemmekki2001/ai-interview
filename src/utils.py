import pathlib
from typing import Dict, Any, List


def validate_data_directory(data_path: pathlib.Path) -> None:
    """Validate that the data directory and expected results file exist."""
    if not data_path.exists():
        print("Error: Data directory 'data' does not exist")
        raise SystemExit(1)

    expected_results_path = data_path / "expected_results.json"
    if not expected_results_path.exists():
        print(f"Error: Expected results file not found at {expected_results_path}")
        raise SystemExit(1)


def print_header() -> None:
    """Print the results table header."""
    print("\nESG Extraction Results:")
    print("-" * 80)
    print(
        f"{'File':<40} {'Score':<8} {'Parsing':<8} {'Coverage':<8} {'Robustness':<8} {'Schema':<8} {'Status'}"
    )
    print("-" * 80)


def print_file_status(filename: str, status: str, scores: Dict[str, Any] = None) -> None:
    """Print the status of a processed file."""
    if scores is None:
        # Default N/A or 0 values for different status types
        if status in ["Not implemented", "No expected results"]:
            score_values = ['N/A'] * 5
        else:
            score_values = ['0'] * 5
        print(f"{filename:<40} {score_values[0]:<8} {score_values[1]:<8} {score_values[2]:<8} {score_values[3]:<8} {score_values[4]:<8} {status}")
    else:
        # Print actual scores
        breakdown = scores["breakdown"]
        print(
            f"{filename:<40} {scores['total_score']:<8.1f} {breakdown['parsing_correctness']:<8.1f} {breakdown['coverage']:<8.1f} {breakdown['robustness']:<8.1f} {breakdown['output_hygiene']:<8.1f} Processed"
        )


def interpret_score(avg_score: float) -> str:
    """Return a performance interpretation based on the average score."""
    if avg_score >= 90:
        return "Excellent performance!"
    elif avg_score >= 70:
        return "Good performance!"
    elif avg_score >= 50:
        return "Needs improvement"
    else:
        return "Significant issues found"


def print_summary(processed_files: int, total_files: int, total_score: float) -> None:
    """Print the processing summary."""
    print("\nSummary:")
    print("-" * 40)
    if processed_files > 0:
        avg_score = total_score / processed_files
        print(f"Files processed: {processed_files}/{total_files}")
        print(f"Average score: {avg_score:.1f}/100")
        print(interpret_score(avg_score))
    else:
        print(f"Files processed: 0/{total_files}")
        print("No files were successfully processed")


def print_detailed_errors(all_results: Dict[str, Any]) -> None:
    """Print detailed error information for each file."""
    if not all_results:
        return
        
    print("\nDetailed Issues:")
    print("-" * 40)

    for file_key, result in all_results.items():
        comparison = result["comparison"]
        if (
            comparison["details"]["incorrect_fields"]
            or not comparison["details"]["schema_valid"]
        ):
            print(f"\nIssues in {result['file']}:")

            # Schema errors
            if not comparison["details"]["schema_valid"]:
                print(
                    f"  Schema validation failed: {comparison['details']['schema_errors']}"
                )

            # Field errors
            for field_error in comparison["details"]["incorrect_fields"]:
                print(f"  ✗ {field_error['field']}: {field_error['error']}")


def find_pdf_files(data_path: pathlib.Path) -> List[pathlib.Path]:
    """Find all PDF files in the data directory."""
    pdf_files = list(data_path.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in data")
    return pdf_files