from xprez import autodiscover, module_type_manager

autodiscover()


app_name = "xprez"

urlpatterns = [] + module_type_manager.get_urls()
