from . import autodiscover
from .models import contents_manager

autodiscover()


app_name = 'xprez'

urlpatterns = [] + contents_manager.get_urls()

