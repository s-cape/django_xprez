from django.db import models
from django.db.models import Max
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf.urls import url
from django.template.loader import render_to_string

from .. import settings as xprez_settings
from ..utils import import_class


class ContentsContainer(models.Model):
    pass


class Content(models.Model):
    form_class = NotImplemented
    admin_template_name = NotImplemented
    front_template_name = NotImplemented
    verbose_name = NotImplemented
    SIZE_FULL = 'full'
    SIZE_MID = 'mid'
    SIZE_TEXT = 'text'
    SIZE_CHOICES = (
        (SIZE_FULL, 'full'),
        (SIZE_MID, 'mid'),
        (SIZE_TEXT, 'text'),
    )

    page = models.ForeignKey(xprez_settings.XPREZ_CONTAINER_MODEL_CLASS, related_name='contents')
    position = models.PositiveSmallIntegerField()
    content_type = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, verbose_name='created')
    changed = models.DateTimeField(auto_now=True, editable=False, db_index=True, verbose_name='changed')

    class Meta:
        ordering = ('position',)

    class AdminMedia:
        js = []
        css = []

    class FrontMedia:
        js = []
        css = []

    def __str__(self):
        return self.content_type

    def __unicode__(self):
        return self.__str__()

    def polymorph(self):
        obj = getattr(self, self.content_type.lower())
        return obj

    def copy(self, for_page=None):
        if not for_page:
            for_page = self.page

        initial = dict([
            (field.name, getattr(self, field.name))
            for field in self._meta.fields if not field.primary_key
        ])
        inst = self.__class__(**initial)
        inst.position = self._count_new_content_position(for_page)
        inst.page = for_page
        inst.save()
        return inst

    def save(self, *args, **kwargs):
        if not self.pk:
            self.content_type = self.__class__.__name__.lower()
        return super(Content, self).save(*args, **kwargs)

    @classmethod
    def _count_new_content_position(cls, page):
        result = page.contents.all().aggregate(Max('position'))
        if result['position__max'] is not None:
            position = result['position__max'] + 1
        else:
            position = 0
        return position

    @classmethod
    def create_for_page(cls, page):
        position = cls._count_new_content_position(page)
        return cls.objects.create(page=page, position=position)

    def build_admin_form(self, data=None, files=None):
        form_class = import_class(self.form_class)
        self.admin_form = form_class(instance=self, prefix='content-' + str(self.pk), data=data, files=files)

    def is_admin_form_valid(self):
        return self.admin_form.is_valid()

    def save_admin_form(self):
        inst = self.admin_form.save(commit=False)
        inst.save()

    def render_admin(self):
        return render_to_string(self.admin_template_name, {'content': self})

    def show_front(self):
        """
        We may want to display content on frontent only when certain its attributes are filled 
        """
        return True

    def render_front(self):
        if self.show_front():
            return render_to_string(self.front_template_name, {'content': self})
        return ''

    def admin_has_errors(self):
        return bool(self.admin_form.errors)

    @classmethod
    def get_urls(cls):
        return []

    @classmethod
    def identifier(cls):
        return cls.__name__.lower()


class FormsetContent(Content):

    formset_factory = NotImplemented

    class Meta:
        abstract = True

    def get_formset_queryset(self):
        raise NotImplementedError()

    def build_admin_form(self, data=None, files=None):
        super(FormsetContent, self).build_admin_form(data)
        FormSet = import_class(self.formset_factory)
        self.formset = FormSet(instance=self, queryset=self.get_formset_queryset(), data=data, files=files, prefix='{}s-{}'.format(self.identifier(), self.pk))

    def save_admin_form(self):
        super(FormsetContent, self).save_admin_form()
        self.formset.save()

    def is_admin_form_valid(self):
        return self.admin_form.is_valid() and self.formset.is_valid()

    def admin_has_errors(self):
        return super(FormsetContent, self).admin_has_errors() or self.formset.total_error_count() > 0

    def copy(self, for_page=None):
        inst = super(FormsetContent, self).copy(for_page)
        # todo
        return inst


class AjaxUploadFormsetContent(FormsetContent):
    admin_formset_item_template_name = NotImplemented

    class Meta:
        abstract = True

    class AdminMedia:
        js = ('xprez/admin/libs/dropzone/dropzone.js', 'xprez/admin/js/ajax_upload_formset.js')

    @classmethod
    @method_decorator(staff_member_required)
    def upload_file_view(cls, request, content_pk):
        content = cls.objects.get(pk=content_pk)
        file_list = request.FILES.getlist('file')
        if len(file_list) > 0:
            file_ = file_list[0]
            FormSet = import_class(cls.formset_factory)
            item = FormSet.model.create_from_file(file_, content)
            queryset = content.get_formset_queryset()
            item_formset = FormSet(instance=content, queryset=queryset, prefix='{}s-{}'.format(cls.identifier(), content.pk))
            item_form = item_formset.forms[-1]
            return JsonResponse(data={
                'form': item_form.as_p(),
                'template': render_to_string(cls.admin_formset_item_template_name, {'item': item, 'content': content, 'number': queryset.count() - 1})
            })

    @classmethod
    def get_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            url(r'^%s/upload-item/(?P<content_pk>\d+)/' % cls_name, cls.upload_file_view, name='%s_ajax_upload_item' % cls_name),
        ]
