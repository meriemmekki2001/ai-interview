import json
from typing import Dict, Any, Tuple
from rapidfuzz import fuzz
from pydantic import ValidationError

from schema import DocESG


def load_expected_results(path: str) -> Dict[str, Dict[str, Any]]:
    """Load expected results from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def compare_values(
    predicted: Any, expected: Any, field_name: str
) -> Tuple[bool, float, str]:
    """
    Compare a single field value between predicted and expected results.

    Returns:
        Tuple of (is_correct, similarity_score, error_message)
    """
    if expected is None and predicted is None:
        return True, 1.0, ""

    if expected is None:
        return True, 1.0, ""  # Optional field, no penalty

    if predicted is None:
        return False, 0.0, f"Missing required field: {field_name}"

    # Boolean comparison (check first since bool is subclass of int)
    if isinstance(expected, bool) and isinstance(predicted, bool):
        if expected == predicted:
            return True, 1.0, ""
        else:
            return False, 0.0, f"Boolean mismatch: expected {expected}, got {predicted}"

    # Numeric comparison with tolerance
    if isinstance(expected, (int, float)) and isinstance(predicted, (int, float)):
        tolerance = abs(expected) * 0.05 if expected != 0 else 0.01  # 5% tolerance
        diff = abs(expected - predicted)
        if diff <= tolerance:
            return True, 1.0, ""
        else:
            return False, 0.0, f"Numeric mismatch: expected {expected}, got {predicted}"

    # String comparison with fuzzy matching
    if isinstance(expected, str) and isinstance(predicted, str):
        ratio = fuzz.ratio(expected.lower(), predicted.lower()) / 100.0
        if ratio >= 0.9:  # 90% similarity threshold
            return True, ratio, ""
        else:
            return (
                False,
                ratio,
                f"String mismatch: expected '{expected}', got '{predicted}'",
            )

    # Exact match for other types
    if expected == predicted:
        return True, 1.0, ""
    else:
        return (
            False,
            0.0,
            f"Type/value mismatch: expected {expected} ({type(expected)}), got {predicted} ({type(predicted)})",
        )


def flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested dictionary for easier comparison."""
    result = {}
    for key, value in d.items():
        new_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_dict(value, new_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    result.update(flatten_dict(item, f"{new_key}[{i}]"))
                else:
                    result[f"{new_key}[{i}]"] = item
        else:
            result[new_key] = value
    return result


def check_policy_synonyms(predicted: Dict[str, Any]) -> int:
    """
    Award bonus points for handling policy synonyms correctly.
    Returns additional points (0-10) for synonym recognition.
    """
    synonym_bonus = 0
    policies = predicted.get("policies", {})
    if not policies:
        return 0

    # Check for common synonyms that should map to our standard fields
    synonym_mappings = {
        "whistleblowing": [
            "speak-up",
            "speak up",
            "ethics hotline",
            "reporting concerns",
        ],
        "anti_corruption": ["anti-bribery", "integrity", "ethical conduct"],
        "human_rights": ["labour rights", "worker rights", "social responsibility"],
        "dei_policy": ["diversity", "inclusion", "equality", "diverse workforce"],
    }

    # Award 2.5 points per correctly identified synonym
    for standard_field, synonyms in synonym_mappings.items():
        if policies.get(standard_field) is True:
            synonym_bonus += 2.5

    return min(synonym_bonus, 10)  # Cap at 10 points


def calculate_coverage_score(
    predicted: Dict[str, Any], expected: Dict[str, Any]
) -> float:
    """Calculate coverage score based on non-null expected fields returned."""
    predicted_flat = flatten_dict(predicted)
    expected_flat = flatten_dict(expected)

    expected_non_null = {k: v for k, v in expected_flat.items() if v is not None}
    if not expected_non_null:
        return 20.0  # Full coverage score if no expected fields

    covered_fields = sum(
        1 for k in expected_non_null.keys() if predicted_flat.get(k) is not None
    )
    coverage_ratio = covered_fields / len(expected_non_null)
    return coverage_ratio * 20.0  # 20 points max for coverage


def validate_schema(predicted: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate that predicted results conform to DocESG schema."""
    try:
        DocESG(**predicted)
        return True, ""
    except ValidationError as e:
        return False, str(e)


def compare(predicted: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare predicted vs expected results and return scoring details.

    Scoring breakdown (100 points total):
    - Parsing correctness: 60 points
    - Coverage: 20 points
    - Robustness (synonyms): 10 points
    - Output hygiene (schema validation): 10 points

    Returns:
        Dictionary with score, breakdown, and detailed differences
    """
    result = {
        "total_score": 0,
        "breakdown": {
            "parsing_correctness": 0,
            "coverage": 0,
            "robustness": 0,
            "output_hygiene": 0,
        },
        "details": {
            "correct_fields": [],
            "incorrect_fields": [],
            "missing_fields": [],
            "schema_valid": True,
            "schema_errors": "",
        },
    }

    # 1. Schema validation (10 points)
    schema_valid, schema_error = validate_schema(predicted)
    result["details"]["schema_valid"] = schema_valid
    result["details"]["schema_errors"] = schema_error
    result["breakdown"]["output_hygiene"] = 10 if schema_valid else 0

    # 2. Field-by-field comparison for parsing correctness (60 points)
    predicted_flat = flatten_dict(predicted)
    expected_flat = flatten_dict(expected)

    total_expected_fields = len([v for v in expected_flat.values() if v is not None])
    correct_fields = 0

    for field, expected_value in expected_flat.items():
        if expected_value is None:
            continue  # Skip optional fields

        predicted_value = predicted_flat.get(field)
        is_correct, similarity, error_msg = compare_values(
            predicted_value, expected_value, field
        )

        if is_correct:
            correct_fields += 1
            result["details"]["correct_fields"].append(
                {"field": field, "value": predicted_value, "similarity": similarity}
            )
        else:
            result["details"]["incorrect_fields"].append(
                {
                    "field": field,
                    "expected": expected_value,
                    "predicted": predicted_value,
                    "error": error_msg,
                    "similarity": similarity,
                }
            )

    if total_expected_fields > 0:
        parsing_score = (correct_fields / total_expected_fields) * 60
        result["breakdown"]["parsing_correctness"] = parsing_score

    # 3. Coverage score (20 points)
    coverage_score = calculate_coverage_score(predicted, expected)
    result["breakdown"]["coverage"] = coverage_score

    # 4. Robustness score - synonym handling (10 points)
    robustness_score = check_policy_synonyms(predicted)
    result["breakdown"]["robustness"] = robustness_score

    # Calculate total score
    result["total_score"] = sum(result["breakdown"].values())

    return result
