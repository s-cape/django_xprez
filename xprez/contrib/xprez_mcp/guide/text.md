{% autoescape off %}# Text and HTML

Text fields edited with the rich text editor take HTML. Only what the editor
can produce is kept; anything else is removed when the module is saved, so
what you send may come back changed.

The text module allows these tags (another field's rules are in its schema,
under `html`, in `xprez_module_types`):

{% for tag in text_rules.tags %}- `{{ tag }}`{% for t, names in text_rules.attributes.items %}{% if t == tag %}, attributes: {{ names|join:", " }}{% endif %}{% endfor %}{% for t, names in text_rules.classes.items %}{% if t == tag %}; classes: {{ names|join:", " }}{% endif %}{% endfor %}
{% endfor %}
## Best practices

- Headings start at `h2`: the page title is usually the `h1`. Do not skip
  levels.
- Use real lists (`ul`, `ol`) rather than lines starting with dashes.
- No inline styles, classes or fonts: the site's design styles the text.
  Only the classes listed above are kept (on links, typically button
  styles).
- Links to other pages of the site use their path (`/contact/`), not the
  full domain.
- Keep layout out of the text: columns, images beside text and spacing belong
  to sections, modules and their configs (see `layout`).
{% endautoescape %}
