# Domain Finder Lite

Generate `.com` domain-name candidates from keywords, rank them with simple
brand-focused heuristics, and check their registration status through Verisign
RDAP. Gemini can optionally generate additional candidates.

## What it does

Domain Finder Lite starts with one or more keywords, creates local candidate
names, converts them to `.com` domains, scores them, and checks higher-scoring
candidates first. It prints confirmed available results in score order, along
with a detailed breakdown for the top five.

With the optional `--ai` flag, it also asks Gemini for additional candidate
names before deduplicating, scoring, and checking them.

## Features

- Local keyword-based candidate generation with built-in prefixes and suffixes.
- Optional Gemini-assisted candidate generation.
- Candidate cleanup, deduplication, and basic length/character filtering.
- Heuristic scoring for brandability, pronounceability, memorability, length,
  and keyword relevance.
- Brand-type labels: `DESCRIPTIVE`, `COMPOUND`, `TECHNICAL`, and `INVENTED`.
- `.com` registration checks using Verisign RDAP.
- Ranked results and score breakdowns for the top five available domains.

## Requirements

- Python 3.10 or later.
- Internet access to check `.com` registration status through Verisign RDAP.
- No third-party Python packages are required for local-only operation.
- Gemini-assisted generation additionally requires the optional
  `google-genai` package and a Gemini API key.

## Installation

Clone or download this repository, then work from its directory.

Core/local-only use has no third-party dependencies. The included
`requirements.txt` is intentionally empty:

```bash
python -m pip install -r requirements.txt
```

## Configuration

No configuration file is required for local generation and `.com` checks.

### Optional Gemini AI setup

Install the optional AI dependency:

```bash
python -m pip install -r requirements-ai.txt
```

Set `GEMINI_API_KEY` in your environment before using `--ai`. For example, in
a POSIX-compatible shell:

```bash
export GEMINI_API_KEY="your-api-key"
```

The program reads this environment variable at runtime; do not put an API key
in the source code. If the optional package is not installed, or if Gemini
generation fails, the program reports the issue and continues with locally
generated candidates. If the API key is absent, it also continues locally.

## Usage

Run the program from the repository directory:

```bash
python domain_finder.py <keyword> [<keyword> ...]
```

### Command-line reference

| Argument or option | Description |
| --- | --- |
| `keywords` | One or more required keywords used for local generation and scoring. |
| `--ai` | Adds Gemini-generated candidates. Requires the optional AI dependency and `GEMINI_API_KEY`. |
| `--results N` | Target number of confirmed available `.com` domains to return. Defaults to `25`; `N` must be at least `1`. |

### Examples

Generate and check locally produced candidates:

```bash
python domain_finder.py AI cybersecurity
```

Add Gemini-generated candidates:

```bash
python domain_finder.py AI cybersecurity --ai
```

Request up to 30 confirmed available results for a multi-word concept:

```bash
python domain_finder.py "AI cybersecurity consulting" --ai --results 30
```

Output includes progress while domains are checked. When results are found,
the program prints an `AVAILABLE .COM DOMAINS` table with each domain's score
and brand type, followed by detailed score breakdowns for up to five results.
Candidates, scores, and registration results vary by keywords, Gemini output
when enabled, and current registry state.

## Understanding results and scores

The score is a 0–100 heuristic used to rank candidates. It combines:

- Brandability: 30%
- Pronounceability: 20%
- Memorability: 15%
- Length: 15%
- Keyword relevance: 20%

The score can be reduced for generic business terms, numbers, long consonant
clusters, repeated characters, and very long names. It is a prioritization
tool, not a measure of trademark strength, linguistic quality, market demand,
or legal availability.

### Brand types

- `DESCRIPTIVE`: contains at least two cleaned input keywords.
- `COMPOUND`: contains at least one built-in brand/technology word and is 15
  characters or fewer.
- `TECHNICAL`: contains at least one built-in brand/technology word and is
  longer than 15 characters.
- `INVENTED`: does not meet the preceding classification rules.

## What “available” means

This project checks `.com` domains through Verisign RDAP. It does **not** make
DNS queries.

- An HTTP 200 RDAP response is treated as registered.
- An HTTP 404 RDAP response is treated as available because no matching domain
  object was found in the `.com` registry.
- Network errors, timeouts, and other responses are reported as unable to
  verify and are not treated as available.

An RDAP result does not guarantee that a domain can be purchased or registered
through a registrar. It may be reserved, premium, subject to registrar rules,
or otherwise unavailable for acquisition.

## Limitations and responsible use

- Only `.com` domains are generated and checked.
- Availability is based solely on Verisign RDAP and may change at any time.
- This is not a trademark search, legal-clearance service, or legal advice.
- You are responsible for trademark research, legal review, and registrar
  availability before using or purchasing a name.
- AI-generated candidates may be unavailable, unsuitable, or similar to
  existing names; review them independently.

## Project structure

```text
domain-finder-lite/
├── domain_finder.py    # Command-line entry point
├── generator.py        # Local candidate generation and formatting
├── scorer.py           # Heuristic scoring and brand-type classification
├── checker.py          # Verisign RDAP availability checking
├── gemini.py           # Optional Gemini candidate generation
├── requirements.txt    # Core dependency manifest (no third-party packages)
├── requirements-ai.txt # Optional Gemini dependency manifest
├── LICENSE             # MIT License
└── README.md
```

## Contributing

Contributions are welcome. Please keep changes focused, preserve local-only
operation without third-party dependencies, and avoid committing API keys or
other secrets. This repository currently has no automated test suite.

## License

This project is licensed under the [MIT License](LICENSE).
