Standalone (outside Django admin)
=================================

Xprez can be used without Django admin by using `XprezAdminMixin` instead of `XprezAdmin`. You provide your own views, templates, and URL routing.

1. Create an admin-like class
-----------------------------

Subclass `XprezAdminMixin` and set `model`, `model_form`, and `xprez_url_namespace`. The `model_form` must inherit from `ModelForm` for your Container model:

```python
from django import forms
from xprez import module_registry
from xprez.admin import XprezAdminMixin

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ()  # or ("title", "slug") if you have regular fields

class PageXprezAdmin(XprezAdminMixin):
    model = Page
    model_form = PageForm
    xprez_url_namespace = "myapp"

    def xprez_allowed_modules(self, container=None):
        allowed = ["xprez.TextModule", "xprez.GalleryModule", "myapp.TeamModule"]
        if container and container.is_landing:
            allowed += ["myapp.HeroModule"]
        return module_registry.modules(include=allowed)

page_xprez_admin = PageXprezAdmin()
```

`xprez_get_form()` returns a form class that mixes `XprezModelFormMixin` with your `model_form`; you instantiate it with `request.POST`, `request.FILES`, and `instance`.

2. Create the edit view
-----------------------

Use `xprez_get_form()` for the form and call `form.xprez_save(request)` on save:

```python
from django.shortcuts import get_object_or_404, redirect, render

def page_edit(request, pk):
    page = get_object_or_404(Page, pk=pk)
    FormClass = page_xprez_admin.xprez_get_form()

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=page)
        if form.is_valid():
            obj = form.save()
            if hasattr(form, "xprez_save"):
                form.xprez_save(request)
            return redirect("page_detail", obj.pk)
    else:
        form = FormClass(instance=page)

    return render(request, "myapp/page_edit.html", {"form": form, "page": page})
```

3. Include xprez URLs
---------------------

Add the xprez admin URLs to your URL config. They provide add, duplicate, clipboard, and config endpoints used by the frontend JS:

```python
# urls.py
from myapp.views import page_edit, page_xprez_admin

app_name = "myapp"

urlpatterns = [
    path("<int:pk>/edit/", page_edit, name="page_edit"),
    path("xprez/", include(page_xprez_admin.xprez_admin_urls())),
]
```

The `xprez_url_namespace` must match the Django URL namespace that contains these patterns. In this example both are `"myapp"`.

Example project URL include with namespace:

```python
# project urls.py
urlpatterns = [
    path("cms/", include(("myapp.urls", "myapp"), namespace="myapp")),
]
```

4. Template
-----------

Include the xprez editor and output admin media in the head:

```django-html
{% extends "base.html" %}

{% block head %}
    {{ form.xprez_admin.xprez_admin_media }}
{% endblock %}

{% block content %}
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        {% include "xprez/admin/xprez.html" with form=form %}
        <button type="submit">Save</button>
    </form>
{% endblock %}
```

5. Permissions
--------------

`XprezAdminMixin.xprez_admin_view` returns the view unchanged. Override it to add your permission check:

```python
from myapp.decorators import login_required

class PageXprezAdmin(XprezAdminMixin):
    # ...

    def xprez_admin_view(self, view):
        return login_required(view)
```

Or set `XPREZ_STAFF_MEMBER_REQUIRED` in settings to a custom decorator path; it is used by some xprez internals.
