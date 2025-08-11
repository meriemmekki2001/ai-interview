# AI Interview – ESG PDF Extractor

A minimal codebase that reads PDF files, extracts ESG facts into structured data, compares results to expected outputs, and provides clear scoring and feedback. Designed for clarity, testability, and candidate autonomy.

## What You Need to Build

Your task is to implement the `extract_esg_info()` function in `src/extract.py`. This function should:

1. **Parse unstructured PDF text** and extract ESG information
2. **Return structured data** matching the `DocESG` schema
3. **Handle missing data gracefully** with `None` values
4. **Recognize policy synonyms** (e.g., "Speak-Up" → whistleblowing)
5. **Parse numeric data** with proper unit handling

To do so you can rely on OpenAI api (we will provide you with an API key).
You are free to use the libraries you want for this project ([openai-python](https://github.com/openai/openai-python),
[langchain](https://www.langchain.com/), ...).

## Quick Start

```bash
# Set up environment
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the extractor
python src/cli.py
```

## Project Structure

```
ai-quality-interview/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── data/                        # Input files and expected results
│   ├── BoardDeck.pdf
│   ├── ESG_Report.pdf
│   ├── Sustainability_Policy_Pack.pdf
│   └── expected_results.json    # Ground truth for all files
└── src/                         # Source code
    ├── __init__.py             # Python package initialization
    ├── reader.py               # PDF text extraction (✓ implemented)
    ├── extract.py              # ESG info extraction (⚠️ YOUR TASK)
    ├── schema.py               # Pydantic data models (✓ implemented)
    ├── evaluate.py             # Scoring and comparison (✓ implemented)
    ├── utils.py                # Utility functions for CLI (✓ implemented)
    └── cli.py                  # Command-line interface (✓ implemented)
```

## Data Schema

Your `extract_esg_info()` function should return a dictionary matching this structure:

```python
{
    "company": "Company Name",           # string
    "year": 2024,                       # int
    "board": {
        "chair": {
            "name": "John Doe",          # string
            "role": "Chairman",          # string
            "independence": "Independent" # string or None
        },
        "members": [                     # list of board members
            {"name": "...", "role": "...", "independence": "..."}
        ],
        "counts": {                      # dict with counts
            "total": 8,                  # int
            "independent": 6,            # int
            "women": 2                   # int
        }
    },
    "ghg": {                            # greenhouse gas emissions
        "base_year": 2020,              # int or None
        "scope1_tco2e": 1250.5,         # float or None (tonnes CO2 equivalent)
        "scope2_market_tco2e": 890.2,   # float or None (market-based)
        "scope2_location_tco2e": 920.8, # float or None (location-based)
        "scope3_tco2e": 15600.0,        # float or None
        "total_tco2e": 17740.7,         # float or None
        "intensity_tco2e_per_eur_m": 12.4 # float or None (per EUR million)
    },
    "policies": {                       # governance policies
        "anti_corruption": True,        # bool or None
        "whistleblowing": True,         # bool or None
        "human_rights": False,          # bool or None
        "climate_policy": True,         # bool or None
        "dei_policy": None,             # bool or None (diversity/equity/inclusion)
        "assurance": "Limited"          # string or None ("Limited"/"Reasonable")
    }
}
```

## Scoring System (100 points total)

1. **Parsing Correctness (60 pts)**: Accurate extraction of numeric and text fields

   - Numeric fields: exact match within 5% tolerance
   - Strings: fuzzy matching with 90%+ similarity threshold
   - Booleans: exact match

2. **Coverage (20 pts)**: Percentage of expected non-null fields successfully extracted

3. **Robustness (10 pts)**: Recognition of policy synonyms and edge cases

   - "Speak-Up" → `whistleblowing`
   - "Anti-bribery" → `anti_corruption`
   - "Labour rights" → `human_rights`
   - "Diversity" → `dei_policy`

4. **Output Hygiene (10 pts)**: Valid schema compliance and error handling

## Need Help?

- Review `src/evaluate.py` to understand the scoring logic
- Look at `data/expected_results.json` to see target output format
- Examine `src/utils.py` for display and validation utilities
- Check `src/schema.py` for the complete data model structure
- Run `python src/cli.py` to see current extraction results and detailed error messages

Good luck! 🚀
