CUSTOM = "custom"
NONE = ""

MARGIN_SMALL = "small"
MARGIN_MEDIUM = "medium"
MARGIN_FULL = "full"
MARGIN_CUSTOM = CUSTOM
MARGIN_CHOICES = (
    (MARGIN_SMALL, "Small"),
    (MARGIN_MEDIUM, "Medium"),
    (MARGIN_FULL, "Full"),
    (MARGIN_CUSTOM, "Custom"),
)

MAX_WIDTH_SMALL = "small"
MAX_WIDTH_MEDIUM = "medium"
MAX_WIDTH_FULL = "full"
MAX_WIDTH_CUSTOM = CUSTOM
MAX_WIDTH_CHOICES = (
    (MAX_WIDTH_SMALL, "Small"),
    (MAX_WIDTH_MEDIUM, "Medium"),
    (MAX_WIDTH_FULL, "Full"),
    (MAX_WIDTH_CUSTOM, "Custom"),
)

PADDING_NONE = NONE
PADDING_SMALL = "small"
PADDING_MEDIUM = "medium"
PADDING_LARGE = "large"
PADDING_CUSTOM = CUSTOM
PADDING_CHOICES = (
    (PADDING_NONE, "None"),
    (PADDING_SMALL, "Small"),
    (PADDING_MEDIUM, "Medium"),
    (PADDING_LARGE, "Large"),
    (PADDING_CUSTOM, "Custom"),
)

# Gap
GAP_NONE = NONE
GAP_SMALL = "small"
GAP_MEDIUM = "medium"
GAP_LARGE = "large"
GAP_CUSTOM = CUSTOM
GAP_CHOICES = (
    (GAP_NONE, "None"),
    (GAP_SMALL, "Small"),
    (GAP_MEDIUM, "Medium"),
    (GAP_LARGE, "Large"),
    (GAP_CUSTOM, "Custom"),
)

# Vertical align
VERTICAL_ALIGN_TOP = "top"
VERTICAL_ALIGN_MIDDLE = "middle"
VERTICAL_ALIGN_BOTTOM = "bottom"
VERTICAL_ALIGN_STRETCH = "stretch"
VERTICAL_ALIGN_CHOICES = (
    (VERTICAL_ALIGN_TOP, "Top"),
    (VERTICAL_ALIGN_MIDDLE, "Middle"),
    (VERTICAL_ALIGN_BOTTOM, "Bottom"),
    (VERTICAL_ALIGN_STRETCH, "Stretch"),
)

# Horizontal align
HORIZONTAL_ALIGN_LEFT = "left"
HORIZONTAL_ALIGN_CENTER = "center"
HORIZONTAL_ALIGN_RIGHT = "right"
HORIZONTAL_ALIGN_STRETCH = "stretch"
HORIZONTAL_ALIGN_CHOICES = (
    (HORIZONTAL_ALIGN_LEFT, "Left"),
    (HORIZONTAL_ALIGN_CENTER, "Center"),
    (HORIZONTAL_ALIGN_RIGHT, "Right"),
    (HORIZONTAL_ALIGN_STRETCH, "Stretch"),
)

CROP_NONE = ""
CROP_1_1 = "1:1"
CROP_3_2 = "3:2"
CROP_4_3 = "4:3"
CROP_16_9 = "16:9"
CROP_CHOICES = (
    (CROP_NONE, "None"),
    (CROP_1_1, "1:1"),
    (CROP_3_2, "3:2"),
    (CROP_4_3, "4:3"),
    (CROP_16_9, "16:9"),
)
