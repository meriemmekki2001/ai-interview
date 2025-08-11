import pathlib

from reader import get_text_from_pdf
from extract import extract_esg_info
from evaluate import load_expected_results, compare
from utils import (
    validate_data_directory,
    print_header,
    print_file_status,
    print_summary,
    print_detailed_errors,
    find_pdf_files,
)


def run():
    """
    Process PDF files and compare extracted ESG data against expected results.
    """
    data_path = pathlib.Path("data")
    validate_data_directory(data_path)

    # Load expected results
    try:
        expected_results_path = data_path / "expected_results.json"
        expected_results = load_expected_results(str(expected_results_path))
    except Exception as e:
        print(f"Error loading expected results: {e}")
        return

    # Find PDF files
    pdf_files = find_pdf_files(data_path)
    if not pdf_files:
        return

    print(f"Processing {len(pdf_files)} PDF files...")

    # Results storage
    all_results = {}
    total_score = 0
    processed_files = 0

    print_header()

    for pdf_file in sorted(pdf_files):
        file_key = pdf_file.name

        try:
            # Extract text from PDF
            text = get_text_from_pdf(str(pdf_file))

            if not text.strip():
                print(f"Warning: No text extracted from {pdf_file.name}")
                print_file_status(pdf_file.name, "No text extracted")
                continue

            # Extract ESG information
            try:
                extracted_data = extract_esg_info(text)
            except NotImplementedError:
                print(f"Skipping {pdf_file.name}: extract_esg_info not implemented")
                print_file_status(pdf_file.name, "Not implemented")
                continue
            except Exception as e:
                print(f"Error extracting from {pdf_file.name}: {e}")
                print_file_status(pdf_file.name, "Extraction error")
                continue

            # Get expected results for this file
            if file_key not in expected_results:
                print(f"Warning: No expected results for {pdf_file.name}")
                print_file_status(pdf_file.name, "No expected results")
                continue

            expected_data = expected_results[file_key]

            # Compare results
            comparison = compare(extracted_data, expected_data)

            # Store results
            all_results[file_key] = {
                "file": pdf_file.name,
                "extracted": extracted_data,
                "expected": expected_data,
                "comparison": comparison,
            }

            # Print results
            print_file_status(pdf_file.name, "Processed", comparison)

            total_score += comparison["total_score"]
            processed_files += 1

        except Exception as e:
            print(f"Unexpected error processing {pdf_file.name}: {e}")
            print_file_status(pdf_file.name, "Error")

    # Display summary
    print_summary(processed_files, len(pdf_files), total_score)

    # Display detailed errors for each file
    print_detailed_errors(all_results)


if __name__ == "__main__":
    run()
