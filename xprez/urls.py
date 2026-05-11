from django.urls import path

from xprez import views

app_name = "xprez"

urlpatterns = [
    path("variables.css", views.css.css_variables_global, name="css_variables_global"),
    path("photoswipe/", views.photoswipe, name="photoswipe"),
]
