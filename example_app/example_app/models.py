
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

    def copy(self):
        new_inst = self.__class__(title="Copy of " + self.title)
        it = 1
        while True:
            new_slug = new_inst.slug + str(it)
            if not self.__class__.objects.filter(slug=new_slug).exists():
                new_inst.slug = new_slug
                break
            it += 1
        new_inst.save()
        self.copy_contents(new_inst)
        return new_inst

    class Meta:
        verbose_name_plural = 'Pages'
        verbose_name = 'Page'
