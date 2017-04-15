
from django.db import models
from django.core.urlresolvers import reverse
from xprez.models import ContentsContainer


class Page(ContentsContainer):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.__str__()

    def get_absolute_url(self):
        return reverse('page', args=[self.slug])

    class Meta:
        verbose_name_plural = 'Pages'
        verbose_name = 'Page'
