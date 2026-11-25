{% autoescape off %}# Editing content with xprez

xprez builds pages out of blocks. You edit those blocks with the `xprez_*`
tools; this guide explains how the content is structured and how to change it
safely.

Topics (call `xprez_guide` with the topic name):

{% for topic in topics %}- `{{ topic.name }}`: {{ topic.summary }}
{% endfor %}
## The structure in one minute

- A **container** is a page, an article or any other object with xprez
  content. It holds an ordered list of **sections**.
- A **section** is a horizontal band of the page: a grid with a number of
  columns. It holds an ordered list of **modules**.
- A **module** is one block of content: text, gallery, quote, video, and so
  on. Some modules (gallery, files, accordion, numbers) hold a list of
  **items**.
- Sections and modules have **configs**: layout settings per screen size
  (breakpoint). See `layout`.
- A section can also be a **link** to a section or a whole container used on
  several pages. See `editing` before changing linked content.

## Before you change anything

1. `xprez_container_get` to see the current content.
2. `xprez_module_types` to see which modules this container allows and which
   fields they take.
3. Read `editing`: changes are live immediately.
{% endautoescape %}
