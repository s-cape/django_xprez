from xprez import constants

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
    "xprez.QuoteModule",
    "xprez.GalleryModule",
    "xprez.DownloadsModule",
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
    0: {"name": "Basic style (&gt; 0px)", "min_width": 0},
    1: {"name": "Small devices (&gt; 500px)", "min_width": 500},
    2: {"name": "Tablets (&gt; 768px)", "min_width": 768},
    3: {"name": "Large devices (&gt; 992px)", "min_width": 992},
    4: {"name": "Desktops (&gt; 1200px)", "min_width": 1200},
    5: {"name": "Extra large devices (&gt; 1500px)", "min_width": 1500},
}
XPREZ_DEFAULT_BREAKPOINT = 0

XPREZ_SECTION_CONFIG_DEFAULTS = {
    "columns": 1,
    "margin_bottom_choice": constants.MARGIN_MEDIUM,
    "padding_left_choice": constants.PADDING_NONE,
    "padding_right_choice": constants.PADDING_NONE,
    "padding_top_choice": constants.PADDING_NONE,
    "padding_bottom_choice": constants.PADDING_NONE,
    "gap_choice": constants.GAP_FULL,
    "vertical_align": constants.VERTICAL_ALIGN_TOP,
    "horizontal_align": constants.HORIZONTAL_ALIGN_LEFT,
}

XPREZ_MODULE_CONFIG_DEFAULTS = {
    "default": {
        "colspan": 1,
        "rowspan": 1,
        "vertical_align": constants.VERTICAL_ALIGN_TOP,
        "horizontal_align": constants.HORIZONTAL_ALIGN_LEFT,
    },
    # "xprez.TextModule": {
    #     "horizontal_align": constants.HORIZONTAL_ALIGN_STRETCH,
    # },
    # "xprez.GalleryModule": {
    #     "colspan": 2,
    #     "gallery_columns": 3,
    #     "gallery_gap": constants.GAP_SMALL,
    # },
}
