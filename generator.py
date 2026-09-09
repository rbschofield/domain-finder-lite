"""
Domain Finder Lite

Generates simple .com domain-name candidates from keywords.
No internet access or external packages required.
"""

import re


# Words that are useful for generating brandable names.
PREFIXES = [
    "ai",
    "cyber",
    "secure",
    "smart",
    "tech",
    "digital",
    "quantum",
    "neural",
    "intel",
    "data",
    "cloud",
    "logic",
    "signal",
    "guard",
    "shield",
    "sentinel",
    "core",
    "vision",
]

SUFFIXES = [
    "ai",
    "tech",
    "labs",
    "lab",
    "works",
    "forge",
    "mind",
    "logic",
    "core",
    "guard",
    "shield",
    "secure",
    "systems",
    "solutions",
    "intelligence",
    "security",
]


def clean_word(word: str) -> str:
    """Remove characters that are unsuitable for a domain name."""

    word = word.lower().strip()
    word = re.sub(r"[^a-z0-9]", "", word)

    return word


def normalize_keywords(keywords: list[str]) -> list[str]:
    """Clean and deduplicate keyword list."""

    cleaned = []

    for keyword in keywords:
        word = clean_word(keyword)

        if word and word not in cleaned:
            cleaned.append(word)

    return cleaned


def generate_candidates(keywords: list[str]) -> list[str]:
    """
    Generate local domain-name candidates.

    The generator intentionally produces more candidates than we
    ultimately need. Availability filtering will happen later.
    """

    words = normalize_keywords(keywords)

    if not words:
        return []

    candidates = set()

    # ---------------------------------------------------------
    # 1. Simple keyword combinations
    # ---------------------------------------------------------

    for word in words:
        candidates.add(word)

    for first in words:
        for second in words:
            if first != second:
                candidates.add(first + second)
                candidates.add(second + first)

    # ---------------------------------------------------------
    # 2. Prefix + keyword
    # ---------------------------------------------------------

    for prefix in PREFIXES:
        for word in words:
            candidates.add(prefix + word)
            candidates.add(word + prefix)

    # ---------------------------------------------------------
    # 3. Keyword + suffix
    # ---------------------------------------------------------

    for word in words:
        for suffix in SUFFIXES:
            candidates.add(word + suffix)
            candidates.add(suffix + word)

    # ---------------------------------------------------------
    # 4. Prefix + keyword + suffix
    # ---------------------------------------------------------

    for prefix in PREFIXES:
        for word in words:
            for suffix in SUFFIXES:
                candidates.add(prefix + word + suffix)

    # ---------------------------------------------------------
    # 5. Two-keyword combinations with prefixes/suffixes
    # ---------------------------------------------------------

    if len(words) >= 2:

        for first in words:
            for second in words:

                if first == second:
                    continue

                candidates.add(first + second)
                candidates.add(first + "ai" + second)
                candidates.add(first + "cyber" + second)
                candidates.add(first + "secure" + second)

    # ---------------------------------------------------------
    # 6. Remove obviously bad candidates
    # ---------------------------------------------------------

    candidates = {
        candidate
        for candidate in candidates
        if is_reasonable_domain(candidate)
    }

    # Return sorted list for repeatable results.
    return sorted(candidates)


def is_reasonable_domain(name: str) -> bool:
    """
    Basic quality filter.

    This is deliberately conservative. More sophisticated
    scoring will be added later.
    """

    # Must contain only letters and numbers.
    if not re.fullmatch(r"[a-z0-9]+", name):
        return False

    # Avoid extremely short names.
    if len(name) < 4:
        return False

    # Avoid excessively long names.
    if len(name) > 30:
        return False

    # Don't allow names beginning with a number.
    if name[0].isdigit():
        return False

    return True


def format_domains(candidates: list[str]) -> list[str]:
    """
    Convert candidate names into normalized .com domains.

    Handles candidates with or without an existing .com suffix.
    """

    domains = []

    for candidate in candidates:

        domain = candidate.strip().lower()

        # Remove an existing .com before adding it back.
        if domain.endswith(".com"):
            domain = domain[:-4]

        # Remove anything that isn't a valid domain character.
        domain = domain.replace(" ", "")
        domain = domain.replace("-", "")

        if not domain:
            continue

        domain = f"{domain}.com"

        if domain not in domains:
            domains.append(domain)

    return domains