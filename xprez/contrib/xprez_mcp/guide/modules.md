{% autoescape off %}# Modules

`xprez_module_types` lists the modules a container allows, with their fields.
This topic says what each one is for.

{% for module in modules %}- `{{ module.type }}` ({{ module.name }}){% if module.summary %}: {{ module.summary }}{% endif %}
{% endfor %}
## Choosing a module

- Plain content (paragraphs, headings, lists, a picture with text) is a
  `text` module. Its `media` is one image or video shown with the text; its
  config's `media_role` places it (above, as an icon, as a background).
- Several pictures are a `gallery`, downloads are `files`, not several text
  modules.
- Questions and answers, or other content a visitor expands, are an
  `accordion`.

## Modules with items

`gallery`, `files`, `accordion` and `numbers` hold items, edited one at a
time with the `xprez_item_*` tools (`item_fields` in `xprez_module_types`).
The module's own fields (title, layout) are edited with
`xprez_module_update`.

A new `accordion` or `numbers` module starts with one empty item, as in the
admin: fill it with `xprez_item_update` before adding more.
{% endautoescape %}
