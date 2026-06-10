# PersonaAudit

PersonaAudit is a research-based password exposure assessment tool that models how attackers generate targeted password guesses using publicly available personal information.

The project is inspired by:

- NIST SP 800-63B
- OWASP Top 10
- TarGuess (Wang et al., 2016)
- The Science of Password Selection (Weir et al., 2010)
- Bonneau et al., IEEE S&P 2012
- Password leak analyses (RockYou, HIBP)

## Purpose

The objective of PersonaAudit is not password cracking.

Its purpose is to help users understand whether their current passwords are predictable from personal information and to encourage stronger password practices.

---

## Features

### Password Pattern Generation

- Name combinations
- Nicknames
- Pet names
- Cities
- Additional keywords
- Birth year patterns
- Date transformations
- Phone number fragments
- Initial-based passwords

### Mutation Engine

- Case variations
- Leetspeak substitutions
- Keyboard walks
- Special characters
- Padding patterns
- Number suffixes

### Statistical Analysis

- Length distribution
- Number usage
- Uppercase usage
- Special character usage
- Leet statistics


### Flask Backend

Built with:

- Flask
- Flask-CORS
- Python

---

## Example

Input:

```json
{
    "first_name": "john",
    "last_name": "smith",
    "birth_year": "1999"
}

output
{
    "count": 15000,
    "passwords": [...]
}
