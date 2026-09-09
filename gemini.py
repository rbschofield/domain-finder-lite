"""
Domain Finder Lite

Gemini is optional.

The main application will continue to work if:
    - --ai is not specified
    - GEMINI_API_KEY is not set
    - Gemini is unavailable
"""

import os
import re

from google import genai
from google.genai import types

os.environ["GEMINI_API_KEY"] = "{your-gemini-api-key}"

# A relatively small, fast model is appropriate for name generation.
MODEL_NAME = "gemini-2.5-flash"


def get_api_key() -> str | None:
    """Return the Gemini API key from the environment."""

    return os.environ.get("GEMINI_API_KEY")


def clean_candidate(name: str) -> str | None:
    """
    Convert a Gemini-generated name into a clean domain name.

    Examples:

        "Cyber Mind"       -> "cybermind.com"
        "Cyber-Mind"       -> "cybermind.com"
        "cybermind.com"    -> "cybermind.com"
    """

    name = name.strip().lower()

    # Remove Markdown formatting.
    name = re.sub(r"[*_`]", "", name)

    # Remove a leading number/bullet.
    name = re.sub(r"^\d+[\.\)\-:\s]+", "", name)

    # Remove common explanatory text.
    name = name.strip()

    # Remove protocol if Gemini gives us a URL.
    name = re.sub(r"^https?://", "", name)

    # Remove www.
    name = re.sub(r"^www\.", "", name)

    # Remove .com if Gemini included it.
    if name.endswith(".com"):
        name = name[:-4]

    # Keep only the domain-name portion.
    name = name.split("/")[0]

    # Remove spaces, hyphens and other punctuation.
    name = re.sub(r"[^a-z0-9]", "", name)

    if not name:
        return None

    if len(name) < 4:
        return None

    if len(name) > 30:
        return None

    if name[0].isdigit():
        return None

    return name + ".com"


def generate_ai_candidates(
    keywords: list[str],
    count: int = 75,
) -> list[str]:
    """
    Ask Gemini to generate creative .com domain names.

    Returns cleaned .com domain names.
    """

    api_key = get_api_key()

    if not api_key:
        print()
        print(
            "WARNING: GEMINI_API_KEY is not set."
        )
        print(
            "Continuing with local generation only."
        )
        print()

        return []

    keyword_text = ", ".join(keywords)

    prompt = f"""
You are an expert brand-name and domain-name strategist.

Generate {count} creative, memorable, professional domain names
for a company associated with these concepts:

{keyword_text}

Requirements:

1. Every candidate must be suitable for a .com domain.
2. Generate original brandable names rather than generic phrases.
3. Prefer short names.
4. Names should be easy to pronounce.
5. Names should be easy to spell after hearing them.
6. Avoid numbers.
7. Avoid hyphens.
8. Avoid awkward abbreviations.
9. Avoid names that sound like existing major technology companies.
10. Do not explain the names.
11. Return ONLY the candidate names.
12. Put exactly one candidate on each line.
13. Do NOT include ".com"; the program will add it.

Generate a diverse mixture of:
- compound words
- invented brand names
- technology-inspired names
- names combining the concepts naturally
- professional consulting/company names

Do not simply append "AI" or "Tech" to every keyword.
"""

    try:

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )

        text = response.text

        if not text:
            return []

        candidates = []

        for line in text.splitlines():

            candidate = clean_candidate(line)

            if candidate and candidate not in candidates:
                candidates.append(candidate)

        return candidates

    except Exception as error:

        print()
        print(
            "WARNING: Gemini generation failed."
        )
        print(
            f"Reason: {error}"
        )
        print(
            "Continuing with local candidates."
        )
        print()

        return []