from django.db import models
from django.urls import reverse

from xprez.models import Container


class Page(Container):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("page", args=[self.slug])
