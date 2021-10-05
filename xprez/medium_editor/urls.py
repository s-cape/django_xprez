from django.conf.urls import url

from .views import medium_file_delete, medium_file_upload

urlpatterns = [
    url(r'^file-upload/(?P<directory>[/\w-]+)/$', medium_file_upload, name='medium_file_upload'),
    url(r'^file-delete/$', medium_file_delete, name='medium_file_delete'),
]
