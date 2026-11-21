{% autoescape off %}# Editing: how changes work and best practices

## Changes are live

Every write tool saves at once: the change is on the public site as soon as
the call returns. There is no draft and no undo. Each change is recorded in
the container's admin history, but the history does not restore content.

- Tell the user what you are about to change before larger edits (rewriting
  a page, deleting sections), and wait for their confirmation.
- Prefer hiding (`visible: false`) to deleting when the user is not sure.

## Work in small steps

- One call changes one thing: a section, a module or an item. Make several
  calls rather than trying to rebuild a page at once.
- `update` sends only the fields you want to change. Fields you leave out
  keep their value.
- Edit in place: update an existing module rather than deleting it and
  adding a new one. Deleting loses its configs, its links from other pages
  and its history.
- After a series of changes, read the page again (`xprez_container_get`, or
  the `xprez://containers/{id}` resource for the rendered HTML) and check the
  result.

## Linked content

A section or container can be shown on several pages through links
(`section_symlink`, `container_symlink` in `xprez_container_get`).

- Editing the original changes every page that links to it. Check
  `linked_from` before editing, and ask the user when it is not empty.
- A link itself has only a position; to change what it shows, edit the
  original.

## Errors

A validation error names the fields that failed and why. Fix those fields and
send the call again; do not guess other values. A field that is not listed in
`xprez_module_types` for that module type cannot be set.

## Content

- Write for the page's visitors, in the language of the existing content.
- Keep the structure the page already has (how sections are used, how
  headings are styled) unless the user asks for a redesign.
- Every image needs a meaningful alternative text.
{% endautoescape %}
