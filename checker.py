"""
Domain Finder Lite

Uses Verisign RDAP to determine whether a .com domain
is registered.

No external packages required.
"""

import json
import time
import urllib.error
import urllib.request


RDAP_BASE_URL = "https://rdap.verisign.com/com/v1/domain/"

# Delay between requests.
# This keeps the checker conservative.
REQUEST_DELAY = 0.25


def normalize_domain(domain: str) -> str:
    """Normalize a domain name before checking it."""

    domain = domain.lower().strip()

    # Remove accidental duplicate .com suffixes.
    while domain.endswith(".com.com"):
        domain = domain[:-4]

    return domain


def check_domain(domain: str) -> bool | None:
    """
    Check whether a .com domain is available.

    Returns:

        True  = available
        False = registered
        None  = unable to determine

    We deliberately return None for network/server errors.
    We never treat an error as proof that a domain is available.
    """

    domain = normalize_domain(domain)

    # Protect against accidental ".com.com".
    while domain.endswith(".com.com"):
        domain = domain[:-4]

    if not domain.endswith(".com"):
        return None

    url = RDAP_BASE_URL + domain

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Domain-Finder-Lite/1.0",
            "Accept": "application/rdap+json",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:

            # A successful RDAP response means the
            # domain is registered.
            if response.status == 200:
                return False

            return None

    except urllib.error.HTTPError as error:

        # Verisign returns 404 when the domain does not
        # exist in the .com registry.
        if error.code == 404:
            return True

        return None

    except (
        urllib.error.URLError,
        TimeoutError,
        ConnectionError,
    ):
        return None

    except Exception:
        # Never assume availability after an unexpected error.
        return None


def check_domains(
    domains: list[str],
    target_available: int = 25,
) -> list[str]:
    """
    Check domains until enough available domains are found.

    Returns only domains confirmed as available.

    Domains that are registered or cannot be checked are
    excluded from the result.
    """

    available = []

    checked = 0

    print()
    print("Checking .COM availability...")
    print()

    for domain in domains:

        if len(available) >= target_available:
            break

        checked += 1

        print(
            f"  Checking {domain:<35}",
            end="",
            flush=True,
        )

        result = check_domain(domain)

        if result is True:

            available.append(domain)

            print("AVAILABLE")

        elif result is False:

            print("registered")

        else:

            print("unable to verify")

        # Avoid unnecessary requests after the final check.
        if len(available) < target_available:
            time.sleep(REQUEST_DELAY)

    print()
    print(
        f"Checked {checked} domains; "
        f"found {len(available)} available."
    )

    return available
