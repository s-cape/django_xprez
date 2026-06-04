from django.urls import path

from . import views

app_name = "sorl_thumbnail_lazy"

urlpatterns = [
    path("lazy/<str:payload>/<str:sig>/", views.lazy_thumbnail, name="lazy_thumbnail"),
]
