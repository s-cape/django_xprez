# AGENTS.md

Instructions for coding agents working in this repository.

## Repository context

- This is a reusable Django library (`xprez`) with an `example_app` used for integration tests and demos.
- Favor library-safe changes over project-specific shortcuts.
- Preserve backward compatibility for public behavior unless the task explicitly asks for a breaking change.

## Scope and change discipline

- Keep changes narrowly focused on the user request.
- Do not mix unrelated refactors with functional fixes.
- Do not revert unrelated local changes you did not create.

## Python and Django conventions

- Follow Django coding style: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/
- Keep Python code Black-compatible (`pyproject.toml` is configured for it).
- Keep comments/docstrings concise and focused on non-obvious context.
- Prefer small helper functions/mixins instead of duplicated logic.

## Templates and frontend code

- Follow existing local style in each file (do not mass-normalize quote style).
- Do not assume Bootstrap; this library ships its own frontend/admin markup and styles.
- Keep existing `data-component` and JS hook attributes stable unless a change requires updating both templates and scripts.
- For JavaScript, prefer plain JavaScript and avoid adding framework dependencies.

## Validation and tests

- Run lightweight, relevant checks for changed code.
- Python formatting/lint baseline is pre-commit + Black (see `.pre-commit-config.yaml`).
- Main CI test command is:
  - `python manage.py test --settings=example_app.settings_ci --keepdb` (from `example_app/`)
- If you change frontend assets, rebuild only the affected asset package(s):
  - `xprez/ck_editor/assets/ckeditor5`
  - `xprez/static/xprez`

## Git practices

- Prefer small, descriptive commits grouped by logical change.
