# Imported only by django-xprez-mcp's autodiscovery; see xprez.contrib.xprez_mcp.
from xprez_mcp import mcp

from xprez.contrib.xprez_mcp.provider import XprezProvider

mcp.register(XprezProvider)
