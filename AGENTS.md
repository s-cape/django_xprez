# AGENTS.md

Instructions for coding agents working in this repository.

## Scope

- Keep changes focused on the user request.
- Avoid ad-hoc infra changes; if needed, update `fabfile.py` or Ansible files.
- Do not modify CSS/SCSS unless explicitly requested.
- Prefer Bootstrap 5 utility/classes in templates instead of custom styling.

## Python and Django

- Follow Django coding style: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/
- Use Black-compatible formatting.
- Prefer `l += [item]` over `l.append(item)` where practical.
- Keep comments minimal; only document non-obvious intent.
- Keep docstrings concise (one-liners when possible).
- Avoid duplication; extract helpers/mixins when repeated logic appears.

## Django Templates

- Use double quotes (`"`) instead of single quotes (`'`).
- Do not add `{% load ... %}` for libraries already provided via `TEMPLATES["OPTIONS"]["builtins"]`.
- Keep template-tag indentation consistent and nested.

## JavaScript

- Prefer vanilla JavaScript.
- Prefer classes when they improve structure.
- Prefer `data-*` attributes for DOM targeting and behavior hooks.

## Project workflow

- Use `./run` wrapper commands instead of activating virtualenv directly.
  - Examples: `./run`, `./run test`, `./run check`, `./run <manage.py command>`.
- Before starting `./run` development server, check whether it is already running.
- Prefer small, targeted tests after non-trivial changes.
- Avoid high-cost tests (for example, browser/end-to-end) unless explicitly requested.

## Git practices

- Make small, descriptive commits grouped by logical change.
- Do not revert unrelated local changes you did not create.
