"""
PersonaAudit v2 - Password Wordlist Generator
==============================================
Research-backed personal password auditor.

Sources:
  - NIST SP 800-63B (password guidelines)
  - "The Science of Password Selection" — Weir et al., 2010
  - "Targeted Online Password Guessing" — Wang et al., 2016 (TarGuess)
  - OWASP A07:2021
  - RockYou / HaveIBeenPwned leak pattern analysis
  - Bonneau et al., "The Science of Guessing", IEEE S&P 2012
"""

import itertools
import re
from typing import Optional


# ---------------------------------------------------------------------------
# 1. CONSTANTS
# ---------------------------------------------------------------------------

SEPARATORS = ["", "@", ".", "_", "-", "!", "#", "$", "&", "+"]

COMMON_NUMBER_SUFFIXES = [
    "1", "12", "123", "1234", "12345", "123456",
    "111", "000", "007", "69", "99", "100", "101",
    "666", "777", "888", "999", "2020", "2021", "2022",
    "2023", "2024", "2025", "2026",
]

# All documented single-char substitutions (Weir 2010)
LEET_MAP = {
    "a": ["@", "4"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["$", "5"],
    "t": ["7", "+"],
    "l": ["1"],
    "g": ["9"],
    "b": ["8"],
    "z": ["2"],
}

SPECIAL_SUFFIXES = ["!", "!!", "@", "#", "$", ".*", "?", "123!", "1!", "!1"]

# QWERTY walks — common lazy passwords
KEYBOARD_WALKS = [
    "qwerty", "qwert", "qwer", "asdf", "asdfg", "zxcv", "zxcvb",
    "1qaz", "2wsx", "3edc", "4rfv", "5tgb", "6yhn", "qazwsx",
]

PADDING_CHARS = ["!", "#", "*", "@", ".", "-", "_", "="]
PADDING_SIZES = [1, 2, 3]

# Date format transforms (Wang et al. TarGuess model)
DATE_FORMAT_FUNCS = [
    lambda d, m, y: f"{d:02d}{m:02d}{y}",
    lambda d, m, y: f"{d:02d}{m:02d}{y[-2:]}",
    lambda d, m, y: f"{m:02d}{d:02d}{y}",
    lambda d, m, y: f"{y}{m:02d}{d:02d}",
    lambda d, m, y: f"{d:02d}-{m:02d}-{y}",
    lambda d, m, y: f"{m:02d}/{d:02d}/{y}",
    lambda d, m, y: f"{d}{m}{y}",
    lambda d, m, y: f"{y}{m}{d}",
    lambda d, m, y: f"{m}{y}",
    lambda d, m, y: f"{d}{y}",
    lambda d, m, y: f"{d:02d}{y}",
    lambda d, m, y: f"{m:02d}{y}",
]


# ---------------------------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------------------------

def case_variants(word: str) -> list:
    variants = {
        word.lower(),
        word.upper(),
        word.capitalize(),
        word.title(),
        word.swapcase(),
    }
    return [v for v in variants if v]


def with_separators(a: str, b: str) -> list:
    return [f"{a}{sep}{b}" for sep in SEPARATORS]


def append_numbers(word: str, birth_year=None, include_common=True) -> list:
    results = []
    if birth_year and len(birth_year) == 4:
        results += [
            f"{word}{birth_year}",
            f"{word}{birth_year[-2:]}",
            f"{birth_year}{word}",
            f"{word}{birth_year[-2:]}!",
            f"{word}{birth_year}!",
        ]
    for n in range(100):
        results.append(f"{word}{n:02d}")
    for yr in range(1960, 2027):
        results.append(f"{word}{yr}")
    if include_common:
        for num in COMMON_NUMBER_SUFFIXES:
            results.append(f"{word}{num}")
            results.append(f"{num}{word}")
    return results


def with_special_suffixes(word: str) -> list:
    return [f"{word}{s}" for s in SPECIAL_SUFFIXES]


def apply_leet_all(word: str) -> list:
    word_lower = word.lower()
    char_options = []
    for c in word_lower:
        subs = LEET_MAP.get(c, [])
        char_options.append([c] + subs)
    variants = set()
    for combo in itertools.product(*char_options):
        v = "".join(combo)
        if v != word_lower:
            variants.add(v)
        if len(variants) >= 40:
            break
    return list(variants)


def with_padding(word: str) -> list:
    results = []
    for ch in PADDING_CHARS:
        for n in PADDING_SIZES:
            pad = ch * n
            results.append(f"{pad}{word}{pad}")
            results.append(f"{word}{pad}")
    return results


def build_date_variants(birth_day, birth_month, birth_year, words) -> list:
    if not (birth_day and birth_month and birth_year and len(birth_year) == 4):
        return []
    results = []
    d, m, y = birth_day, birth_month, birth_year
    for fmt in DATE_FORMAT_FUNCS:
        try:
            date_str = fmt(d, m, y)
            results.append(date_str)
            for w in words[:4]:
                results.append(f"{w}{date_str}")
                results.append(f"{date_str}{w}")
        except Exception:
            pass
    return results


def build_phone_fragments(phone, words) -> list:
    if not phone:
        return []
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return []
    results = []
    for n in [4, 6, 7, 8]:
        tail = digits[-n:]
        results.append(tail)
        for w in words[:4]:
            results.append(f"{w}{tail}")
            results.append(f"{tail}{w}")
    return results


def build_base_words(first_name, last_name, nickname, pet_name,
                     city, birth_year, additional_keywords) -> list:
    raw = [first_name, last_name, nickname, pet_name, city, birth_year]
    if additional_keywords:
        raw.extend(additional_keywords)
    base = [w.strip().lower() for w in raw if w and w.strip()]
    return list(dict.fromkeys(base))


# ---------------------------------------------------------------------------
# 3. PATTERN GENERATORS
# ---------------------------------------------------------------------------

def gen_case_reversal_truncation(words):
    results = []
    for w in words:
        results.extend(case_variants(w))
        results.append(w[::-1])
        for n in range(3, min(len(w), 7)):
            results.append(w[:n])
    return results


def gen_pair_combos(words):
    results = []
    for w1, w2 in itertools.permutations(words, 2):
        results.extend(with_separators(w1, w2))
        results.extend(with_separators(w1.capitalize(), w2.capitalize()))
        results.extend(with_separators(w1, w2.capitalize()))
    return results


def gen_triple_combos(words):
    results = []
    capped = words[:6]
    for w1, w2, w3 in itertools.permutations(capped, 3):
        results += [
            f"{w1}{w2}{w3}",
            f"{w1}.{w2}.{w3}",
            f"{w1}_{w2}_{w3}",
            f"{w1.capitalize()}{w2.capitalize()}{w3}",
        ]
    return results


def gen_number_appended(words, birth_year):
    results = []
    for w in words:
        results.extend(append_numbers(w, birth_year))
    return results


def gen_leet_variants(words, birth_year):
    results = []
    for word in words:
        for leet in apply_leet_all(word):
            results.extend(case_variants(leet))
            if birth_year:
                results.append(f"{leet}{birth_year}")
                results.append(f"{leet}{birth_year[-2:]}")
            for s in SPECIAL_SUFFIXES[:5]:
                results.append(f"{leet}{s}")
    return results


def gen_special_suffixes(words):
    results = []
    for w in words:
        results.extend(with_special_suffixes(w))
        results.extend(with_special_suffixes(w.capitalize()))
        results.extend(with_special_suffixes(w.upper()))
    return results


def gen_year_patterns(words, birth_year):
    if not birth_year:
        return []
    yr2 = birth_year[-2:]
    results = []
    for w in words:
        for sep in ["@", "#", "!", ".", "_", ""]:
            results += [
                f"{w}{sep}{birth_year}",
                f"{w}{sep}{yr2}",
                f"{birth_year}{sep}{w}",
                f"{yr2}{sep}{w}",
            ]
        results += [
            f"{w.capitalize()}{birth_year}",
            f"{w.upper()}{birth_year}",
            f"{w}{birth_year}!",
            f"{w}{yr2}!",
        ]
    return results


def gen_padding(words):
    results = []
    for w in words:
        results.extend(with_padding(w))
        results.extend(with_padding(w.capitalize()))
    return results


def gen_keyboard_walks(words, birth_year):
    results = list(KEYBOARD_WALKS)
    for walk in KEYBOARD_WALKS:
        for w in words[:4]:
            results.append(f"{w}{walk}")
            results.append(f"{walk}{w}")
        if birth_year:
            results.append(f"{walk}{birth_year}")
            results.append(f"{walk}{birth_year[-2:]}")
    return results


def gen_initials(first_name, last_name, birth_year, words):
    fi = first_name[0] if first_name else ""
    li = last_name[0] if last_name else ""
    results = []
    if fi and last_name:
        results += [
            f"{fi}{last_name}", f"{fi}.{last_name}", f"{fi}_{last_name}",
            f"{last_name}{fi}", f"{first_name}{li}", f"{fi}{li}",
        ]
        if birth_year:
            results += [
                f"{fi}{last_name}{birth_year}",
                f"{fi}{last_name}{birth_year[-2:]}",
                f"{fi}{last_name}{birth_year}!",
            ]
    all_initials = "".join(w[0] for w in words if w)
    if len(all_initials) >= 2:
        results.append(all_initials)
        if birth_year:
            results.append(f"{all_initials}{birth_year}")
    return results


def gen_pair_number_interleave(words, birth_year):
    pairs = [f"{w1}{w2}" for w1, w2 in itertools.permutations(words, 2)]
    results = []
    for p in pairs[:60]:
        results.extend(append_numbers(p, birth_year))
    return results


# ---------------------------------------------------------------------------
# 4. MAIN GENERATOR
# ---------------------------------------------------------------------------

def generate_passwords(
    first_name: str,
    last_name: str,
    nickname=None,
    pet_name=None,
    city=None,
    birth_year=None,
    birth_month=None,
    birth_day=None,
    phone=None,
    additional_keywords=None,
    max_passwords: int = 15000,
    enable_leet: bool = True,
    enable_numbers: bool = True,
    enable_padding: bool = True,
    enable_dates: bool = True,
    enable_keyboard_walks: bool = True,
    save_to_file: bool = False,
    output_filename: str = "wordlist.txt",
) -> list:

    base_words = build_base_words(
        first_name, last_name, nickname, pet_name,
        city, birth_year, additional_keywords
    )

    password_set = set()
    HARD_CAP = max_passwords * 3

    def add(batch):
        for p in batch:
            if len(password_set) >= HARD_CAP:
                return
            if p and len(p) >= 4:
                password_set.add(p.strip())

    add(gen_case_reversal_truncation(base_words))
    add(gen_pair_combos(base_words))
    add(gen_triple_combos(base_words))

    if enable_numbers:
        add(gen_number_appended(base_words, birth_year))

    if birth_year:
        add(gen_year_patterns(base_words, birth_year))

    add(gen_special_suffixes(base_words))

    if enable_leet:
        add(gen_leet_variants(base_words, birth_year))

    if enable_padding:
        add(gen_padding(base_words))

    if enable_keyboard_walks:
        add(gen_keyboard_walks(base_words, birth_year))

    add(gen_initials(first_name, last_name, birth_year, base_words))

    if enable_dates:
        add(build_date_variants(birth_day, birth_month, birth_year, base_words))

    if phone:
        add(build_phone_fragments(phone, base_words))

    if enable_numbers:
        add(gen_pair_number_interleave(base_words, birth_year))

    if enable_leet:
        pair_combos = gen_pair_combos(base_words)
        leet_pairs = []
        for p in pair_combos[:300]:
            leet_pairs.extend(apply_leet_all(p))
        add(leet_pairs)

    result = sorted(list(password_set))[:max_passwords]

    if save_to_file:
        with open(output_filename, "w") as f:
            f.write("\n".join(result))
        print(f"[+] Saved {len(result)} passwords to '{output_filename}'")

    print(f"[+] Generated {len(result)} unique password candidates.")
    return result


# ---------------------------------------------------------------------------
# 5. FLASK WRAPPER
# ---------------------------------------------------------------------------

def generate_from_dict(data: dict) -> dict:
    passwords = generate_passwords(
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        nickname=data.get("nickname"),
        pet_name=data.get("pet_name"),
        city=data.get("city"),
        birth_year=data.get("birth_year"),
        birth_month=data.get("birth_month"),
        birth_day=data.get("birth_day"),
        phone=data.get("phone"),
        additional_keywords=data.get("additional_keywords", []),
        max_passwords=data.get("max_passwords", 15000),
        enable_leet=data.get("enable_leet", True),
        enable_numbers=data.get("enable_numbers", True),
        enable_padding=data.get("enable_padding", True),
        enable_dates=data.get("enable_dates", True),
        enable_keyboard_walks=data.get("enable_keyboard_walks", True),
        save_to_file=False,
    )
    return {
        "count": len(passwords),
        "passwords": passwords,
        "warning": (
            "These passwords were generated from YOUR personal information. "
            "If any of your current passwords appear in this list, change them immediately."
        ),
    }


# ---------------------------------------------------------------------------
# 6. STATISTICS
# ---------------------------------------------------------------------------

def analyze_wordlist(passwords: list) -> dict:
    stats = {
        "total": len(passwords),
        "length_distribution": {},
        "has_number": 0,
        "has_upper": 0,
        "has_special": 0,
        "all_lower": 0,
        "all_upper": 0,
        "pure_number": 0,
        "pattern_families": {
            "base_words": 0,
            "pairs_and_triples": 0,
            "leet": 0,
            "number_appended": 0,
            "special_char": 0,
        }
    }
    leet_chars = set("@34!$57190+82")
    special_chars = set("!@#$%^&*?.")
    for p in passwords:
        l = len(p)
        bucket = f"{l}" if l <= 20 else "21+"
        stats["length_distribution"][bucket] = stats["length_distribution"].get(bucket, 0) + 1
        if any(c.isdigit() for c in p): stats["has_number"] += 1
        if any(c.isupper() for c in p): stats["has_upper"] += 1
        if any(c in special_chars for c in p): stats["has_special"] += 1
        if p.islower(): stats["all_lower"] += 1
        if p.isupper(): stats["all_upper"] += 1
        if p.isdigit(): stats["pure_number"] += 1
        if any(c in leet_chars for c in p): stats["pattern_families"]["leet"] += 1
        if p[-1].isdigit(): stats["pattern_families"]["number_appended"] += 1
        if any(c in special_chars for c in p): stats["pattern_families"]["special_char"] += 1
    return stats


def print_stats(passwords: list):
    stats = analyze_wordlist(passwords)
    total = stats["total"]
    pct = lambda n: f"{n/total*100:.1f}%" if total else "0%"
    print("\n" + "="*60)
    print("  WORDLIST STATISTICS (v2)")
    print("="*60)
    print(f"  Total candidates    : {total:,}")
    print(f"  Contains a digit    : {stats['has_number']:,}  ({pct(stats['has_number'])})")
    print(f"  Contains uppercase  : {stats['has_upper']:,}  ({pct(stats['has_upper'])})")
    print(f"  Contains special    : {stats['has_special']:,}  ({pct(stats['has_special'])})")
    print(f"  All lowercase       : {stats['all_lower']:,}  ({pct(stats['all_lower'])})")
    print(f"  All uppercase       : {stats['all_upper']:,}  ({pct(stats['all_upper'])})")
    print(f"  Pure numbers        : {stats['pure_number']:,}  ({pct(stats['pure_number'])})")
    print(f"  Has leet chars      : {stats['pattern_families']['leet']:,}  ({pct(stats['pattern_families']['leet'])})")
    print(f"  Number-appended     : {stats['pattern_families']['number_appended']:,}  ({pct(stats['pattern_families']['number_appended'])})")
    print(f"  Special char ending : {stats['pattern_families']['special_char']:,}  ({pct(stats['pattern_families']['special_char'])})")
    print("\n  Length distribution:")
    dist = stats["length_distribution"]
    max_count = max(dist.values()) if dist else 1
    for length in sorted(dist.keys(), key=lambda x: int(x.replace("+",""))):
        count = dist[length]
        bar = "\u2588" * min(28, int(count / max_count * 28))
        print(f"    {length:>4} chars : {bar} {count:,}")
    print("="*60)


# ---------------------------------------------------------------------------
# 7. CLI DEMO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = generate_passwords(
        first_name="john",
        last_name="smith",
        nickname="johnny",
        pet_name="rex",
        city="casablanca",
        birth_year="1999",
        birth_month=7,
        birth_day=4,
        phone="0612345678",
        additional_keywords=["barcelona", "google", "arsenal"],
        max_passwords=15000,
        enable_leet=True,
        enable_numbers=True,
        enable_padding=True,
        enable_dates=True,
        enable_keyboard_walks=True,
        save_to_file=True,
        output_filename="my_wordlist.txt",
    )

    print("\n--- Sample output (first 30) ---")
    for p in result[:30]:
        print(" ", p)

    print_stats(result)
    print("\n[!] REMINDER: Use this list to check what NOT to use as a password.")