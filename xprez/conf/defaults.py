XPREZ_SECTION_MODEL_CLASS = "xprez.Section"
XPREZ_CONTAINER_MODEL_CLASS = "xprez.Container"
XPREZ_CK_EDITOR_MODULE_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_GRID_BOXES_MODULE_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_TEXT_IMAGE_MODULE_WIDGET = (
    "xprez.ck_editor.widgets.CkEditorWidgetFullNoInsertPlugin"
)

XPREZ_MODULES_AUTOREGISTER = True
XPREZ_MODULES_AUTOREGISTER_BUILTINS = [
    "xprez.TextModule",
    "xprez.QuotesModule",
    "xprez.ImagesModule",
    "xprez.DownloadModule",
    "xprez.VideoModule",
    "xprez.NumbersModule",
    "xprez.CodeInputModule",
    "xprez.CodeTemplateModule",
]
XPREZ_MODULES_AUTOREGISTER_CUSTOM = "__all__"

XPREZ_DEFAULT_AVAILABLE_MODULES = "__all__"

XPREZ_CODE_TEMPLATES_DIR = None
XPREZ_CODE_TEMPLATES_PREFIX = "xprez/code_templates"
XPREZ_USE_ABSOLUTE_URI = False
XPREZ_BASE_URL = ""

XPREZ_STAFF_MEMBER_REQUIRED = (
    "django.contrib.admin.views.decorators.staff_member_required"
)

XPREZ_BREAKPOINTS = {
    0: {"infix": "", "name": "Basic style (&gt; 0px)"},
    1: {"infix": "sm", "name": "Small devices (&gt; 500px)"},
    2: {"infix": "md", "name": "Tablets (&gt; 768px)"},
    3: {"infix": "lg", "name": "Large devices (&gt; 992px)"},
    4: {"infix": "xl", "name": "Desktops (&gt; 1200px)"},
    5: {"infix": "xxl", "name": "Extra large devices (&gt; 1500px)"},
}
XPREZ_DEFAULT_BREAKPOINT = 0
