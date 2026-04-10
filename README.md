# web-health-system

# Is It Stress or Physical Illness?

A clinical decision support web app that uses a **Discrete Bayesian Network** to assess whether a user's symptoms are more likely stress-related or indicative of a physical illness — with probabilistic reasoning, red flag detection, and a full symptom history log.

---

## How It Works

Users select symptoms from a structured form. The app runs a **Naive Bayes inference** engine with hand-specified Conditional Probability Tables (CPTs) for 20 symptoms across two conditions (stress vs. physical illness). Prior probabilities are updated using the likelihood of each symptom given each condition, then adjusted with contextual modifiers like symptom timing and duration.

The system flags "red flag" symptoms (e.g. fever, swelling, vomiting) that are strongly associated with physical illness and always surfaces them prominently regardless of the overall posterior.

---

## Features

- Discrete Bayesian Network with CPTs for 20 symptoms
- Posterior probability calculation (stress vs. physical illness)
- Contextual modifiers: symptom timing, duration, lifestyle factors
- Red flag symptom detection with automatic escalation
- Per-symptom signal explanations (stress signal / physical signal / mixed)
- User session tracking with symptom history log
- Flask backend with HTML/CSS frontend

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python |
| Probabilistic Model | Custom Bayesian Network (pgmpy-inspired, hand-built CPTs) |
| Web Framework | Flask |
| Database | SQLite (via SQLAlchemy) |
| Frontend | HTML, CSS |

---

## Project Structure

```
stress-or-physical/
├── app.py              # Flask routes + session handling
├── bayesian.py         # Bayesian Network: CPTs, inference engine, red flag logic
├── models.py           # SQLAlchemy models (user sessions, history)
├── templates/
│   ├── index.html      # Landing page
│   ├── assessment.html # Symptom input form
│   ├── results.html    # Probabilistic output + explanations
│   ├── history.html    # Past session log
│   └── login.html
└── .gitignore
```

---

## Running Locally

```bash
pip install flask flask-sqlalchemy pgmpy
python app.py           # starts Flask server at localhost:5000
```

---

## Design Decisions

**Why Bayesian Network over rule-based logic?**
An earlier prototype used if/else rules, but symptoms are not independent — the combination of fatigue + sleep disturbances + racing heart means something different than any single symptom alone. A Bayesian approach captures these probabilistic dependencies more accurately.

**Why hand-specified CPTs?**
No labelled clinical dataset was available, so CPT values were grounded in published literature on somatic stress symptoms and common physical illness indicators.

---

## Skills Demonstrated

- Probabilistic graphical model design (Bayesian Network)
- Conditional probability and belief propagation
- Clinical decision support system architecture
- Flask full-stack development with persistent storage
- Handling uncertainty in user-facing outputs
