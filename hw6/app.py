"""Offline educational password checker. Python 3.10+, standard library only."""
import argparse
import getpass
import sys
import warnings
from dataclasses import dataclass

MAX_LENGTH = 256
COMMON = frozenset({"password", "password123", "password123!", "123456",
                    "123456789", "qwerty", "qwerty123", "admin", "letmein",
                    "welcome", "welcome123!", "iloveyou", "abc123"})


@dataclass(frozen=True)
class Result:
    rating: str
    length: int
    feedback: tuple[str, ...]


def analyze(password: str) -> Result:
    """Treat input as data; never print, save, transmit, or execute it."""
    if not isinstance(password, str):
        raise ValueError("Input must be text.")
    if not 1 <= len(password) <= MAX_LENGTH:
        raise ValueError(f"Enter between 1 and {MAX_LENGTH} characters.")
    if not password.isprintable():
        raise ValueError("Control characters are not accepted.")
    lower = password.casefold()
    advice = []
    common = lower in COMMON
    repeated = len(set(password)) <= 2
    sequential = any(s in lower for s in ("1234", "abcd", "qwerty"))
    if len(password) < 16:
        advice.append("Use at least 16 characters; several unrelated words can help.")
    if common:
        advice.append("This matches the small built-in list of common passwords.")
    if repeated:
        advice.append("Avoid repeating only one or two characters.")
    if sequential:
        advice.append("Avoid obvious keyboard or alphabetical sequences.")
    if common or repeated or len(password) < 10:
        rating = "Weak"
    elif len(password) < 16 or sequential:
        rating = "Moderate"
    else:
        rating = "Stronger candidate"
    advice.append("Use a unique password for every account and enable MFA.")
    return Result(rating, len(password), tuple(advice))


def print_result(result: Result) -> None:
    print(f"\nRating: {result.rating}\nLength: {result.length}")
    for tip in result.feedback:
        print(f"- {tip}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Evaluate public fake examples.")
    args = parser.parse_args(argv)
    print("OFFLINE PASSWORD CHECKER")
    print("Educational heuristic, not a guarantee or a breach database check.")
    print("Use made-up examples for class; never paste an actual account password.")
    if args.demo:
        for label, sample in (("Common fake example", "password123!"),
                              ("Long repeated fake example", "a" * 20),
                              ("Long fake passphrase", "harbor cactus violet lantern")):
            print(f"\nDEMO: {label}")
            print_result(analyze(sample))
        print("\nLIMIT TEST: 257 characters")
        try:
            analyze("x" * 257)
        except ValueError as exc:
            print(f"Rejected: {exc}")
        return 0
    if not sys.stdin.isatty():
        print("Interactive mode requires a terminal. Try --demo.", file=sys.stderr)
        return 2
    try:
        # Refuse getpass's insecure echoed-input fallback.
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("\nMade-up password (hidden): ")
        result = analyze(password)
        del password  # Drops this reference; Python cannot guarantee memory erasure.
        print_result(result)
        return 0
    except (ValueError, getpass.GetPassWarning) as exc:
        print(f"Cannot evaluate: {exc}", file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
