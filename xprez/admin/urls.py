from xprez import autodiscover, module_manager

autodiscover()


app_name = "xprez"

urlpatterns = [] + module_manager.get_urls()
