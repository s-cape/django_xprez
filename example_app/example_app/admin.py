from django.contrib import admin
from xprez.admin import XprezAdmin
from .models import Page


@admin.register(Page)
class PageAdmin(XprezAdmin):
    pass
