{% autoescape off %}# Layout: sections, columns and breakpoints

## Sections are grids

A section lays its modules out in a grid. The section's config sets the
number of `columns` (1 to 8) and the `gap` between them; each module's config
sets how many columns it spans (`colspan`) and rows (`rowspan`).

Modules fill the grid in their `position` order. To put two modules side by
side, give the section two columns and each module `colspan: 1`. To have one
module span the full width, give it `colspan` equal to the section's columns.

## Breakpoints

Configs are set per breakpoint (screen size). Breakpoint `0` is the base
style, used at every size; higher numbers are smaller screens and override
the base only where they differ:

{% for number, breakpoint in breakpoints %}- `{{ number }}`: {{ breakpoint.name }}
{% endfor %}
- Set the layout on breakpoint `0` first.
- Add a smaller breakpoint only for what must change there, typically fewer
  columns on mobile (`columns: 1` on the smallest breakpoint).
- A config equal to the one before it is removed automatically, so you never
  need to copy values between breakpoints.

## Spacing and look

Spacing (`padding_*`, `margin_bottom`, `gap`) and widths (`max_width`) are
choices from a fixed scale, with a `custom` value as an escape hatch. Use
the scale; custom values make pages inconsistent.

The site's design defines colors and fonts. Use `background_color`,
`alternate_background` and `alternate_color` only as the existing pages do.
{% endautoescape %}
