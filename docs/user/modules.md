Modules
=======

Built-in modules
----------------

- Text — rich text with CKEditor
- Quote — single quote block
- Gallery — image gallery
- Files — downloadable attachments
- Video — embed video
- Numbers — numeric stats/features
- Code input — user-editable code snippet
- Code template — pre-defined code templates
- Anchor — in-page anchor links

Custom modules
--------------

Subclass `Module` in your app, set `front_template_name` to your template path, and define your fields. Custom modules auto-register and appear in the same admin UI and frontend. See the [built-in modules](../../xprez/modules/) source for examples.

### Simple module

```python
from django.db import models
from xprez.models import Module

class MyModule(Module):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)

    front_template_name = "myapp/modules/my.html"
```

Template `myapp/templates/myapp/modules/my.html`:

```django-html
{% extends "xprez/modules/base.html" %}

{% block content %}
    <div>
        <h3>{{ module.title }}</h3>
        {{ module.body|linebreaks }}
    </div>
{% endblock %}
```

### Module with custom config class

Use `config_model` and a `ModuleConfig` subclass for breakpoint-specific layout. `ModuleConfig` is the base for all module configs and is concrete, so modules that omit `config_model` use it as the default. CSS variables and classes come from the config model via `CssMixin` (`xprez.models.mixins.css`). Override `get_css_variables` and `get_css_classes` in your config subclass:

```python
from django.db import models
from xprez.models import Module
from xprez.models.configs import ModuleConfig

class FeaturedModule(Module):
    title = models.CharField(max_length=200)
    config_model = "myapp.FeaturedConfig"
    front_template_name = "myapp/modules/featured.html"

class FeaturedConfig(ModuleConfig):
    spacing = models.PositiveIntegerField(null=True, blank=True, default=24)
    compact = models.BooleanField(default=False)

    def get_css_classes(self):
        classes = super().get_css_classes()
        classes["featured-compact"] = self.compact
        return classes

    def get_css_variables(self):
        css_variables = super().get_css_variables()
        if self.spacing:
            css_variables["spacing"] = f"{self.spacing}px"
        return css_variables
```

### MultiModule (multiple items)

Subclass `MultiModule` for modules with repeatable items (e.g. gallery, numbers):

```python
from django.db import models
from xprez.models import MultiModule, MultiModuleItem

class TeamModule(MultiModule):
    name = models.CharField(max_length=200, blank=True)
    front_template_name = "myapp/modules/team.html"
    admin_form_class = "myapp.forms.TeamModuleForm"
    admin_item_form_class = "myapp.forms.TeamMemberForm"
    admin_item_template_name = "myapp/admin/team_member.html"

class TeamMember(MultiModuleItem):
    module = models.ForeignKey(
        TeamModule, related_name="items", on_delete=models.CASCADE, editable=False
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="team", null=True, blank=True)
```

Template `myapp/templates/myapp/modules/team.html`:

```django-html
{% extends "xprez/modules/base.html" %}

{% block content %}
    <div>
        {% for item in items %}
            <div>
                {% if item.photo %}
                    <img src="{{ item.photo.url }}" alt="{{ item.name }}">
                {% endif %}
                <h4>{{ item.name }}</h4>
                {% if item.role %}<p>{{ item.role }}</p>{% endif %}
            </div>
        {% endfor %}
    </div>
{% endblock %}
```
