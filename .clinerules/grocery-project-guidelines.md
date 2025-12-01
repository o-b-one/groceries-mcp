## Brief overview
This document outlines the core guidelines for developing and maintaining the grocery-agent project. These rules cover documentation practices, code style, testing standards, and architectural preferences to ensure consistency, maintainability, and alignment with the project’s goals.

## Documentation Requirements
  - Update `retail_agent/docs` directory whenever new features are implemented or existing ones are modified.
  - Keep `retail_agent/README.md` synchronized with the latest capabilities, including usage examples and setup instructions.
  - Maintain `CHANGELOG.md` by adding entries for every new feature, bug fix, or breaking change using the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## Testing Standards
  - Write **unit tests** for all business logic, using `pytest`.
  - All tests must be located in a dedicated `tests/` directory at the root.
  - Any feature should have unit-test first, that describe all scenarios, then implementation should pass all those tests.

## Project Context
  - This project is a grocery shopping assistant powered by an MCP server, integrating multiple grocery providers (Keshet, Rami Levy, Shufersal).
  - The agent logic resides in `retail_agent/src/agent`.
  - Tools developed as modular MCP servers and located under `/retail_agent/src/server`.
  - Use `uv` as the Python package manager; ensure `uv.lock` is updated after any dependency changes.

## Other Guidelines
  - Avoid long-running or complex prompts in agent logic; break down reasoning into small, composable steps.
  - Use meaningful variable and function names; avoid abbreviations unless widely recognized.
  - Do not commit to `main` directly; always use feature branches and open a PR for review.
  - Prioritize clarity and maintainability over brevity in code and comments.
  - In case of file creation, verify folder exists first, if not, create it
