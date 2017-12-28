from django.contrib import admin
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR, IS_POPUP_VAR
from django.contrib.auth.admin import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import all_valid
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.contrib.admin.utils import unquote
from django.utils.encoding import force_text
from django.utils.html import escape
from django.contrib.admin import helpers
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.shortcuts import redirect

from . import models
from . import contents_manager
from .settings import XPREZ_CONTAINER_MODEL_CLASS


class XprezAdmin(admin.ModelAdmin):
    change_form_extend_template = 'admin/change_form.html'
    change_form_template = 'xprez/admin/xprez_changeform.html'
    allowed_contents = '__all__'
    excluded_contents = None

    def _get_allowed_contents(self):
        content_types = []
        if self.allowed_contents == '__all__':
            content_types = contents_manager.all_as_list()
        else:
            for ct in self.allowed_contents:
                content_types.append(contents_manager.get(ct))
        if self.excluded_contents:
            for ct in self.excluded_contents:
                ct = contents_manager.get(ct)
                if ct in content_types:
                    content_types.remove(ct)
        return content_types

    def _get_container_instance(self, request, object_pk):
        app_label, model_name = XPREZ_CONTAINER_MODEL_CLASS.split('.')
        klass = apps.get_model(app_label, model_name)
        return klass.objects.get(pk=object_pk)
        # return self.get_object(request, object_pk)

    def _show_xprez_toolbar(self, request, object_pk=None):
        return bool(object_pk)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not extra_context:
            extra_context = {}
        contents_media = contents_manager.admin_media()

        extra_context.update({
            'content_types': self._get_allowed_contents(),
            'contents_media': contents_media,
            'change_form_extend_template': self.change_form_extend_template
        })
        return super(XprezAdmin, self).change_view(request, object_id, form_url, extra_context)

    @csrf_protect_m
    @transaction.atomic
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        contents = None
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        model = self.model
        opts = model._meta

        if request.method == 'POST' and '_saveasnew' in request.POST:
            object_id = None

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if not self.has_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                    'name': force_text(opts.verbose_name), 'key': escape(object_id)})

        ModelForm = self.get_form(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            contents = []
            all_content_forms_valid = True
            if obj and obj.contents:
                for content in obj.contents.all():
                    content = content.polymorph()
                    content.build_admin_form(request.POST, request.FILES)
                    if not content.is_admin_form_valid():
                        all_content_forms_valid = False
                    contents.append(content)
            if form.is_valid() and all_content_forms_valid:
                form_validated = True
                new_object = self.save_form(request, form, change=not add)
                for content in contents:
                    content.save_admin_form()
            else:
                form_validated = False
                new_object = form.instance
            formsets, inline_instances = self._create_formsets(request, new_object, change=not add)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                change_message = self.construct_change_message(request, form, formsets, add)
                if add:
                    self.log_addition(request, new_object, change_message)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
            else:
                form_validated = False
        else:
            all_content_forms_valid = True
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(request, form.instance, change=False)
            else:
                form = ModelForm(instance=obj)
                contents = []
                if obj.contents:
                    for content in obj.contents.all():
                        content = content.polymorph()
                        content.build_admin_form()
                        contents.append(content)
                formsets, inline_instances = self._create_formsets(request, obj, change=True)

        adminForm = helpers.AdminForm(
            form,
            list(self.get_fieldsets(request, obj)),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        context = dict(
            self.admin_site.each_context(request),
            title=(_('Add %s') if add else _('Change %s')) % force_text(opts.verbose_name),
            adminform=adminForm,
            object_id=object_id,
            original=obj,
            is_popup=(IS_POPUP_VAR in request.POST or
                      IS_POPUP_VAR in request.GET),
            to_field=to_field,
            media=media,
            inline_admin_formsets=inline_formsets,
            errors=helpers.AdminErrorList(form, formsets) or not all_content_forms_valid,
            preserved_filters=self.get_preserved_filters(request),
            contents=contents,
            copy_url_name='admin:' + self.model._meta.model_name + '_copy',
            copy_supported=hasattr(obj, 'copy'),
            change_form_extend_template=self.change_form_extend_template,
            show_xprez_toolbar=self._show_xprez_toolbar(request, object_id)
        )

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if request.method == 'POST' and not form_validated and "_saveasnew" in request.POST:
            context['show_save'] = False
            context['show_save_and_continue'] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)

    def add_content_view(self, request, page_pk, content_type):
        content_class = models.contents_manager.get(content_type)

        container = self._get_container_instance(request, page_pk)
        content = content_class.create_for_page(container)
        content.build_admin_form()
        return JsonResponse({'template': content.render_admin(), 'content_pk': content.pk})

    def copy_content_view(self, request, content_pk):
        content = models.Content.objects.get(pk=content_pk).polymorph()
        new_content = content.copy()
        new_content.build_admin_form()
        return JsonResponse({'template': new_content.render_admin(), 'content_pk': new_content.pk})

    def copy_view(self, request, page_pk):
        inst = self.model.objects.get(pk=page_pk)
        copy = inst.copy()
        info = (copy._meta.app_label, copy._meta.model_name)
        return redirect('admin:%s_%s_change' % info, copy.pk)

    @csrf_exempt
    def delete_content_view(self, request, content_pk):
        if request.method == 'POST':
            content = models.Content.objects.get(pk=content_pk)
            content.delete()
        return HttpResponse()

    def get_urls(self):
        urls = super(XprezAdmin, self).get_urls()
        my_urls = [
            url(r'^%s/copy/(?P<page_pk>\d+)/$' % self.model._meta.model_name, self.admin_site.admin_view(self.copy_view), name=self.model._meta.model_name+'_copy'),
            url(r'^ajax/add-content/(?P<page_pk>\d+)/(?P<content_type>[A-z0-9-]+)/$', self.admin_site.admin_view(self.add_content_view), name='ajax_add_content'),
            url(r'^ajax/delete-content/(?P<content_pk>\d+)/$', self.admin_site.admin_view(self.delete_content_view), name='ajax_delete_content'),
            url(r'^ajax/copy-content/(?P<content_pk>\d+)/$', self.admin_site.admin_view(self.copy_content_view), name='ajax_copy_content'),

        ]
        return my_urls + urls


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('position', 'content_type', 'page', )


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'position', )