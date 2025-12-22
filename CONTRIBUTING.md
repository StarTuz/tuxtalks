# Contributing to TuxTalks

Thank you for your interest in contributing to TuxTalks! We welcome contributions from the community to help make TuxTalks the standard for Linux voice control.

## Getting Started

1.  **Fork the Repository**: Start by forking the `tuxtalks` repository to your GitHub account.
2.  **Clone Locally**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/tuxtalks.git
    cd tuxtalks
    ```
3.  **Set Up Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -e .  # Install in editable mode
    ```

## Development Workflow

1.  **Create a Branch**: Always work on a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/my-new-feature
    ```
2.  **Code Standards**:
    *   Follow PEP 8 guidelines.
    *   Use descriptive variable names.
    *   Add comments for complex logic.
3.  **Running Tests**:
    *   Install test dependencies: `pip install pytest pytest-mock`
    *   Run tests: `pytest`

## Submitting a Pull Request

1.  Push your branch to your fork.
2.  Open a Pull Request (PR) against the `main` branch of the `tuxtalks` repository.
3.  Provide a clear description of your changes and link any relevant issues.

## Reporting Bugs

Please use the GitHub Issues tab to report bugs. Include:
*   Steps to reproduce.
*   Expected behavior.
*   Log output (if applicable).
