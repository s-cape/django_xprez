from xprez import autodiscover, module_registry

autodiscover()


app_name = "xprez"

urlpatterns = [] + module_registry.get_urls()
