# Contributing to Resume.AI

Thank you for your interest in contributing to **Resume.AI**! We welcome contributions from developers of all skill levels to help improve this enterprise-grade Resume Intelligence Platform.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/resume-parser-llm.git
   cd resume-parser-llm
   ```
3. **Set up local environment**:
   - Install dependencies: `pip install -r requirements.txt`
   - Copy `.env.example` to `.env` and configure local development variables.
4. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/my-amazing-feature
   ```

## Development Guidelines

### Coding Standards

We enforce styling checks on commits using GitHub Actions. Please format your changes to ensure they conform to standards:
- **Formatting**: Format your Python code using **Black**:
  ```bash
  black .
  ```
- **Imports**: Group and sort your imports using **isort**:
  ```bash
  isort .
  ```
- **Linting**: Check your code structure using **Flake8**:
  ```bash
  flake8 .
  ```

### Running Tests

Before submitting a Pull Request, verify that all existing unit tests pass:
- Run the test suite:
  ```bash
  python -m unittest discover tests
  ```

## Submitting Pull Requests

1. Commit your changes with descriptive commit messages.
2. Push your branch to your forked repository.
3. Open a Pull Request against the `main` branch of the parent repository.
4. Fill out the Pull Request template completely so reviewers can understand your changes.
