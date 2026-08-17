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

## Installation & Setup

### Step 1 — Download the project

If you have Git:
```bash
git clone https://github.com/YOUR_USERNAME/personaaudit.git
cd personaaudit
```

Or download the ZIP from GitHub and extract it, then open a terminal in the project folder.

---

### Step 2 — Set up the backend

Navigate into the backend folder:

```bash
cd backend
```

**Create a virtual environment** (strongly recommended — keeps your system Python clean):

```bash
# Mac / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` appear at the start of your terminal line. That means it worked.

**Install dependencies:**

```bash
pip install -r requirements.txt
```

This installs Flask and Flask-CORS. That's all that's needed.

---

### Step 3 — Start the Flask server

```bash
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Leave this terminal open. The backend must stay running while you use the app.

**Verify it's working** — open a new terminal and run:

```bash
curl http://localhost:5000/health
# → {"status": "ok"}
```

Or just open `http://localhost:5000/health` in your browser.

---

### Step 4 — Open the frontend

Open a **second terminal** (keep the Flask one running), then:

```bash
cd frontend
```

**Option A — Open directly (simplest):**

```bash
# Mac
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

**Option B — Serve with Python (recommended, avoids browser security restrictions):**

```bash
python -m http.server 3000
```

Then open your browser and go to: **http://localhost:3000**

---

### Step 5 — Use the app

1. Fill in the form with your personal information
2. Toggle **Leetspeak** and **Number suffixes** on or off as you like
3. Click **⚡ Generate Passwords**
4. Wait a moment — the backend generates 5,000+ combinations
5. Browse the first 50 results shown on screen
6. Use the **Password Risk Check** box to test any password you currently use
7. Download the full wordlist as `.txt` if you want to review everything

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
