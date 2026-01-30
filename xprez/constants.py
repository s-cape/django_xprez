CUSTOM = "custom"
NONE = ""

MARGIN_NONE = NONE
MARGIN_SMALL = "small"
MARGIN_MEDIUM = "medium"
MARGIN_LARGE = "large"
MARGIN_CUSTOM = CUSTOM
MARGIN_CHOICES = (
    (MARGIN_NONE, "None"),
    (MARGIN_SMALL, "Small"),
    (MARGIN_MEDIUM, "Medium"),
    (MARGIN_LARGE, "Large"),
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

# Vertical align - Grid (CSS Grid values for grid positioning)
VERTICAL_ALIGN_GRID_START = "start"
VERTICAL_ALIGN_GRID_CENTER = "center"
VERTICAL_ALIGN_GRID_END = "end"
VERTICAL_ALIGN_GRID_STRETCH = "stretch"
VERTICAL_ALIGN_GRID_BASELINE = "baseline"
VERTICAL_ALIGN_GRID_UNSET = "initial"

# SectionConfig vertical grid alignment (no unset)
VERTICAL_ALIGN_GRID_SECTION_CHOICES = (
    (VERTICAL_ALIGN_GRID_START, "Start"),
    (VERTICAL_ALIGN_GRID_CENTER, "Center"),
    (VERTICAL_ALIGN_GRID_END, "End"),
    (VERTICAL_ALIGN_GRID_STRETCH, "Stretch"),
    (VERTICAL_ALIGN_GRID_BASELINE, "Baseline"),
)

# ModuleConfig vertical grid alignment (includes unset)
VERTICAL_ALIGN_GRID_MODULE_CHOICES = (
    (VERTICAL_ALIGN_GRID_START, "Start"),
    (VERTICAL_ALIGN_GRID_CENTER, "Center"),
    (VERTICAL_ALIGN_GRID_END, "End"),
    (VERTICAL_ALIGN_GRID_STRETCH, "Stretch"),
    (VERTICAL_ALIGN_GRID_BASELINE, "Baseline"),
    (VERTICAL_ALIGN_GRID_UNSET, "Unset"),
)

# Horizontal align - Grid (CSS Grid values for grid positioning)
HORIZONTAL_ALIGN_GRID_START = "start"
HORIZONTAL_ALIGN_GRID_CENTER = "center"
HORIZONTAL_ALIGN_GRID_END = "end"
HORIZONTAL_ALIGN_GRID_STRETCH = "stretch"
HORIZONTAL_ALIGN_GRID_UNSET = "initial"

# SectionConfig horizontal grid alignment (no unset)
HORIZONTAL_ALIGN_GRID_SECTION_CHOICES = (
    (HORIZONTAL_ALIGN_GRID_START, "Start"),
    (HORIZONTAL_ALIGN_GRID_CENTER, "Center"),
    (HORIZONTAL_ALIGN_GRID_END, "End"),
    (HORIZONTAL_ALIGN_GRID_STRETCH, "Stretch"),
)

# ModuleConfig horizontal grid alignment (includes unset)
HORIZONTAL_ALIGN_GRID_MODULE_CHOICES = (
    (HORIZONTAL_ALIGN_GRID_START, "Start"),
    (HORIZONTAL_ALIGN_GRID_CENTER, "Center"),
    (HORIZONTAL_ALIGN_GRID_END, "End"),
    (HORIZONTAL_ALIGN_GRID_STRETCH, "Stretch"),
    (HORIZONTAL_ALIGN_GRID_UNSET, "Unset"),
)

# Vertical align - Flex (Flexbox values for content alignment inside modules)
VERTICAL_ALIGN_FLEX_START = "flex-start"
VERTICAL_ALIGN_FLEX_CENTER = "center"
VERTICAL_ALIGN_FLEX_END = "flex-end"
VERTICAL_ALIGN_FLEX_STRETCH = "stretch"
VERTICAL_ALIGN_FLEX_BASELINE = "baseline"

VERTICAL_ALIGN_FLEX_CHOICES = (
    (VERTICAL_ALIGN_FLEX_START, "Flex Start"),
    (VERTICAL_ALIGN_FLEX_CENTER, "Center"),
    (VERTICAL_ALIGN_FLEX_END, "Flex End"),
    (VERTICAL_ALIGN_FLEX_STRETCH, "Stretch"),
    (VERTICAL_ALIGN_FLEX_BASELINE, "Baseline"),
)

# Horizontal align - Flex (Flexbox values for content alignment inside modules)
HORIZONTAL_ALIGN_FLEX_START = "flex-start"
HORIZONTAL_ALIGN_FLEX_CENTER = "center"
HORIZONTAL_ALIGN_FLEX_END = "flex-end"

HORIZONTAL_ALIGN_FLEX_CHOICES = (
    (HORIZONTAL_ALIGN_FLEX_START, "Flex Start"),
    (HORIZONTAL_ALIGN_FLEX_CENTER, "Center"),
    (HORIZONTAL_ALIGN_FLEX_END, "Flex End"),
)

# Legacy - kept for backward compatibility
VERTICAL_ALIGN_CHOICES = VERTICAL_ALIGN_GRID_SECTION_CHOICES
HORIZONTAL_ALIGN_CHOICES = HORIZONTAL_ALIGN_GRID_SECTION_CHOICES

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

# Font size
FONT_SIZE_SMALLEST = "smallest"
FONT_SIZE_SMALL = "small"
FONT_SIZE_NORMAL = "normal"
FONT_SIZE_LARGE = "large"
FONT_SIZE_LARGEST = "largest"
FONT_SIZE_CHOICES = (
    (FONT_SIZE_SMALLEST, "Smallest"),
    (FONT_SIZE_SMALL, "Small"),
    (FONT_SIZE_NORMAL, "Normal"),
    (FONT_SIZE_LARGE, "Large"),
    (FONT_SIZE_LARGEST, "Largest"),
)

# Text align
TEXT_ALIGN_LEFT = "left"
TEXT_ALIGN_CENTER = "center"
TEXT_ALIGN_RIGHT = "right"
TEXT_ALIGN_CHOICES = (
    (TEXT_ALIGN_LEFT, "Left"),
    (TEXT_ALIGN_CENTER, "Center"),
    (TEXT_ALIGN_RIGHT, "Right"),
)

# Media role
MEDIA_ROLE_BACKGROUND = "background"
MEDIA_ROLE_LEAD = "lead"
MEDIA_ROLE_ICON = "icon"
MEDIA_ROLE_CHOICES = (
    (MEDIA_ROLE_BACKGROUND, "Background"),
    (MEDIA_ROLE_LEAD, "Lead"),
    (MEDIA_ROLE_ICON, "Icon"),
)

# Background position
BACKGROUND_POSITION_TOP = "top"
BACKGROUND_POSITION_CENTER = "center"
BACKGROUND_POSITION_BOTTOM = "bottom"
BACKGROUND_POSITION_CHOICES = (
    (BACKGROUND_POSITION_TOP, "Top"),
    (BACKGROUND_POSITION_CENTER, "Center"),
    (BACKGROUND_POSITION_BOTTOM, "Bottom"),
)

# Border radius
BORDER_RADIUS_NONE = NONE
BORDER_RADIUS_SMALL = "small"
BORDER_RADIUS_MEDIUM = "medium"
BORDER_RADIUS_LARGE = "large"
BORDER_RADIUS_CUSTOM = CUSTOM
BORDER_RADIUS_CHOICES = (
    (BORDER_RADIUS_NONE, "None"),
    (BORDER_RADIUS_SMALL, "Small"),
    (BORDER_RADIUS_MEDIUM, "Medium"),
    (BORDER_RADIUS_LARGE, "Large"),
    (BORDER_RADIUS_CUSTOM, "Custom"),
)
