"""
Domain Finder Lite
Enhanced Domain Scoring

Scores domain candidates based on:

    - Brandability       30%
    - Pronounceability   20%
    - Memorability       15%
    - Length             15%
    - Relevance          20%

Also provides:

    - Negative quality penalties
    - Brand-type classification
    - Detailed score breakdown

No external packages required.
"""

import re


# ------------------------------------------------------------------
# Brand vocabulary
# ------------------------------------------------------------------

POSITIVE_BRAND_WORDS = {
    "ai",
    "cyber",
    "secure",
    "security",
    "smart",
    "tech",
    "digital",
    "data",
    "cloud",
    "logic",
    "signal",
    "guard",
    "shield",
    "sentinel",
    "core",
    "vision",
    "mind",
    "forge",
    "labs",
    "lab",
    "works",
    "systems",
    "intelligence",
    "intel",
    "neural",
    "quantum",
}


# Generic business words are not bad, but they don't make
# a domain particularly distinctive.
GENERIC_BUSINESS_WORDS = {
    "solutions",
    "consulting",
    "services",
    "technology",
    "technologies",
    "systems",
    "enterprise",
    "enterprises",
    "group",
    "company",
    "global",
    "digital",
}


# ------------------------------------------------------------------
# Basic utilities
# ------------------------------------------------------------------

def remove_tld(domain: str) -> str:
    """Remove .com from a domain."""

    domain = domain.lower().strip()

    if domain.endswith(".com"):
        return domain[:-4]

    return domain


def clean_keyword(keyword: str) -> str:
    """Convert a keyword into domain-safe text."""

    return re.sub(
        r"[^a-z0-9]",
        "",
        keyword.lower(),
    )


# ------------------------------------------------------------------
# Length
# ------------------------------------------------------------------

def length_score(name: str) -> float:
    """
    Score domain length.

    Shorter names are generally more desirable.
    """

    length = len(name)

    if length <= 6:
        return 100

    if length <= 8:
        return 96

    if length <= 10:
        return 92

    if length <= 12:
        return 86

    if length <= 15:
        return 78

    if length <= 18:
        return 68

    if length <= 21:
        return 55

    if length <= 24:
        return 42

    if length <= 27:
        return 28

    if length <= 30:
        return 15

    return 0


# ------------------------------------------------------------------
# Pronounceability
# ------------------------------------------------------------------

def pronounceability_score(name: str) -> float:
    """
    Estimate how easy a domain is to pronounce.

    This is heuristic rather than a true linguistic model.
    """

    if not name:
        return 0

    score = 70.0

    vowels = "aeiou"

    vowel_count = sum(
        1
        for char in name
        if char in vowels
    )

    vowel_ratio = vowel_count / len(name)

    # Healthy vowel/consonant balance.
    if 0.30 <= vowel_ratio <= 0.55:
        score += 18

    elif 0.22 <= vowel_ratio <= 0.62:
        score += 8

    else:
        score -= 10

    # Long consonant clusters are hard to pronounce.
    if re.search(
        r"[bcdfghjklmnpqrstvwxyz]{5,}",
        name,
    ):
        score -= 30

    elif re.search(
        r"[bcdfghjklmnpqrstvwxyz]{4}",
        name,
    ):
        score -= 18

    elif re.search(
        r"[bcdfghjklmnpqrstvwxyz]{3}",
        name,
    ):
        score -= 8

    # Too many vowels in a row can also be awkward.
    if re.search(r"[aeiou]{4,}", name):
        score -= 15

    # Repeated characters.
    if re.search(r"(.)\1\1", name):
        score -= 20

    elif re.search(r"(.)\1", name):
        score -= 5

    return max(0, min(100, score))


# ------------------------------------------------------------------
# Memorability
# ------------------------------------------------------------------

def memorability_score(name: str) -> float:
    """
    Estimate how memorable the name is.
    """

    score = 65.0

    length = len(name)

    # Short names are easier to remember.
    if length <= 8:
        score += 20

    elif length <= 12:
        score += 12

    elif length <= 16:
        score += 5

    elif length > 22:
        score -= 15

    # Compound names with recognizable concepts can be memorable.
    matched_words = 0

    for word in POSITIVE_BRAND_WORDS:
        if word in name:
            matched_words += 1

    if matched_words == 1:
        score += 8

    elif matched_words >= 2:
        score += 4

    # Too many repeated characters hurt memorability.
    if re.search(r"(.)\1\1", name):
        score -= 15

    # Numbers are harder to remember and communicate.
    if any(char.isdigit() for char in name):
        score -= 20

    return max(0, min(100, score))


# ------------------------------------------------------------------
# Brandability
# ------------------------------------------------------------------

def brandability_score(name: str) -> float:
    """
    Estimate how strongly the name works as a brand.
    """

    score = 60.0

    length = len(name)

    # Ideal general-purpose brand length.
    if 6 <= length <= 15:
        score += 15

    elif length <= 20:
        score += 5

    elif length > 25:
        score -= 15

    # Recognizable technology/business concepts.
    matched_words = sum(
        1
        for word in POSITIVE_BRAND_WORDS
        if word in name
    )

    if matched_words == 1:
        score += 10

    elif matched_words == 2:
        score += 6

    elif matched_words >= 3:
        score -= 5

    # Invented/compound names can be more brandable than
    # long descriptive phrases.
    if 7 <= length <= 14:
        score += 8

    # Numbers are usually undesirable for this project.
    if any(char.isdigit() for char in name):
        score -= 20

    return max(0, min(100, score))


# ------------------------------------------------------------------
# Relevance
# ------------------------------------------------------------------

def relevance_score(
    name: str,
    keywords: list[str],
) -> float:
    """
    Score relevance without excessively rewarding keyword stuffing.

    One strong keyword match is good.
    Multiple matches are useful but do not dominate the score.
    """

    cleaned_keywords = [
        clean_keyword(keyword)
        for keyword in keywords
        if clean_keyword(keyword)
    ]

    if not cleaned_keywords:
        return 50

    matches = 0

    for keyword in cleaned_keywords:

        if keyword in name:
            matches += 1

    if matches == 0:
        return 35

    if matches == 1:
        return 75

    if matches == 2:
        return 92

    # Don't reward stuffing.
    return 95


# ------------------------------------------------------------------
# Generic-name penalty
# ------------------------------------------------------------------

def generic_penalty(name: str) -> float:
    """
    Penalize overly generic corporate naming.
    """

    penalty = 0

    matches = sum(
        1
        for word in GENERIC_BUSINESS_WORDS
        if word in name
    )

    if matches == 1:
        penalty += 5

    elif matches == 2:
        penalty += 12

    elif matches >= 3:
        penalty += 20

    return penalty


# ------------------------------------------------------------------
# Awkward-name penalty
# ------------------------------------------------------------------

def awkward_name_penalty(name: str) -> float:
    """
    Penalize characteristics that tend to make a domain
    difficult to use as a brand.
    """

    penalty = 0

    # Numbers.
    if any(char.isdigit() for char in name):
        penalty += 15

    # Excessive consonant clusters.
    if re.search(
        r"[bcdfghjklmnpqrstvwxyz]{5,}",
        name,
    ):
        penalty += 20

    elif re.search(
        r"[bcdfghjklmnpqrstvwxyz]{4}",
        name,
    ):
        penalty += 8

    # Excessive repeated characters.
    if re.search(r"(.)\1\1", name):
        penalty += 15

    # Extremely long names.
    if len(name) > 25:
        penalty += 15

    return penalty


# ------------------------------------------------------------------
# Brand type
# ------------------------------------------------------------------

def classify_brand_type(
    name: str,
    keywords: list[str],
) -> str:
    """
    Classify the domain into a broad brand category.
    """

    cleaned_keywords = [
        clean_keyword(keyword)
        for keyword in keywords
        if clean_keyword(keyword)
    ]

    keyword_matches = sum(
        1
        for keyword in cleaned_keywords
        if keyword in name
    )

    known_matches = sum(
        1
        for word in POSITIVE_BRAND_WORDS
        if word in name
    )

    # Mostly literal keyword usage.
    if keyword_matches >= 2:
        return "DESCRIPTIVE"

    # One or more recognizable words combined.
    if known_matches >= 1:

        if len(name) <= 15:
            return "COMPOUND"

        return "TECHNICAL"

    # Otherwise it is likely an invented/abstract name.
    return "INVENTED"


# ------------------------------------------------------------------
# Detailed scoring
# ------------------------------------------------------------------

def score_breakdown(
    domain: str,
    keywords: list[str],
) -> dict:
    """
    Return detailed scoring information.
    """

    name = remove_tld(domain)

    brandability = brandability_score(name)
    pronounceability = pronounceability_score(name)
    memorability = memorability_score(name)
    length = length_score(name)
    relevance = relevance_score(
        name,
        keywords,
    )

    generic_penalty_value = generic_penalty(name)
    awkward_penalty = awkward_name_penalty(name)

    base_score = (
        brandability * 0.30
        + pronounceability * 0.20
        + memorability * 0.15
        + length * 0.15
        + relevance * 0.20
    )

    final_score = (
        base_score
        - generic_penalty_value
        - awkward_penalty
    )

    final_score = max(
        0,
        min(100, final_score),
    )

    return {
        "domain": domain,
        "score": round(final_score),
        "brandability": round(brandability),
        "pronounceability": round(pronounceability),
        "memorability": round(memorability),
        "length": round(length),
        "relevance": round(relevance),
        "generic_penalty": round(
            generic_penalty_value
        ),
        "awkward_penalty": round(
            awkward_penalty
        ),
        "brand_type": classify_brand_type(
            name,
            keywords,
        ),
    }


# ------------------------------------------------------------------
# Public scoring functions
# ------------------------------------------------------------------

def calculate_score(
    domain: str,
    keywords: list[str],
) -> int:
    """
    Calculate the overall domain score.
    """

    breakdown = score_breakdown(
        domain,
        keywords,
    )

    return breakdown["score"]


def score_domains(
    domains: list[str],
    keywords: list[str],
) -> list[tuple[str, int]]:
    """
    Score and rank domains.

    Returns:

        [
            ("example.com", 94),
            ("another.com", 87),
        ]
    """

    scored = []

    for domain in domains:

        score = calculate_score(
            domain,
            keywords,
        )

        scored.append(
            (domain, score)
        )

    scored.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return scored


def detailed_score_domains(
    domains: list[str],
    keywords: list[str],
) -> list[dict]:
    """
    Score domains and return complete score breakdowns.
    """

    results = []

    for domain in domains:

        results.append(
            score_breakdown(
                domain,
                keywords,
            )
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results