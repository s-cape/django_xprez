from django.urls import include, path

from xprez import views

app_name = "xprez"

urlpatterns = [
    path("variables.css", views.css.css_variables_global, name="css_variables_global"),
    path("photoswipe/", views.photoswipe, name="photoswipe"),
    path("thumbnail/", include("xprez.contrib.sorl_thumbnail.lazy.urls")),
]
