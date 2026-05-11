Concepts
========

Xprez content is built from these core concepts:

- **Container** — A model that holds content (e.g. Page, Article). Subclass `Container` in your app.
- **Section** — Rows within a container.
  - **SectionConfig** — Breakpoint-specific section settings.
- **Module** — Content blocks inside sections (text, gallery, video, etc.). Built-in modules are provided; you can add custom ones by subclassing `Module`.
    - **ModuleConfig** — Base for breakpoint-specific module settings; default when a module has no custom config.

Containers contain sections; sections contain modules.
