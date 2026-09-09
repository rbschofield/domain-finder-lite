"""
Domain Finder Lite

    - Local candidate generation
    - Optional Gemini generation
    - Candidate scoring
    - .COM availability checking
    - Ranked results

Usage:

    python domain_finder.py AI cybersecurity

    python domain_finder.py AI cybersecurity --ai

    python domain_finder.py "AI cybersecurity consulting" --ai --results 30
"""

import argparse

from generator import generate_candidates, format_domains
from scorer import (
    score_domains,
    detailed_score_domains,
)
from checker import check_domains
from gemini import generate_ai_candidates


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate and find available .com domain names."
    )

    parser.add_argument(
        "keywords",
        nargs="+",
        help="Keywords to use when generating domain names.",
    )

    parser.add_argument(
        "--ai",
        action="store_true",
        help="Enable AI-assisted Gemini generation.",
    )

    parser.add_argument(
        "--results",
        type=int,
        default=25,
        help="Number of available domains to return (default: 25).",
    )

    return parser.parse_args()


def main():
    """Main application entry point."""

    args = parse_arguments()

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    print()
    print("=" * 72)
    print("DOMAIN FINDER LITE")
    print("=" * 72)

    print()
    print("Keywords:", ", ".join(args.keywords))

    if args.ai:
        print("Mode: AI-assisted")
    else:
        print("Mode: Local generation")

    print()

    # ---------------------------------------------------------
    # Validate results argument
    # ---------------------------------------------------------

    if args.results < 1:
        print("ERROR: --results must be at least 1.")
        return

    # ---------------------------------------------------------
    # Local candidate generation
    # ---------------------------------------------------------

    print("Generating local candidates...")
    print()

    candidates = generate_candidates(
        args.keywords
    )

    print(
        f"Local generator produced "
        f"{len(candidates)} candidates."
    )

    # ---------------------------------------------------------
    # Optional Gemini generation
    # ---------------------------------------------------------

    if args.ai:

        print()
        print("Generating additional AI candidates...")
        print()

        ai_candidates = generate_ai_candidates(
            args.keywords,
            count=100,
        )

        print(
            f"Gemini produced "
            f"{len(ai_candidates)} candidates."
        )

        candidates.extend(ai_candidates)

    # ---------------------------------------------------------
    # Deduplicate candidates
    # ---------------------------------------------------------

    candidates = sorted(
        set(candidates)
    )

    if not candidates:

        print()
        print("No candidates were generated.")
        print()

        return

    print()
    print(
        f"Total unique candidates: "
        f"{len(candidates)}"
    )

    # ---------------------------------------------------------
    # Convert to .com domains
    # ---------------------------------------------------------

    domains = format_domains(
        candidates
    )

    # ---------------------------------------------------------
    # Score candidates
    #
    # We score everything before checking availability so
    # that we can check the highest-quality names first.
    # ---------------------------------------------------------

    print()
    print("Scoring candidates...")

    scored_domains = score_domains(
        domains,
        args.keywords,
    )

    # ---------------------------------------------------------
    # Availability checking
    #
    # check_domains receives domains in score order.
    # It stops once it finds the requested number of
    # available domains.
    # ---------------------------------------------------------

    available_domains = check_domains(
        [
            domain
            for domain, score in scored_domains
        ],
        target_available=args.results,
    )

    # ---------------------------------------------------------
    # If nothing is available, stop here.
    # ---------------------------------------------------------

    if not available_domains:

        print()
        print("=" * 72)
        print("NO AVAILABLE DOMAINS FOUND")
        print("=" * 72)
        print()

        return

    # ---------------------------------------------------------
    # Detailed scoring for available domains
    # ---------------------------------------------------------

    detailed_results = detailed_score_domains(
        available_domains,
        args.keywords,
    )

    # Keep only requested number of results.
    detailed_results = detailed_results[
        :args.results
    ]

    # ---------------------------------------------------------
    # Main results table
    # ---------------------------------------------------------

    print()
    print("=" * 72)
    print("AVAILABLE .COM DOMAINS")
    print("=" * 72)

    print()

    print(
        f"{'#':>2}  "
        f"{'DOMAIN':<35} "
        f"{'SCORE':>5}  "
        f"{'TYPE'}"
    )

    print("-" * 72)

    for number, result in enumerate(
        detailed_results,
        start=1,
    ):

        print(
            f"{number:2}  "
            f"{result['domain']:<35} "
            f"{result['score']:>5}  "
            f"{result['brand_type']}"
        )

    # ---------------------------------------------------------
    # Detailed breakdown for top 5
    # ---------------------------------------------------------

    print()
    print("=" * 72)
    print("TOP 5 SCORE BREAKDOWN")
    print("=" * 72)

    print()

    for number, result in enumerate(
        detailed_results[:5],
        start=1,
    ):

        print(
            f"{number}. "
            f"{result['domain']} "
            f"({result['score']}/100)"
        )

        print(
            f"   Brandability:     "
            f"{result['brandability']:>3}"
        )

        print(
            f"   Pronounceability: "
            f"{result['pronounceability']:>3}"
        )

        print(
            f"   Memorability:     "
            f"{result['memorability']:>3}"
        )

        print(
            f"   Length:           "
            f"{result['length']:>3}"
        )

        print(
            f"   Relevance:        "
            f"{result['relevance']:>3}"
        )

        print(
            f"   Brand type:       "
            f"{result['brand_type']}"
        )

        if result["generic_penalty"] > 0:

            print(
                f"   Generic penalty:  "
                f"-{result['generic_penalty']}"
            )

        if result["awkward_penalty"] > 0:

            print(
                f"   Quality penalty:  "
                f"-{result['awkward_penalty']}"
            )

        print()

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("=" * 72)

    print(
        f"Found {len(detailed_results)} "
        f"available .COM domains."
    )

    print("=" * 72)
    print()


if __name__ == "__main__":
    main()