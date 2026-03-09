from django.utils.translation import gettext_lazy as _

CUSTOM = "custom"

MODULE_KEY = "module"
SECTION_KEY = "section"
CONTAINER_KEY = "container"

MARGIN_NONE = ""
MARGIN_SMALL = "small"
MARGIN_MEDIUM = "medium"
MARGIN_LARGE = "large"
MARGIN_CUSTOM = CUSTOM
MARGIN_CHOICES = (
    (MARGIN_NONE, _("None")),
    (MARGIN_SMALL, _("Small")),
    (MARGIN_MEDIUM, _("Medium")),
    (MARGIN_LARGE, _("Large")),
    (MARGIN_CUSTOM, _("Custom")),
)

MAX_WIDTH_SMALL = "small"
MAX_WIDTH_MEDIUM = "medium"
MAX_WIDTH_FULL = "full"
MAX_WIDTH_CUSTOM = CUSTOM
MAX_WIDTH_CHOICES = (
    (MAX_WIDTH_SMALL, _("Small")),
    (MAX_WIDTH_MEDIUM, _("Medium")),
    (MAX_WIDTH_FULL, _("Full")),
    (MAX_WIDTH_CUSTOM, _("Custom")),
)

PADDING_NONE = ""
PADDING_SMALL = "small"
PADDING_MEDIUM = "medium"
PADDING_LARGE = "large"
PADDING_CUSTOM = CUSTOM
PADDING_CHOICES = (
    (PADDING_NONE, _("None")),
    (PADDING_SMALL, _("Small")),
    (PADDING_MEDIUM, _("Medium")),
    (PADDING_LARGE, _("Large")),
    (PADDING_CUSTOM, _("Custom")),
)

# Gap
GAP_NONE = ""
GAP_SMALL = "small"
GAP_MEDIUM = "medium"
GAP_LARGE = "large"
GAP_CUSTOM = CUSTOM
GAP_CHOICES = (
    (GAP_NONE, _("None")),
    (GAP_SMALL, _("Small")),
    (GAP_MEDIUM, _("Medium")),
    (GAP_LARGE, _("Large")),
    (GAP_CUSTOM, _("Custom")),
)

# Numbers module columns (None = auto)
COLUMNS_AUTO = None

# Vertical align - Grid (CSS Grid values for grid positioning)
VERTICAL_ALIGN_GRID_START = "start"
VERTICAL_ALIGN_GRID_CENTER = "center"
VERTICAL_ALIGN_GRID_END = "end"
VERTICAL_ALIGN_GRID_STRETCH = "stretch"
VERTICAL_ALIGN_GRID_BASELINE = "baseline"
VERTICAL_ALIGN_GRID_UNSET = "initial"

# SectionConfig vertical grid alignment (no unset)
VERTICAL_ALIGN_GRID_SECTION_CHOICES = (
    (VERTICAL_ALIGN_GRID_START, _("Start")),
    (VERTICAL_ALIGN_GRID_CENTER, _("Center")),
    (VERTICAL_ALIGN_GRID_END, _("End")),
    (VERTICAL_ALIGN_GRID_STRETCH, _("Stretch")),
    (VERTICAL_ALIGN_GRID_BASELINE, _("Baseline")),
)

# ModuleConfig vertical grid alignment (includes unset)
VERTICAL_ALIGN_GRID_MODULE_CHOICES = (
    (VERTICAL_ALIGN_GRID_START, _("Start")),
    (VERTICAL_ALIGN_GRID_CENTER, _("Center")),
    (VERTICAL_ALIGN_GRID_END, _("End")),
    (VERTICAL_ALIGN_GRID_STRETCH, _("Stretch")),
    (VERTICAL_ALIGN_GRID_BASELINE, _("Baseline")),
    (VERTICAL_ALIGN_GRID_UNSET, _("Unset")),
)

# Horizontal align - Grid (CSS Grid values for grid positioning)
HORIZONTAL_ALIGN_GRID_START = "start"
HORIZONTAL_ALIGN_GRID_CENTER = "center"
HORIZONTAL_ALIGN_GRID_END = "end"
HORIZONTAL_ALIGN_GRID_STRETCH = "stretch"
HORIZONTAL_ALIGN_GRID_UNSET = "initial"

# SectionConfig horizontal grid alignment (no unset)
HORIZONTAL_ALIGN_GRID_SECTION_CHOICES = (
    (HORIZONTAL_ALIGN_GRID_START, _("Start")),
    (HORIZONTAL_ALIGN_GRID_CENTER, _("Center")),
    (HORIZONTAL_ALIGN_GRID_END, _("End")),
    (HORIZONTAL_ALIGN_GRID_STRETCH, _("Stretch")),
)

# ModuleConfig horizontal grid alignment (includes unset)
HORIZONTAL_ALIGN_GRID_MODULE_CHOICES = (
    (HORIZONTAL_ALIGN_GRID_START, _("Start")),
    (HORIZONTAL_ALIGN_GRID_CENTER, _("Center")),
    (HORIZONTAL_ALIGN_GRID_END, _("End")),
    (HORIZONTAL_ALIGN_GRID_STRETCH, _("Stretch")),
    (HORIZONTAL_ALIGN_GRID_UNSET, _("Unset")),
)

# Vertical align - Flex (Flexbox values for content alignment inside modules)
VERTICAL_ALIGN_FLEX_START = "flex-start"
VERTICAL_ALIGN_FLEX_CENTER = "center"
VERTICAL_ALIGN_FLEX_END = "flex-end"
VERTICAL_ALIGN_FLEX_STRETCH = "stretch"
VERTICAL_ALIGN_FLEX_BASELINE = "baseline"

VERTICAL_ALIGN_FLEX_CHOICES = (
    (VERTICAL_ALIGN_FLEX_START, _("Flex Start")),
    (VERTICAL_ALIGN_FLEX_CENTER, _("Center")),
    (VERTICAL_ALIGN_FLEX_END, _("Flex End")),
    (VERTICAL_ALIGN_FLEX_STRETCH, _("Stretch")),
    (VERTICAL_ALIGN_FLEX_BASELINE, _("Baseline")),
)

# Horizontal align - Flex (Flexbox values for content alignment inside modules)
HORIZONTAL_ALIGN_FLEX_START = "flex-start"
HORIZONTAL_ALIGN_FLEX_CENTER = "center"
HORIZONTAL_ALIGN_FLEX_END = "flex-end"

HORIZONTAL_ALIGN_FLEX_CHOICES = (
    (HORIZONTAL_ALIGN_FLEX_START, _("Flex Start")),
    (HORIZONTAL_ALIGN_FLEX_CENTER, _("Center")),
    (HORIZONTAL_ALIGN_FLEX_END, _("Flex End")),
)

# Legacy - kept for backward compatibility
VERTICAL_ALIGN_CHOICES = VERTICAL_ALIGN_GRID_SECTION_CHOICES
HORIZONTAL_ALIGN_CHOICES = HORIZONTAL_ALIGN_GRID_SECTION_CHOICES

ASPECT_RATIO_1_1 = "1/1"
ASPECT_RATIO_3_2 = "3/2"
ASPECT_RATIO_4_3 = "4/3"
ASPECT_RATIO_16_9 = "16/9"
ASPECT_RATIO_2_3 = "2/3"
ASPECT_RATIO_3_4 = "3/4"
ASPECT_RATIO_9_16 = "9/16"
ASPECT_RATIO_CHOICES = (
    (ASPECT_RATIO_1_1, _("1:1")),
    (ASPECT_RATIO_3_2, _("3:2")),
    (ASPECT_RATIO_4_3, _("4:3")),
    (ASPECT_RATIO_16_9, _("16:9")),
    (ASPECT_RATIO_2_3, _("2:3")),
    (ASPECT_RATIO_3_4, _("3:4")),
    (ASPECT_RATIO_9_16, _("9:16")),
)

CROP_NONE = ""
CROP_CHOICES = ((CROP_NONE, _("None")),) + ASPECT_RATIO_CHOICES

# Font size
FONT_SIZE_UNSET = "unset"
FONT_SIZE_SMALLEST = "smallest"
FONT_SIZE_SMALL = "small"
FONT_SIZE_NORMAL = "normal"
FONT_SIZE_LARGE = "large"
FONT_SIZE_LARGEST = "largest"
FONT_SIZE_CHOICES = (
    (FONT_SIZE_UNSET, _("Unset")),
    (FONT_SIZE_SMALLEST, _("Extra Small")),
    (FONT_SIZE_SMALL, _("Small")),
    (FONT_SIZE_NORMAL, _("Normal")),
    (FONT_SIZE_LARGE, _("Large")),
    (FONT_SIZE_LARGEST, _("Extra Large")),
)

# Text align
TEXT_ALIGN_LEFT = "left"
TEXT_ALIGN_CENTER = "center"
TEXT_ALIGN_RIGHT = "right"
TEXT_ALIGN_CHOICES = (
    (TEXT_ALIGN_LEFT, _("Left")),
    (TEXT_ALIGN_CENTER, _("Center")),
    (TEXT_ALIGN_RIGHT, _("Right")),
)

# Media role
MEDIA_ROLE_BACKGROUND = "background"
MEDIA_ROLE_LEAD = "lead"
MEDIA_ROLE_ICON = "icon"
MEDIA_ROLE_CHOICES = (
    (MEDIA_ROLE_BACKGROUND, _("Background")),
    (MEDIA_ROLE_LEAD, _("Lead")),
    (MEDIA_ROLE_ICON, _("Icon")),
)

# Background position
BACKGROUND_POSITION_TOP = "top"
BACKGROUND_POSITION_CENTER = "center"
BACKGROUND_POSITION_BOTTOM = "bottom"
BACKGROUND_POSITION_CHOICES = (
    (BACKGROUND_POSITION_TOP, _("Top")),
    (BACKGROUND_POSITION_CENTER, _("Center")),
    (BACKGROUND_POSITION_BOTTOM, _("Bottom")),
)

# Border radius
BORDER_RADIUS_NONE = ""
BORDER_RADIUS_SMALL = "small"
BORDER_RADIUS_MEDIUM = "medium"
BORDER_RADIUS_LARGE = "large"
BORDER_RADIUS_CUSTOM = CUSTOM
BORDER_RADIUS_CHOICES = (
    (BORDER_RADIUS_NONE, _("None")),
    (BORDER_RADIUS_SMALL, _("Small")),
    (BORDER_RADIUS_MEDIUM, _("Medium")),
    (BORDER_RADIUS_LARGE, _("Large")),
    (BORDER_RADIUS_CUSTOM, _("Custom")),
)
