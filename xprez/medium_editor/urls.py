from django.conf.urls import include, url

from .views import medium_file_upload, medium_file_delete

urlpatterns = [
    url(r'^file-upload/(?P<directory>[/\w-]+)/$', medium_file_upload, name='medium_file_upload'),
    url(r'^file-delete/$', medium_file_delete, name='medium_file_delete'),
]
