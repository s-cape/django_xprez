from django.utils.translation import gettext_lazy as _

from xprez import constants

XPREZ_CK_EDITOR_MODULE_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFullWithUpload"
XPREZ_CK_EDITOR_FILE_UPLOAD_URL_NAME = (
    None  # only needed when using ck_editor outside of xprez admin
)
XPREZ_CK_EDITOR_FILE_UPLOAD_DIR = "xprez_ckeditor_uploads"
XPREZ_CK_EDITOR_SIMPLE_CONFIG = {
    "toolbar": ("bold", "italic", "link"),
    "blockToolbar": (),
}
XPREZ_CK_EDITOR_FULL_CONFIG = {
    "blockToolbar": (
        "heading",
        "|",
        "blockQuote",
        "bulletedList",
        "numberedList",
    ),
    "toolbar": (
        "bold",
        "italic",
        "link",
        "|",
        "heading",
        "|",
        "blockQuote",
        "bulletedList",
        "numberedList",
    ),
    "placeholder": "Type your text",
    "link": {
        "decorators": {
            "toggleButtonPrimary": {
                "mode": "manual",
                "label": "Primary button",
                "classes": ["btn", "btn-primary"],
            },
            "toggleButtonSecondary": {
                "mode": "manual",
                "label": "Secondary button",
                "classes": ["btn", "btn-secondary"],
            },
            "openInNewTab": {
                "mode": "manual",
                "label": "Open in a new tab",
                "defaultValue": False,
                "attributes": {
                    "target": "_blank",
                },
            },
        }
    },
    "heading": {
        "options": (
            {
                "model": "paragraph",
                "title": "Paragraph",
                "class": "ck-heading_paragraph",
            },
            {
                "model": "heading2",
                "view": "h2",
                "title": "Heading 2",
                "class": "ck-heading_heading2",
            },
            {
                "model": "heading3",
                "view": "h3",
                "title": "Heading 3",
                "class": "ck-heading_heading3",
            },
            {
                "model": "heading4",
                "view": "h4",
                "title": "Heading 4",
                "class": "ck-heading_heading4",
            },
        ),
    },
    "fontSize": {
        "options": (
            "tiny",
            "default",
            "big",
        )
    },
}

XPREZ_MODULES_AUTOREGISTER = True
XPREZ_MODULES_AUTOREGISTER_BUILTINS = [
    "xprez.TextModule",
    "xprez.QuoteModule",
    "xprez.GalleryModule",
    "xprez.AccordionModule",
    "xprez.FilesModule",
    "xprez.VideoModule",
    "xprez.NumbersModule",
    "xprez.CodeInputModule",
    "xprez.CodeTemplateModule",
    "xprez.AnchorModule",
    "xprez.ModuleSymlink",
]
XPREZ_MODULES_AUTOREGISTER_CUSTOM = "__all__"

XPREZ_MODULES_ALLOWED = "__all__"
XPREZ_MODULES_ALLOWED_EXCLUDE = ()
XPREZ_MODULES_ADD_MENU = None
XPREZ_MODULES_ADD_MENU_EXCLUDE = ("xprez.ModuleSymlink",)


XPREZ_CODE_TEMPLATES_DIR = None
XPREZ_CODE_TEMPLATES_PREFIX = "xprez/code_templates"
XPREZ_USE_ABSOLUTE_URI = False
XPREZ_BASE_URL = ""

XPREZ_FRONT_CACHE_ENABLED = False
XPREZ_FRONT_CACHE_TIMEOUT = None  # None = use cache backend default

XPREZ_STAFF_MEMBER_REQUIRED = (
    "django.contrib.admin.views.decorators.staff_member_required"
)

XPREZ_BREAKPOINTS = {
    0: {"name": _("Base style (all sizes &lt; ∞)"), "max_width": None},
    1: {"name": _("Desktops (&lt; 1500px)"), "max_width": 1499},
    2: {"name": _("Large devices (&lt; 1200px)"), "max_width": 1199},
    3: {"name": _("Tablets (&lt; 992px)"), "max_width": 991},
    4: {"name": _("Small devices (&lt; 768px)"), "max_width": 767},
    5: {"name": _("Mobile (&lt; 500px)"), "max_width": 499},
}
XPREZ_SRCSET_WIDTHS = (160, 320, 480, 640, 960, 1280, 1920, 2560)
XPREZ_IMAGE_EXTENSIONS = (
    "avif",
    "bmp",
    "gif",
    "jpeg",
    "jpg",
    "png",
    "svg",
    "tiff",
    "webp",
)
XPREZ_VIDEO_EXTENSIONS = ("avi", "mov", "mp4", "ogg", "webm")

XPREZ_VIDEO_PROVIDERS = (
    "xprez.modules.video.YouTubeVideoProvider",
    "xprez.modules.video.VimeoVideoProvider",
)

XPREZ_ADMIN_MEDIA_JS = (
    "xprez/admin/libs/sortablejs/sortable-1.15.6.min.js",
    "xprez/admin/js/xprez.min.js",
)
XPREZ_ADMIN_MEDIA_CSS = {"all": ("xprez/styles/xprez_backend.css",)}
XPREZ_FRONT_MEDIA_JS = ()
XPREZ_FRONT_MEDIA_CSS = {}

XPREZ_DEFAULTS = {
    "section": {
        "default": {
            "max_width_choice": constants.MAX_WIDTH_MEDIUM,
            "max_width_custom": 0,
            "alternate_background": False,
            "background_color": "",
        },
        "xprez.TextModule": {
            "max_width_choice": constants.MAX_WIDTH_SMALL,
        },
        "xprez.AccordionModule": {
            "max_width_choice": constants.MAX_WIDTH_SMALL,
        },
    },
    "section_config": {
        "default": {
            "columns": 1,
            "margin_bottom_choice": constants.MARGIN_MEDIUM,
            "margin_bottom_custom": 0,
            "padding_left_choice": constants.PADDING_SMALL,
            "padding_left_custom": 0,
            "padding_right_choice": constants.PADDING_SMALL,
            "padding_right_custom": 0,
            "padding_top_choice": constants.PADDING_NONE,
            "padding_top_custom": 0,
            "padding_bottom_choice": constants.PADDING_NONE,
            "padding_bottom_custom": 0,
            "gap_choice": constants.GAP_MEDIUM,
            "gap_custom": 0,
            "vertical_align_grid": constants.VERTICAL_ALIGN_GRID_STRETCH,
            "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_START,
        }
    },
    "section_shortcuts": {
        "columns": {
            "label": "Columns",
            "choices": (
                {
                    "value": 1,
                    "label": "1",
                    "config": {"columns": {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1}},
                },
                {
                    "value": 2,
                    "label": "2",
                    "config": {"columns": {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1}},
                },
                {
                    "value": 3,
                    "label": "3",
                    "config": {"columns": {0: 3, 1: 3, 2: 3, 3: 3, 4: 2, 5: 1}},
                },
                {
                    "value": 4,
                    "label": "4",
                    "config": {"columns": {0: 4, 1: 4, 2: 3, 3: 3, 4: 2, 5: 1}},
                },
                {
                    "value": 5,
                    "label": "5",
                    "config": {"columns": {0: 5, 1: 5, 2: 4, 3: 3, 4: 2, 5: 2}},
                },
                {
                    "value": 6,
                    "label": "6",
                    "config": {"columns": {0: 6, 1: 6, 2: 4, 3: 3, 4: 3, 5: 2}},
                },
                {
                    "value": 7,
                    "label": "7",
                    "config": {"columns": {0: 7, 1: 7, 2: 5, 3: 4, 4: 3, 5: 2}},
                },
                {
                    "value": 8,
                    "label": "8",
                    "config": {"columns": {0: 8, 1: 8, 2: 6, 3: 4, 4: 3, 5: 2}},
                },
            ),
        },
        "gap": {
            "label": "Gap",
            "choices": (
                {
                    "value": constants.GAP_NONE,
                    "label": "None",
                    "config": {
                        "gap_choice": {
                            0: constants.GAP_NONE,
                            1: constants.GAP_NONE,
                            2: constants.GAP_NONE,
                            3: constants.GAP_NONE,
                            4: constants.GAP_NONE,
                            5: constants.GAP_NONE,
                        },
                    },
                },
                {
                    "value": constants.GAP_SMALL,
                    "label": "Small",
                    "config": {
                        "gap_choice": {
                            0: constants.GAP_SMALL,
                            1: constants.GAP_SMALL,
                            2: constants.GAP_SMALL,
                            3: constants.GAP_SMALL,
                            4: constants.GAP_SMALL,
                            5: constants.GAP_SMALL,
                        },
                    },
                },
                {
                    "value": constants.GAP_MEDIUM,
                    "label": "Medium",
                    "config": {
                        "gap_choice": {
                            0: constants.GAP_MEDIUM,
                            1: constants.GAP_MEDIUM,
                            2: constants.GAP_MEDIUM,
                            3: constants.GAP_MEDIUM,
                            4: constants.GAP_MEDIUM,
                            5: constants.GAP_MEDIUM,
                        },
                    },
                },
                {
                    "value": constants.GAP_LARGE,
                    "label": "Large",
                    "config": {
                        "gap_choice": {
                            0: constants.GAP_LARGE,
                            1: constants.GAP_LARGE,
                            2: constants.GAP_LARGE,
                            3: constants.GAP_LARGE,
                            4: constants.GAP_LARGE,
                            5: constants.GAP_LARGE,
                        },
                    },
                },
            ),
        },
        "max_width": {
            "label": "Max width",
            "clone": "max_width_choice",
        },
    },
    "module": {
        "default": {
            "alternate_color": False,
        },
        "xprez.TextModule": {
            "font_size": constants.FONT_SIZE_NORMAL,
        },
        "xprez.GalleryModule": {
            "crop": constants.CROP_NONE,
            "font_size": constants.FONT_SIZE_NORMAL,
            "lightbox": True,
        },
        "xprez.FilesModule": {
            "font_size": constants.FONT_SIZE_NORMAL,
        },
        "xprez.QuoteModule": {
            "font_size": constants.FONT_SIZE_NORMAL,
        },
        "xprez.NumbersModule": {
            "font_size": constants.FONT_SIZE_NORMAL,
        },
        "xprez.CodeTemplateModule": {
            "font_size": constants.FONT_SIZE_NORMAL,
        },
    },
    "module_config": {
        "default": {
            "colspan": 1,
            "rowspan": 1,
            "vertical_align_grid": constants.VERTICAL_ALIGN_GRID_UNSET,
            "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_UNSET,
            "vertical_align_flex": constants.VERTICAL_ALIGN_FLEX_START,
            "horizontal_align_flex": constants.HORIZONTAL_ALIGN_FLEX_CENTER,
            "border_radius_choice": constants.BORDER_RADIUS_NONE,
            "border_radius_custom": 0,
            "background": False,
            "background_color": "",
            "border": False,
            "padding_left_choice": constants.PADDING_NONE,
            "padding_left_custom": 0,
            "padding_right_choice": constants.PADDING_NONE,
            "padding_right_custom": 0,
            "padding_top_choice": constants.PADDING_NONE,
            "padding_top_custom": 0,
            "padding_bottom_choice": constants.PADDING_NONE,
            "padding_bottom_custom": 0,
            "aspect_ratio": "",
        },
        "xprez.TextModule": {
            "text_align": constants.TEXT_ALIGN_LEFT,
            "media_role": constants.MEDIA_ROLE_LEAD,
            "media_background_position": constants.BACKGROUND_POSITION_CENTER,
            "media_lead_to_edge": True,
            "media_icon_max_size": 100,
            "media_crop": constants.CROP_NONE,
            "media_border_radius_choice": constants.BORDER_RADIUS_NONE,
            "media_border_radius_custom": 0,
        },
        "xprez.GalleryModule": {
            "vertical_align_grid": constants.VERTICAL_ALIGN_GRID_CENTER,
            "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_STRETCH,
            "columns": 1,
            "gap_choice": constants.GAP_SMALL,
        },
        "xprez.NumbersModule": {
            "gap_choice": constants.GAP_MEDIUM,
            "gap_custom": 0,
            "columns": constants.COLUMNS_AUTO,
        },
    },
    "module_shortcuts": {
        "default": {},
        "xprez.GalleryModule": {
            "columns": {
                "label": "Columns",
                "choices": (
                    {
                        "value": 1,
                        "label": "1",
                        "config": {"columns": {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1}},
                    },
                    {
                        "value": 2,
                        "label": "2",
                        "config": {"columns": {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1}},
                    },
                    {
                        "value": 3,
                        "label": "3",
                        "config": {"columns": {0: 3, 1: 3, 2: 3, 3: 3, 4: 2, 5: 1}},
                    },
                    {
                        "value": 4,
                        "label": "4",
                        "config": {"columns": {0: 4, 1: 4, 2: 3, 3: 3, 4: 2, 5: 1}},
                    },
                    {
                        "value": 5,
                        "label": "5",
                        "config": {"columns": {0: 5, 1: 5, 2: 4, 3: 3, 4: 2, 5: 2}},
                    },
                    {
                        "value": 6,
                        "label": "6",
                        "config": {"columns": {0: 6, 1: 6, 2: 4, 3: 3, 4: 3, 5: 2}},
                    },
                    {
                        "value": 7,
                        "label": "7",
                        "config": {"columns": {0: 7, 1: 7, 2: 5, 3: 4, 4: 3, 5: 2}},
                    },
                    {
                        "value": 8,
                        "label": "8",
                        "config": {"columns": {0: 8, 1: 8, 2: 6, 3: 4, 4: 3, 5: 2}},
                    },
                ),
            },
            "gap": {
                "label": "Gap",
                "choices": (
                    {
                        "value": constants.GAP_NONE,
                        "label": "None",
                        "config": {
                            "gap_choice": {
                                0: constants.GAP_NONE,
                                1: constants.GAP_NONE,
                                2: constants.GAP_NONE,
                                3: constants.GAP_NONE,
                                4: constants.GAP_NONE,
                                5: constants.GAP_NONE,
                            },
                        },
                    },
                    {
                        "value": constants.GAP_SMALL,
                        "label": "Small",
                        "config": {
                            "gap_choice": {
                                0: constants.GAP_SMALL,
                                1: constants.GAP_SMALL,
                                2: constants.GAP_SMALL,
                                3: constants.GAP_SMALL,
                                4: constants.GAP_SMALL,
                                5: constants.GAP_SMALL,
                            },
                        },
                    },
                    {
                        "value": constants.GAP_MEDIUM,
                        "label": "Medium",
                        "config": {
                            "gap_choice": {
                                0: constants.GAP_MEDIUM,
                                1: constants.GAP_MEDIUM,
                                2: constants.GAP_MEDIUM,
                                3: constants.GAP_MEDIUM,
                                4: constants.GAP_MEDIUM,
                                5: constants.GAP_MEDIUM,
                            },
                        },
                    },
                    {
                        "value": constants.GAP_LARGE,
                        "label": "Large",
                        "config": {
                            "gap_choice": {
                                0: constants.GAP_LARGE,
                                1: constants.GAP_LARGE,
                                2: constants.GAP_LARGE,
                                3: constants.GAP_LARGE,
                                4: constants.GAP_LARGE,
                                5: constants.GAP_LARGE,
                            },
                        },
                    },
                ),
            },
        },
    },
}

XPREZ_CSS = {
    "section": {
        "max_width": {
            "units": {
                constants.MAX_WIDTH_SMALL: "px",
                constants.MAX_WIDTH_MEDIUM: "px",
                constants.MAX_WIDTH_FULL: "%",
                constants.MAX_WIDTH_CUSTOM: "px",
            },
            "values": {
                constants.MAX_WIDTH_SMALL: {0: 720},
                constants.MAX_WIDTH_MEDIUM: {0: 1296},
                constants.MAX_WIDTH_FULL: {0: 100},
            },
        },
    },
    "section_config": {
        "margin_bottom": {
            "units": {
                constants.MARGIN_NONE: "",
                constants.MARGIN_SMALL: "rem",
                constants.MARGIN_MEDIUM: "rem",
                constants.MARGIN_LARGE: "rem",
                constants.MARGIN_EXTRA_LARGE: "rem",
                constants.MARGIN_CUSTOM: "px",
            },
            "values": {
                constants.MARGIN_NONE: {0: 0},
                constants.MARGIN_SMALL: {0: 2, 2: 1.5, 4: 1},
                constants.MARGIN_MEDIUM: {0: 5, 2: 3, 4: 2},
                constants.MARGIN_LARGE: {0: 8, 2: 4.5, 4: 3},
                constants.MARGIN_EXTRA_LARGE: {0: 11, 2: 6, 4: 4},
            },
        },
        "padding_left": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_EXTRA_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 2, 4: 1},
                constants.PADDING_MEDIUM: {0: 4, 4: 2},
                constants.PADDING_LARGE: {0: 8, 4: 4},
                constants.PADDING_EXTRA_LARGE: {0: 11, 2: 6, 4: 4},
            },
        },
        "padding_right": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_EXTRA_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 2, 4: 1},
                constants.PADDING_MEDIUM: {0: 4, 4: 2},
                constants.PADDING_LARGE: {0: 8, 4: 4},
                constants.PADDING_EXTRA_LARGE: {0: 11, 2: 6, 4: 4},
            },
        },
        "padding_top": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_EXTRA_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 2, 2: 1.5, 4: 1},
                constants.PADDING_MEDIUM: {0: 5, 2: 3, 4: 2},
                constants.PADDING_LARGE: {0: 8, 2: 4.5, 4: 3},
                constants.PADDING_EXTRA_LARGE: {0: 11, 2: 6, 4: 4},
            },
        },
        "padding_bottom": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_EXTRA_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 2, 2: 1.5, 4: 1},
                constants.PADDING_MEDIUM: {0: 5, 2: 3, 4: 2},
                constants.PADDING_LARGE: {0: 8, 2: 4.5, 4: 3},
                constants.PADDING_EXTRA_LARGE: {0: 11, 2: 6, 4: 4},
            },
        },
        "gap": {
            "units": {
                constants.GAP_SMALL: "px",
                constants.GAP_MEDIUM: "px",
                constants.GAP_LARGE: "px",
                constants.GAP_CUSTOM: "px",
            },
            "values": {
                constants.GAP_SMALL: {0: 20, 3: 15, 5: 10},
                constants.GAP_MEDIUM: {0: 40, 3: 30, 5: 20},
                constants.GAP_LARGE: {0: 80, 3: 60, 5: 40},
            },
        },
    },
    "module": {
        "default": {},
    },
    "module_config": {
        "default": {
            "padding_left": {
                "units": {
                    constants.PADDING_NONE: "",
                    constants.PADDING_SMALL: "rem",
                    constants.PADDING_MEDIUM: "rem",
                    constants.PADDING_LARGE: "rem",
                    constants.PADDING_EXTRA_LARGE: "rem",
                    constants.PADDING_CUSTOM: "px",
                },
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 1, 4: 0.5},
                    constants.PADDING_MEDIUM: {0: 2, 4: 1},
                    constants.PADDING_LARGE: {0: 4, 4: 2},
                    constants.PADDING_EXTRA_LARGE: {0: 8, 2: 5, 4: 3},
                },
            },
            "padding_right": {
                "units": {
                    constants.PADDING_NONE: "",
                    constants.PADDING_SMALL: "rem",
                    constants.PADDING_MEDIUM: "rem",
                    constants.PADDING_LARGE: "rem",
                    constants.PADDING_EXTRA_LARGE: "rem",
                    constants.PADDING_CUSTOM: "px",
                },
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 1, 4: 0.5},
                    constants.PADDING_MEDIUM: {0: 2, 4: 1},
                    constants.PADDING_LARGE: {0: 4, 4: 2},
                    constants.PADDING_EXTRA_LARGE: {0: 8, 2: 5, 4: 3},
                },
            },
            "padding_top": {
                "units": {
                    constants.PADDING_NONE: "",
                    constants.PADDING_SMALL: "rem",
                    constants.PADDING_MEDIUM: "rem",
                    constants.PADDING_LARGE: "rem",
                    constants.PADDING_EXTRA_LARGE: "rem",
                    constants.PADDING_CUSTOM: "px",
                },
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 1, 4: 0.5},
                    constants.PADDING_MEDIUM: {0: 2, 4: 1},
                    constants.PADDING_LARGE: {0: 4, 4: 2},
                    constants.PADDING_EXTRA_LARGE: {0: 8, 2: 5, 4: 3},
                },
            },
            "padding_bottom": {
                "units": {
                    constants.PADDING_NONE: "",
                    constants.PADDING_SMALL: "rem",
                    constants.PADDING_MEDIUM: "rem",
                    constants.PADDING_LARGE: "rem",
                    constants.PADDING_EXTRA_LARGE: "rem",
                    constants.PADDING_CUSTOM: "px",
                },
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 1, 4: 0.5},
                    constants.PADDING_MEDIUM: {0: 2, 4: 1},
                    constants.PADDING_LARGE: {0: 4, 4: 2},
                    constants.PADDING_EXTRA_LARGE: {0: 8, 2: 5, 4: 3},
                },
            },
            "border_radius": {
                "units": {
                    constants.BORDER_RADIUS_NONE: "",
                    constants.BORDER_RADIUS_SMALL: "px",
                    constants.BORDER_RADIUS_MEDIUM: "px",
                    constants.BORDER_RADIUS_LARGE: "px",
                    constants.BORDER_RADIUS_CUSTOM: "px",
                },
                "values": {
                    constants.BORDER_RADIUS_NONE: {0: 0},
                    constants.BORDER_RADIUS_SMALL: {0: 6},
                    constants.BORDER_RADIUS_MEDIUM: {0: 16},
                    constants.BORDER_RADIUS_LARGE: {0: 32},
                },
            },
        },
        "xprez.TextModule": {
            "media_icon_max_size": {"units": "px"},
            "media_border_radius": {
                "units": {
                    constants.BORDER_RADIUS_NONE: "",
                    constants.BORDER_RADIUS_SMALL: "px",
                    constants.BORDER_RADIUS_MEDIUM: "px",
                    constants.BORDER_RADIUS_LARGE: "px",
                    constants.BORDER_RADIUS_CUSTOM: "px",
                },
                "values": {
                    constants.BORDER_RADIUS_NONE: {0: 0},
                    constants.BORDER_RADIUS_SMALL: {0: 6},
                    constants.BORDER_RADIUS_MEDIUM: {0: 16},
                    constants.BORDER_RADIUS_LARGE: {0: 32},
                },
            },
            "font_size": {
                "values": {
                    constants.FONT_SIZE_SMALLEST: {0: 14, 3: 12},
                    constants.FONT_SIZE_SMALL: {0: 16, 3: 14},
                    constants.FONT_SIZE_NORMAL: {0: 18, 3: 16},
                    constants.FONT_SIZE_LARGE: {0: 24, 3: 20},
                    constants.FONT_SIZE_LARGEST: {0: 32, 3: 28},
                },
            },
        },
        "xprez.GalleryModule": {
            "gap": {
                "units": {
                    constants.GAP_NONE: "px",
                    constants.GAP_SMALL: "px",
                    constants.GAP_MEDIUM: "px",
                    constants.GAP_LARGE: "px",
                    constants.GAP_CUSTOM: "px",
                },
                "values": {
                    constants.GAP_NONE: {0: 0},
                    constants.GAP_SMALL: {0: 20, 3: 15, 5: 10},
                    constants.GAP_MEDIUM: {0: 40, 3: 30, 5: 20},
                    constants.GAP_LARGE: {0: 80, 3: 60, 5: 40},
                },
            },
        },
        "xprez.NumbersModule": {
            "gap": {
                "units": {
                    constants.GAP_NONE: "px",
                    constants.GAP_SMALL: "px",
                    constants.GAP_MEDIUM: "px",
                    constants.GAP_LARGE: "px",
                    constants.GAP_CUSTOM: "px",
                },
                "values": {
                    constants.GAP_NONE: {0: 0},
                    constants.GAP_SMALL: {0: 20, 3: 15, 5: 10},
                    constants.GAP_MEDIUM: {0: 40, 3: 30, 5: 20},
                    constants.GAP_LARGE: {0: 80, 3: 60, 5: 40},
                },
            },
        },
    },
}
