from xprez import constants

XPREZ_SECTION_MODEL_CLASS = "xprez.Section"
XPREZ_CONTAINER_MODEL_CLASS = "xprez.Container"
XPREZ_CK_EDITOR_MODULE_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_GRID_BOXES_MODULE_WIDGET = "xprez.ck_editor.widgets.CkEditorWidgetFull"
XPREZ_TEXT_IMAGE_MODULE_WIDGET = (
    "xprez.ck_editor.widgets.CkEditorWidgetFullNoInsertPlugin"
)
XPREZ_CK_EDITOR_FILE_UPLOAD_VIEW_NAME = "admin:textmodule_file_upload"

XPREZ_MODULES_AUTOREGISTER = True
XPREZ_MODULES_AUTOREGISTER_BUILTINS = [
    "xprez.TextModule",
    "xprez.QuoteModule",
    "xprez.GalleryModule",
    "xprez.FilesModule",
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

XPREZ_DEFAULTS = {
    "section": {
        "max_width_choice": constants.MAX_WIDTH_MEDIUM,
        "max_width_custom": 0,
    },
    "section_config": {
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
        "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_STRETCH,
    },
    "module": {
        "default": {},
    },
    "module_config": {
        "default": {
            "colspan": 1,
            "rowspan": 1,
            "vertical_align_grid": constants.VERTICAL_ALIGN_GRID_UNSET,
            "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_UNSET,
            "vertical_align_flex": constants.VERTICAL_ALIGN_FLEX_START,
            "horizontal_align_flex": constants.HORIZONTAL_ALIGN_FLEX_CENTER,
            "border_radius_choice": constants.BORDER_RADIUS_MEDIUM,
        },
        "xprez.TextModule": {
            # "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_STRETCH,  # TODO: different just for testing
        },
        "xprez.GalleryModule": {
            "colspan": 1,
            "rowspan": 1,
            "vertical_align_grid": constants.VERTICAL_ALIGN_GRID_CENTER,
            "horizontal_align_grid": constants.HORIZONTAL_ALIGN_GRID_CENTER,
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
                constants.MARGIN_CUSTOM: "px",
            },
            "values": {
                constants.MARGIN_NONE: {0: 0},
                constants.MARGIN_SMALL: {0: 1, 1: 1.5, 3: 2},
                constants.MARGIN_MEDIUM: {0: 2, 1: 3, 3: 5},
                constants.MARGIN_LARGE: {0: 4, 1: 6, 3: 10},
            },
        },
        "padding_left": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 1, 1: 2},
                constants.PADDING_MEDIUM: {0: 2, 1: 4},
                constants.PADDING_LARGE: {0: 4, 1: 8},
            },
        },
        "padding_right": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 1, 1: 2},
                constants.PADDING_MEDIUM: {0: 2, 1: 4},
                constants.PADDING_LARGE: {0: 4, 1: 8},
            },
        },
        "padding_top": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 1, 1: 1.5, 3: 2},
                constants.PADDING_MEDIUM: {0: 2, 1: 3, 3: 5},
                constants.PADDING_LARGE: {0: 4, 1: 6, 3: 10},
            },
        },
        "padding_bottom": {
            "units": {
                constants.PADDING_NONE: "",
                constants.PADDING_SMALL: "rem",
                constants.PADDING_MEDIUM: "rem",
                constants.PADDING_LARGE: "rem",
                constants.PADDING_CUSTOM: "px",
            },
            "values": {
                constants.PADDING_NONE: {0: 0},
                constants.PADDING_SMALL: {0: 1, 1: 1.5, 3: 2},
                constants.PADDING_MEDIUM: {0: 2, 1: 3, 3: 5},
                constants.PADDING_LARGE: {0: 4, 1: 6, 3: 10},
            },
        },
        "gap": {
            "units": "px",
            "values": {
                constants.GAP_SMALL: {0: 10, 1: 15, 2: 20},
                constants.GAP_MEDIUM: {0: 20, 1: 30, 2: 40},
                constants.GAP_LARGE: {0: 40, 1: 60, 2: 80},
            },
        },
    },
    "module": {
        "default": {},
    },
    "module_config": {
        "default": {
            "padding_left": {
                "units": "px",
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.PADDING_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.PADDING_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
            "padding_right": {
                "units": "px",
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.PADDING_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.PADDING_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
            "padding_top": {
                "units": "px",
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.PADDING_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.PADDING_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
            "padding_bottom": {
                "units": "px",
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.PADDING_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.PADDING_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
            "border_radius": {
                "units": "px",
                "values": {
                    constants.BORDER_RADIUS_NONE: {0: 0},
                    constants.BORDER_RADIUS_SMALL: {0: 4},
                    constants.BORDER_RADIUS_MEDIUM: {0: 8},
                    constants.BORDER_RADIUS_LARGE: {0: 16},
                },
            },
        },
        "xprez.TextModule": {
            "font_size": {
                "units": "px",
                "values": {
                    constants.FONT_SIZE_SMALLEST: {0: 12, 2: 14},
                    constants.FONT_SIZE_SMALL: {0: 14, 2: 16},
                    constants.FONT_SIZE_NORMAL: {0: 16, 2: 18},
                    constants.FONT_SIZE_LARGE: {0: 20, 2: 24},
                    constants.FONT_SIZE_LARGEST: {0: 28, 2: 32},
                },
            },
        },
        "xprez.GalleryModule": {
            "gap": {
                "units": "px",
                "values": {
                    constants.GAP_NONE: {0: 0},
                    constants.GAP_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.GAP_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.GAP_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
            "padding_horizontal": {
                "units": "px",
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.PADDING_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.PADDING_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
            "padding_vertical": {
                "units": "px",
                "values": {
                    constants.PADDING_NONE: {0: 0},
                    constants.PADDING_SMALL: {0: 10, 1: 15, 2: 20},
                    constants.PADDING_MEDIUM: {0: 20, 1: 30, 2: 40},
                    constants.PADDING_LARGE: {0: 40, 1: 60, 2: 80},
                },
            },
        },
    },
}
