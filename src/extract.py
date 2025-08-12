import os
import json
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from schema import DocESG



load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_esg_info(text: str) -> Dict[str, Any]:
    """
    Extract ESG data from raw text using OpenAI API with enforced JSON schema.
    Following the prompting principles including: 
    - Asking for a structured output
    - Instructing the model with the steps 
    - Few shot prompting (guiding the llm through examples)

    """
    
    json_schema = DocESG.model_json_schema()

    system_prompt = """
    You are an expert ESG report parser.
    Your task is to extract ESG-related information from unstructured company reports
    and return it in the EXACT JSON format defined by the provided schema.

    Rules for extraction:
    1. Company identification and reporting year — find the company's legal name and the reporting year.
    2. Board composition and governance structure — list board members, roles, and whether they are independent, executive, or non-independent.
    3. GHG emissions data — extract Scope 1, Scope 2 (market/location-based), Scope 3 emissions.
       Ensure correct numeric parsing and handle units (e.g., "tCO2e", "tonnes").
    4. Policies — detect policy mentions, accounting for synonyms.
       Example: "Speak-Up policy" → whistleblowing = true.
    5. Missing data — if a value cannot be found, set it explicitly to null.
    6. Be faithful to the report — do not guess values not present in the text.
    7. All extracted data MUST match the schema's field names and structure exactly.

    Return ONLY the JSON object as output. No extra text.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "DocESGSchema",
                "schema": json_schema
            }
        },
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    data = json.loads(response.choices[0].message.content)
    
    return DocESG(**data).model_dump()
