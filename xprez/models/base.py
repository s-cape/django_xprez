import warnings

from django.apps import apps
from django.db import models
from django.db.models import F, Max
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import re_path
from django.utils.decorators import method_decorator
from django.utils.functional import classproperty

from ..conf import settings
from ..permissions import xprez_staff_member_required
from ..utils import import_class

CLIPBOARD_TEXT_MAX_LENGTH = 100


class ContentsContainer(models.Model):
    front_template_name = "xprez/container.html"

    content_type = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.content_type = self.__class__.__name__.lower()
        super().save(*args, **kwargs)

    def polymorph(self):
        return getattr(self, self.content_type.lower())

    def copy_contents(self, for_container):
        for content in self.contents.all():
            content.polymorph().copy(for_container)

    def clipboard_verbose_name(self):
        return self.polymorph()._meta.verbose_name

    def clipboard_text_preview(self):
        return self.polymorph().__str__()

    def render_front(self, context):
        context["sections"] = self.get_sections_front()
        return render_to_string(self.front_template_name, context)

    def get_sections(self):
        if not hasattr(self, "_sections"):
            # TODO: prefetch section configs, contents (polymorphed) and content configs (polymorphed)
            self._sections = self.sections.filter(visible=True)
        return self._sections


class Section(models.Model):
    front_template_name = "xprez/section.html"
    admin_template_name = "xprez/admin/section.html"

    container = models.ForeignKey(
        settings.XPREZ_CONTAINER_MODEL_CLASS,
        on_delete=models.SET_NULL,
        related_name="sections",
        editable=False,
        null=True,
    )
    position = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)
    saved = models.BooleanField(default=False, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    changed = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    MAX_WIDTH_SMALL = "small"
    MAX_WIDTH_MEDIUM = "medium"
    MAX_WIDTH_FULL = "full"
    MAX_WIDTH_CUSTOM = "custom"
    MAX_WIDTH_CHOICES = (
        (MAX_WIDTH_SMALL, "small"),
        (MAX_WIDTH_MEDIUM, "medium"),
        (MAX_WIDTH_FULL, "full"),
        (MAX_WIDTH_CUSTOM, "custom"),
    )
    max_width_choice = models.CharField(
        verbose_name="Max width",
        max_length=100,
        choices=MAX_WIDTH_CHOICES,
        default=MAX_WIDTH_FULL,
    )
    max_width_custom = models.PositiveIntegerField(null=True, blank=True)

    alternate_color = models.BooleanField(default=False)
    background_color = models.CharField(max_length=30, blank=True)
    css_class = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ("position",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            for css_breakpoint in settings.XPREZ_BREAKPOINTS.keys():
                self.configs.get_or_create(css_breakpoint=css_breakpoint)

    def get_form_prefix(self):
        return "section-" + str(self.pk)

    def build_admin_form(self, admin, data=None, files=None):
        form_class = import_class("xprez.admin_forms.SectionForm")
        self.admin_form = form_class(
            instance=self, prefix=self.get_form_prefix(), data=data, files=files
        )
        self.admin_form.xprez_admin = admin
        self.admin_form.xprez_contents_all_valid = None
        self.admin_form.xprez_contents = [c.polymorph() for c in self.contents.all()]
        for content in self.admin_form.xprez_contents:
            content.build_admin_form(admin, data, files)

        # self.admin_form.xprez_contents = sorted(
        #     self.admin_form.xprez_contents,
        #     key=lambda content: int(content.admin_form["position"].value() or 0),
        # )

    def is_admin_form_valid(self):
        self.admin_form.xprez_contents_all_valid = True
        for content in self.admin_form.xprez_contents:
            if not content.is_admin_form_valid():
                self.admin_form.xprez_contents_all_valid = False
        return self.admin_form.is_valid() and self.admin_form.xprez_contents_all_valid

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.save()
        for content in self.admin_form.xprez_contents:
            content.save_admin_form(request)

    def render_admin(self, context):
        # xprez_admin = self.admin_form.xprez_admin
        form = self.admin_form
        context.update(
            {
                "section": self,
                "form": form,
                # "xprez_admin": xprez_admin,
                "allowed_contents": form.xprez_admin.xprez_get_allowed_contents(
                    container=self.container
                ),
            }
        )
        return render_to_string(self.admin_template_name, context)

    def get_contents(self):
        if not hasattr(self, "_contents"):
            self._contents = self.contents.filter(visible=True)
        return self._contents

    def get_configs(self):
        if not hasattr(self, "_configs"):
            self._configs = self.configs.filter(visible=True)
        return self._configs

    def render_front(self, context):
        context["section"] = self
        context["contents"] = self.get_front_contents()
        context["configs"] = self.get_front_configs()
        return render_to_string(self.front_template_name, context)


class Content(models.Model):
    config_model = "xprez.ContentConfig"
    form_class = "xprez.admin_forms.BaseContentForm"
    js_controller_class = "XprezContent"

    SIZE_FULL = "full"
    SIZE_MID = "mid"
    SIZE_TEXT = "text"
    SIZE_CHOICES = (
        (SIZE_FULL, "full"),
        (SIZE_MID, "mid"),
        (SIZE_TEXT, "text"),
    )

    # # TODO: remove
    # page = models.ForeignKey(
    #     settings.XPREZ_CONTAINER_MODEL_CLASS,
    #     on_delete=models.CASCADE,
    #     related_name="contents",
    #     editable=False,
    #     null=True,
    # )
    section = models.ForeignKey(
        settings.XPREZ_SECTION_MODEL_CLASS,
        on_delete=models.CASCADE,
        related_name="contents",
        # editable=False,
        # null=True,  # TODO: remove
    )
    position = models.PositiveSmallIntegerField(default=0)
    content_type = models.CharField(max_length=100, editable=False)

    # # TODO: remove
    # visible = models.BooleanField(default=True)
    # alternate_color = models.BooleanField(default=False)
    # background_color = models.CharField(max_length=30, blank=True)
    # css_class = models.CharField(max_length=100, null=True, blank=True)

    # MARGIN_BOTTOM_DEFAULT = 2
    # MARGIN_BOTTOM_CHOICES = (
    #     (0, "None"),
    #     (1, "S"),
    #     (2, "M"),
    #     (3, "L"),
    #     (4, "XL"),
    # )
    # margin_bottom = models.PositiveSmallIntegerField(
    #     choices=MARGIN_BOTTOM_CHOICES, default=MARGIN_BOTTOM_DEFAULT
    # )

    # PADDING_TOP_DEFAULT = 0
    # PADDING_TOP_CHOICES = (
    #     (0, "None"),
    #     (1, "S"),
    #     (2, "M"),
    #     (3, "L"),
    #     (4, "XL"),
    # )
    # padding_top = models.PositiveSmallIntegerField(
    #     choices=PADDING_TOP_CHOICES, default=PADDING_TOP_DEFAULT
    # )

    # PADDING_BOTTOM_DEFAULT = 0
    # PADDING_BOTTOM_CHOICES = (
    #     (0, "None"),
    #     (1, "S"),
    #     (2, "M"),
    #     (3, "L"),
    #     (4, "XL"),
    # )
    # padding_bottom = models.PositiveSmallIntegerField(
    #     choices=PADDING_BOTTOM_CHOICES, default=PADDING_BOTTOM_DEFAULT
    # )

    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    changed = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    class Meta:
        ordering = ("position",)

    class AdminMedia:
        js = []
        css = {}

    class FrontMedia:
        js = []
        css = {}

    def __str__(self):
        return self.content_type

    def save(self, *args, **kwargs):
        if not self.pk:
            self.content_type = self.class_content_type()
        super().save(*args, **kwargs)
        if self.pk:
            self.get_or_create_config(css_breakpoint=settings.XPREZ_DEFAULT_BREAKPOINT)

    @property
    def verbose_name(self):
        return self._meta.verbose_name.title()

    @classmethod
    def class_content_type(cls):
        return "{}.{}".format(
            cls._meta.app_label,
            cls._meta.object_name,
        )

    @classmethod
    def identifier(cls):
        return cls._meta.model_name

    @property
    def admin_template_name(self):
        return [
            "xprez/admin/contents/{}.html".format(self.identifier()),
            "xprez/admin/contents/base.html",
        ]

    @property
    def front_template_name(self):
        return "xprez/contents/{}.html".format(self.identifier())

    def polymorph(self):
        app_label, object_name = self.content_type.split(".")
        model = apps.get_model(app_label, object_name)
        if isinstance(self, model):
            return self
        else:
            return model.objects.get(pk=self.pk)

    def copy(self, for_container=None, save=True, position=None):
        if not for_container:
            for_container = self.container

        initial = {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
            if not field.primary_key
        }
        inst = self.__class__(**initial)
        if position is None:  # add to end
            inst.position = self._count_new_content_position(for_container)
        else:  # add on specific position
            inst.position = position
            if for_container.contents.filter(position=position).exists():
                for_container.contents.filter(position__gte=position).update(
                    position=F("position") + 1
                )
        inst.container = for_container
        if save:
            inst.save()
        return inst

    # @classmethod
    # def _count_new_content_position(cls, container):
    #     result = container.contents.all().aggregate(Max("position"))
    #     if result["position__max"] is not None:
    #         position = result["position__max"] + 1
    #     else:
    #         position = 0
    #     return position

    # @classmethod
    # def create_for_section(cls, section, position=None, **kwargs):
    #     if position is None:  # add to end
    #         position = cls._count_new_content_position(section)
    #     else:  # add on specific position
    #         if section.contents.filter(position=position).exists():
    #             section.contents.filter(position__gte=position).update(
    #                 position=F("position") + 1
    #             )
    #     return cls.objects.create(section=section, position=position, **kwargs)

    # @property
    # def page(self):
    #     warnings.warn(
    #         "page attribute is deprecated, use container instead.",
    #         DeprecationWarning,
    #         stacklevel=2,
    #     )
    #     return self.container

    # @classmethod
    # def create_for_page(cls, *args, **kwargs):
    #     warnings.warn(
    #         "create_for_page() is deprecated, use create_for_container() instead.",
    #         DeprecationWarning,
    #         stacklevel=2,
    #     )
    #     return cls.create_for_container(*args, **kwargs)

    def get_config_model(self):
        app_label, model_name = self.config_model.split(".")
        return apps.get_model(app_label, model_name)

    def get_or_create_config(self, css_breakpoint):
        config, created = self.get_config_model().objects.get_or_create(
            content=self,
            css_breakpoint=css_breakpoint,
        )
        return config

    def get_form_prefix(self):
        return "content-" + str(self.pk)

    def get_admin_form_class(self):
        cls = import_class(self.form_class)
        if cls._meta.model:
            return cls
        else:

            class ContentForm(cls):
                class Meta(cls.Meta):
                    model = self.__class__

            return ContentForm

    def build_admin_form(self, admin, data=None, files=None):
        form_class = self.get_admin_form_class()
        self.admin_form = form_class(
            instance=self, prefix=self.get_form_prefix(), data=data, files=files
        )
        self.admin_form.xprez_admin = admin

    def is_admin_form_valid(self):
        return self.admin_form.is_valid()

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.save()

    def render_admin(self, context):
        xprez_admin = self.admin_form.xprez_admin
        context.update(
            {
                "content": self,
                "xprez_admin": xprez_admin,
                "allowed_contents": xprez_admin.xprez_get_allowed_contents(
                    container=self.section.container
                ),
            }
        )
        return render_to_string(self.admin_template_name, context)

    def render_front(self, context):
        context["content"] = self
        return render_to_string(self.front_template_name, context)

    def admin_has_errors(self):
        return bool(self.admin_form.errors)

    @classmethod
    def get_urls(cls):
        return []

    @classproperty
    def icon_template_name(cls):
        return [
            "xprez/admin/icons/contents/{}.html".format(cls.class_content_type()),
            "xprez/admin/icons/contents/default.html",
        ]

    @classproperty
    def icon(cls):
        return render_to_string(cls.icon_template_name)

    def clipboard_verbose_name(self):
        return self.polymorph()._meta.verbose_name

    def clipboard_text_preview(self):
        return ""


class FormsetContent(Content):
    formset_factory = NotImplemented

    class Meta:
        abstract = True

    def get_formset_queryset(self):
        raise NotImplementedError()

    def build_admin_form(self, admin, data=None, files=None):
        super().build_admin_form(admin, data)
        FormSet = import_class(self.formset_factory)
        self.formset = FormSet(
            instance=self,
            queryset=self.get_formset_queryset(),
            data=data,
            files=files,
            prefix="{}s-{}".format(self.identifier(), self.pk),
        )

    def save_admin_form(self, request):
        super().save_admin_form(request)
        self.formset.save()

    def is_admin_form_valid(self):
        return self.admin_form.is_valid() and self.formset.is_valid()

    def admin_has_errors(self):
        return super().admin_has_errors() or (
            self.formset.total_error_count() > 0 and not self.formset.is_valid()
        )

    def copy(self, for_container=None, save=True, position=None):
        inst = super().copy(for_container, save=save, position=position)
        if save:
            self.copy_items(inst)
        return inst

    def copy_items(self, inst):
        for item in self.get_formset_queryset():
            item.copy(inst)


class AjaxUploadFormsetContent(FormsetContent):
    admin_formset_item_template_name = NotImplemented

    class Meta:
        abstract = True

    class AdminMedia:
        js = (
            "xprez/admin/libs/dropzone/dropzone.js",
            "xprez/admin/js/ajax_upload_formset.js",
        )

    @classmethod
    @method_decorator(xprez_staff_member_required)
    def upload_file_view(cls, request, content_pk):
        content = cls.objects.get(pk=content_pk)
        file_list = request.FILES.getlist("file")
        if len(file_list) > 0:
            file_ = file_list[0]
            FormSet = import_class(cls.formset_factory)
            item = FormSet.model.create_from_file(file_, content)
            queryset = content.get_formset_queryset()
            item_formset = FormSet(
                instance=content,
                queryset=queryset,
                prefix="{}s-{}".format(cls.identifier(), content.pk),
            )
            item_form = item_formset.forms[-1]
            return JsonResponse(
                data={
                    "form": item_form.as_p(),
                    "template": render_to_string(
                        cls.admin_formset_item_template_name,
                        {
                            "item": item,
                            "content": content,
                            "number": queryset.count() - 1,
                        },
                    ),
                }
            )
        return JsonResponse(status=400, data={"error": "No files uploaded"})

    @classmethod
    def get_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            re_path(
                r"^%s/upload-item/(?P<content_pk>\d+)/" % cls_name,
                cls.upload_file_view,
                name="%s_ajax_upload_item" % cls_name,
            ),
        ]


class ContentItem(models.Model):
    content_foreign_key = NotImplemented

    class Meta:
        abstract = True

    def copy(self, for_content, save=True):
        if not for_content:
            for_content = getattr(self, self.content_foreign_key)
        initial = {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
            if not field.primary_key
        }
        inst = self.__class__(**initial)
        setattr(inst, self.content_foreign_key, for_content)
        if save:
            inst.save()
        return inst
