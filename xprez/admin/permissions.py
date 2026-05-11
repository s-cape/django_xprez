from xprez.conf import settings
from xprez.utils import import_class

xprez_staff_member_required = import_class(settings.XPREZ_STAFF_MEMBER_REQUIRED)
