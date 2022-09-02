from django.urls import re_path

from .views import medium_file_delete, medium_file_upload

urlpatterns = [
    re_path(r'^file-upload/(?P<directory>[/\w-]+)/$', medium_file_upload, name='medium_file_upload'),
    re_path(r'^file-delete/$', medium_file_delete, name='medium_file_delete'),
]
