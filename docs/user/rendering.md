Rendering
=========

In your template:

1. Load the xprez template tags.
2. Output front media (JS/CSS) for the container — typically in the `<head>`.
3. Render the container where the content should appear — typically in the main body.

```django-html
{% load xprez %}
{% xprez_front_media page %}
{% xprez_container_render_front page %}
```

Put `{% xprez_front_media page %}` in the head section of your base template. Put `{% xprez_container_render_front page %}` where the page content should render.
