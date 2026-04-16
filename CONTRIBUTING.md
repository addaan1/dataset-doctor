# Contributing to Dataset Doctor

First of all, thank you for considering contributing to Dataset Doctor! It's people like you that make open source tools such a great working environment.

## Where to start

* If you find a bug, please create an [Issue](https://github.com/addaan1/dataset-doctor/issues) and label it as `bug`. 
* If you have an idea for a new feature, create an Issue labeled `enhancement`.
* If you want to contribute code, check our issues labeled `good first issue` or `help wanted`.

## Development Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dataset-doctor.git
   cd dataset-doctor
   ```
3. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
4. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Running Tests

We use `pytest` for testing. To ensure your changes haven't broken existing functionality, run:

```bash
pytest tests/ -v
```

If you add a new feature, please add a corresponding test in the `tests/` directory. Check test coverage if possible using `pytest --cov=dataset_doctor tests/`.

## Code Style

* We aim for PEP 8 compliance.
* Please ensure your code format is consistent with the rest of the project.
* Type hints are required for all function signatures.

## Submitting a Pull Request

1. Create a new branch for your feature/bugfix: `git checkout -b feature/your-feature-name`
2. Commit your changes with a clear and descriptive commit message.
3. Push the branch to your fork: `git push origin feature/your-feature-name`
4. Open a Pull Request against the `main` branch of the upstream repository.
5. In your PR description, explain what changes you made and link any related issues.

## Reporting Issues

When reporting a bug, please include:
* Details about your local setup (OS, Python version).
* The command you ran.
* The exact error message or unexpected behavior.
* If possible, a small snippet of the CSV data that triggered the issue (anonymized if necessary).

Thank you for your contributions!
