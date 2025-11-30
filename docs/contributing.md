# Contributing to SUHS-MRV

Thank you for your interest in contributing to the SUHS-MRV dataset and tools.

---

## 1. Ways to Contribute

- Improve or extend documentation in `docs/`.  
- Propose new validation checks or evaluation metrics.  
- Add new example notebooks demonstrating use cases.  
- Suggest enhancements to physics models or generator logic.  
- Report bugs or inconsistencies in generated data.

---

## 2. Getting Started

1. Fork and clone the repository.  
2. Create and activate a virtual environment.  
3. Install dependencies:

   `pip install -r requirements.txt`

4. From the repo root, run:

   `python -m src.generator`

5. Open the notebooks under `notebooks/` to explore the dataset.

---

## 3. Development Guidelines

- Keep physics logic localized to `src/physics.py` where possible.  
- Keep `src/generator.py` focused on orchestration and high-level flow.  
- Avoid hard-coding constants; prefer configuration via `config/uhs_config.yaml`.  
- Ensure new features are covered by validation checks or example notebooks.

---

## 4. Coding Style

- Use clear, descriptive names for variables and functions.  
- Prefer type hints for public functions.  
- Keep functions small and focused on one responsibility.

---

## 5. Submitting Changes

1. Create a feature branch in your fork.  
2. Make and test your changes locally.  
3. Commit with clear messages describing the change.  
4. Open a Pull Request against the main repository, including:
   - A short description and motivation.  
   - Any notes on configuration changes.  
   - Screenshots or notebook snippets if helpful.

---

## 6. Reporting Issues

When filing an issue, please include:

- SUHS-MRV version (e.g., v2.0).  
- Python version and OS.  
- Steps to reproduce the problem or a minimal notebook.  
- Any error messages or stack traces.

---
