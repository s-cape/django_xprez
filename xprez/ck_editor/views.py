from os import makedirs, path

from django import forms
from django.conf import settings as django_settings
from django.core.exceptions import SuspiciousFileOperation
from django.http import JsonResponse
from django.utils._os import safe_join
from django.utils.text import get_valid_filename

from xprez.admin.permissions import xprez_staff_member_required
from xprez.utils import random_string


class CkEditorUploadForm(forms.Form):
    upload = forms.FileField(required=True)


def _ckeditor_file_upload(request, directory):
    if request.method != "POST":
        return JsonResponse({}, status=405)
    form = CkEditorUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"error": "No file in 'upload'."}, status=400)

    try:
        upload_subdir = path.join(directory, random_string(16))
        full_directory = safe_join(django_settings.MEDIA_ROOT, upload_subdir)
    except SuspiciousFileOperation:
        return JsonResponse({"error": "Invalid directory."}, status=400)

    uploaded_file = form.cleaned_data["upload"]
    safe_filename = get_valid_filename(uploaded_file.name)
    makedirs(full_directory, exist_ok=True)

    destination_path = path.join(full_directory, safe_filename)
    with open(destination_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    relative_url = path.join(upload_subdir, safe_filename)
    return JsonResponse({"url": django_settings.MEDIA_URL + relative_url})


@xprez_staff_member_required
def ckeditor_file_upload(request, directory):
    return _ckeditor_file_upload(request, directory)
