# AGENTS.md - Guidelines for Agentic Coding in PLAMOTO

## Build/Lint/Test Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Run app**: `flask run`
- **Database setup**: `./db_setup.sh` (runs migrations)
- **Linting**: No linter configured; consider `ruff check .` or `flake8 .`
- **Formatting**: No formatter configured; consider `black .` or `ruff format .`
- **Tests**: No tests present; run `pytest` to execute. For single test: `pytest path/to/test_file.py::test_function`

## Code Style Guidelines
- **Imports**: Group as standard library, third-party, local. Separate groups with blank lines. Use `import numpy as np` for common aliases.
- **Formatting**: 4 spaces indentation, line length ~88 chars. Use trailing commas in multi-line structures.
- **Types**: Add type hints to function parameters and returns where beneficial (e.g., `def func(x: int) -> str:`).
- **Naming**: snake_case for functions/variables/constants, PascalCase for classes. Use descriptive names.
- **Error Handling**: Wrap risky code in try-except, log with `logger.exception("message")`. Avoid bare except.
- **Docstrings**: Use triple quotes for module/function descriptions. Keep concise.
- **Comments**: Add comments for complex logic, avoid obvious ones. No inline comments unless necessary.
- **Flask Specifics**: Use `app.logger` for logging, follow RESTful route naming. Handle DB commits with `safe_commit()`.
- **Security**: Never log secrets/keys. Use environment variables for sensitive data.
- **Commits**: Use imperative mood, e.g., "Add feature" not "Added feature". Reference issues if applicable.</content>
<parameter name="filePath">AGENTS.md