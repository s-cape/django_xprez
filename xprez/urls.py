from django.urls import path

from xprez import views

app_name = "xprez"

urlpatterns = [
    path("variables.css", views.variables_css, name="variables_css"),
]
