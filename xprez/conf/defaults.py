XPREZ_CONTAINER_MODEL_CLASS = "xprez.ContentsContainer"
XPREZ_CK_EDITOR_CONTENT_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_GRID_BOXES_CONTENT_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_TEXT_IMAGE_CONTENT_WIDGET = (
    "xprez.ck_editor.widgets.CkEditorWidgetFullNoInsertPlugin"
)

XPREZ_CONTENTS_AUTOREGISTER = True
XPREZ_CONTENTS_AUTOREGISTER_BUILTINS = [
    # 'mediumeditor',  # deprecated
    "ckeditor",
    "gridboxes",
    "quotecontent",
    "gallery",
    "downloadcontent",
    "video",
    "numberscontent",
    # "featureboxes",  # deprecated
    "codeinput",
    "codetemplate",
    "textimage",
    # "anchor",  # not yet implemented, disabled by default
]
XPREZ_CONTENTS_AUTOREGISTER_CUSTOM = "__all__"

XPREZ_DEFAULT_ALLOWED_CONTENTS = "__all__"
XPREZ_DEFAULT_EXCLUDED_CONTENTS = None

XPREZ_CODE_TEMPLATES_DIR = ""
XPREZ_CODE_TEMPLATES_PREFIX = ""
XPREZ_USE_ABSOLUTE_URI = False
XPREZ_BASE_URL = ""

XPREZ_JQUERY_INIT_MEDIA_JS = (
    "admin/js/vendor/jquery/jquery.js",  # use django's jquery
    "admin/js/jquery.init.js",  # call django's jquery init (which includes noconflict)
    "xprez/admin/js/jquery_revert_noconflict.js",  # revert noconflict - $ is now global again
)
