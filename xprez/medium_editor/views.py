# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# import random
from os import makedirs, path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from xprez.utils import random_string

# def random_string(length, include_special_chars=False):
#     chars = "abcdefghijklmnopqrstuvwxyz0123456789"
#     if include_special_chars:
#         chars += "!@#$%^&*(-_=+)"
#     return ''.join([random.choice(chars) for i in range(length)])


@csrf_exempt
@staff_member_required
def medium_file_upload(request, directory):
    if request.method == 'POST':
        file_data = request.FILES['files[]']
        name = file_data.name
        random_dir_name = random_string(16)
        full_directory = path.join(settings.MEDIA_ROOT, directory, random_dir_name)
        if not path.isdir(full_directory):
            makedirs(full_directory)

        with open(path.join(full_directory, name), 'wb+') as destination:
            for chunk in file_data.chunks():
                destination.write(chunk)

        filename = path.join(directory, random_dir_name, name)
        response_data = {
            'files': [{'url': settings.MEDIA_URL + filename}]
        }
        return JsonResponse(response_data)


@csrf_exempt
@staff_member_required
def medium_file_delete(request):
    # do nothing, we want to keep the file

    # full_path = request.POST.get('file')
    # if full_path:
    #     filepath = full_path.split('media/')[-1]
    #     if default_storage.exists(filepath):
    #         print 'existuje', filepath
    #         default_storage.delete(filepath)
    #     else:
    #         print 'neexistuje', filepath

    return JsonResponse({})
