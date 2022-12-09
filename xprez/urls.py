from . import autodiscover, contents_manager

autodiscover()


app_name = "xprez"

urlpatterns = [] + contents_manager.get_urls()
