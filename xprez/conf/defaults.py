XPREZ_SECTION_MODEL_CLASS = "xprez.Section"
XPREZ_CONTAINER_MODEL_CLASS = "xprez.ContentsContainer"
XPREZ_CK_EDITOR_CONTENT_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_GRID_BOXES_CONTENT_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_TEXT_IMAGE_CONTENT_WIDGET = (
    "xprez.ck_editor.widgets.CkEditorWidgetFullNoInsertPlugin"
)

XPREZ_CONTENTS_AUTOREGISTER = True
# XPREZ_CONTENTS_AUTOREGISTER_BUILTINS = [
#     # 'mediumeditor',  # deprecated
#     "textcontent",
#     "ckeditor",
#     "gridboxes",
#     "quotecontent",
#     "gallery",
#     "downloadcontent",
#     "video",
#     "numberscontent",
#     # "featureboxes",  # deprecated
#     "codeinput",
#     "codetemplate",
#     "textimage",
#     # "anchor",  # not yet implemented, disabled by default
# ]
XPREZ_CONTENTS_AUTOREGISTER_BUILTINS = [
    "xprez.TextContent",
    "xprez.QuoteContent",
    "xprez.Gallery",
    "xprez.DownloadContent",
    "xprez.Video",
    "xprez.NumbersContent",
    "xprez.CodeInput",
    "xprez.CodeTemplate",
]
XPREZ_CONTENTS_AUTOREGISTER_CUSTOM = "__all__"

XPREZ_DEFAULT_ALLOWED_CONTENTS = "__all__"
XPREZ_DEFAULT_EXCLUDED_CONTENTS = None

XPREZ_CODE_TEMPLATES_DIR = ""
XPREZ_CODE_TEMPLATES_PREFIX = ""
XPREZ_USE_ABSOLUTE_URI = False
XPREZ_BASE_URL = ""

# XPREZ_JQUERY_INIT_MEDIA_JS = (
#     "admin/js/vendor/jquery/jquery.js",  # use django's jquery
#     "admin/js/jquery.init.js",  # call django's jquery init (which includes noconflict)
#     "xprez/admin/js/jquery_revert_noconflict.js",  # revert noconflict - $ is now global again
# )

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
