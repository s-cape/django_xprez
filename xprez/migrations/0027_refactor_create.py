import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("xprez", "0026_alter_contentsymlink_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Container",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content_type", models.CharField(editable=False, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("visible", models.BooleanField(default=True)),
                ("saved", models.BooleanField(default=False, editable=False)),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("changed", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "max_width_choice",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("full", "Full"),
                            ("custom", "Custom"),
                        ],
                        default="medium",
                        max_length=16,
                        verbose_name="Max width",
                    ),
                ),
                (
                    "max_width_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("alternate_background", models.BooleanField(default=False)),
                ("background_color", models.CharField(blank=True, max_length=30)),
                ("css_class", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "container",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sections",
                        to="xprez.container",
                    ),
                ),
            ],
            options={
                "ordering": ("position",),
            },
        ),
        migrations.CreateModel(
            name="Module",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("saved", models.BooleanField(default=False, editable=False)),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("content_type", models.CharField(editable=False, max_length=100)),
                ("css_class", models.CharField(blank=True, max_length=100, null=True)),
                ("alternate_color", models.BooleanField(default=False)),
                ("background_color", models.CharField(blank=True, max_length=30)),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("changed", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="modules",
                        to="xprez.section",
                    ),
                ),
            ],
            options={
                "ordering": ("position",),
            },
        ),
        migrations.CreateModel(
            name="TextModule",
            fields=[
                (
                    "module_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="xprez.module",
                    ),
                ),
                ("text", models.TextField(blank=True)),
                ("media", models.FileField(upload_to="images", null=True, blank=True)),
                (
                    "url",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Target URL"
                    ),
                ),
            ],
            options={
                "verbose_name": "Text",
            },
            bases=("xprez.module",),
        ),
        migrations.CreateModel(
            name="QuoteModule",
            fields=[
                (
                    "module_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="xprez.module",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("subtitle", models.CharField(blank=True, max_length=255, null=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="quotes")),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("quote", models.TextField()),
            ],
            options={
                "verbose_name": "Quote",
            },
            bases=("xprez.module",),
        ),
        migrations.CreateModel(
            name="SectionSymlink",
            fields=[
                (
                    "module_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="xprez.module",
                    ),
                ),
                (
                    "symlink",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="symlinked_section_set",
                        to="xprez.section",
                    ),
                ),
            ],
            options={
                "verbose_name": "Linked section",
            },
            bases=("xprez.module",),
        ),
        migrations.CreateModel(
            name="SectionConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "css_breakpoint",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Basic style (&gt; 0px)"),
                            (1, "Small devices (&gt; 500px)"),
                            (2, "Tablets (&gt; 768px)"),
                            (3, "Large devices (&gt; 992px)"),
                            (4, "Desktops (&gt; 1200px)"),
                            (5, "Extra large devices (&gt; 1500px)"),
                        ],
                        default=0,
                        editable=False,
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                (
                    "margin_bottom_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="medium",
                        blank=True,
                        max_length=20,
                        verbose_name="Margin bottom",
                    ),
                ),
                (
                    "margin_bottom_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_left_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="small",
                        max_length=20,
                        verbose_name="Padding left",
                    ),
                ),
                (
                    "padding_right_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="small",
                        max_length=20,
                        verbose_name="Padding right",
                    ),
                ),
                (
                    "padding_top_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Padding top",
                    ),
                ),
                (
                    "padding_bottom_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Padding bottom",
                    ),
                ),
                (
                    "padding_left_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_right_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_top_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_bottom_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "columns",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "1"),
                            (2, "2"),
                            (3, "3"),
                            (4, "4"),
                            (5, "5"),
                            (6, "6"),
                            (7, "7"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "gap_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="small",
                        max_length=20,
                        verbose_name="Gap",
                        blank=True,
                    ),
                ),
                ("gap_custom", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "vertical_align_grid",
                    models.CharField(
                        choices=[
                            ("start", "Start"),
                            ("center", "Center"),
                            ("end", "End"),
                            ("stretch", "Stretch"),
                            ("baseline", "Baseline"),
                        ],
                        default="stretch",
                        max_length=20,
                    ),
                ),
                (
                    "horizontal_align_grid",
                    models.CharField(
                        choices=[
                            ("start", "Start"),
                            ("center", "Center"),
                            ("end", "End"),
                            ("stretch", "Stretch"),
                        ],
                        default="stretch",
                        max_length=20,
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="configs",
                        to="xprez.section",
                        editable=False,
                    ),
                ),
            ],
            options={
                "verbose_name": "Section Config",
                "verbose_name_plural": "Section Configs",
                "unique_together": {("section", "css_breakpoint")},
                "ordering": ("css_breakpoint",),
            },
        ),
        migrations.CreateModel(
            name="ModuleConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "css_breakpoint",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Basic style (&gt; 0px)"),
                            (1, "Small devices (&gt; 500px)"),
                            (2, "Tablets (&gt; 768px)"),
                            (3, "Large devices (&gt; 992px)"),
                            (4, "Desktops (&gt; 1200px)"),
                            (5, "Extra large devices (&gt; 1500px)"),
                        ],
                        default=0,
                        editable=False,
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="configs",
                        to="xprez.module",
                        editable=False,
                    ),
                ),
                (
                    "colspan",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Column span"
                    ),
                ),
                (
                    "rowspan",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Row span"
                    ),
                ),
                (
                    "vertical_align_grid",
                    models.CharField(
                        choices=[
                            ("start", "Start"),
                            ("center", "Center"),
                            ("end", "End"),
                            ("stretch", "Stretch"),
                            ("baseline", "Baseline"),
                            ("unset", "Unset"),
                        ],
                        default="unset",
                        max_length=20,
                        verbose_name="Vertical align (grid)",
                    ),
                ),
                (
                    "horizontal_align_grid",
                    models.CharField(
                        choices=[
                            ("start", "Start"),
                            ("center", "Center"),
                            ("end", "End"),
                            ("stretch", "Stretch"),
                            ("unset", "Unset"),
                        ],
                        default="unset",
                        max_length=20,
                        verbose_name="Horizontal align (grid)",
                    ),
                ),
                (
                    "vertical_align_flex",
                    models.CharField(
                        choices=[
                            ("flex-start", "Flex Start"),
                            ("center", "Center"),
                            ("flex-end", "Flex End"),
                            ("stretch", "Stretch"),
                            ("baseline", "Baseline"),
                        ],
                        default="flex-start",
                        max_length=20,
                        verbose_name="Vertical align (flex)",
                    ),
                ),
                (
                    "horizontal_align_flex",
                    models.CharField(
                        choices=[
                            ("flex-start", "Flex Start"),
                            ("center", "Center"),
                            ("flex-end", "Flex End"),
                        ],
                        default="center",
                        max_length=20,
                        verbose_name="Horizontal align (flex)",
                    ),
                ),
                ("background", models.BooleanField(default=False)),
                ("border", models.BooleanField(default=False)),
                (
                    "padding_left_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Padding left",
                    ),
                ),
                (
                    "padding_left_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_right_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Padding right",
                    ),
                ),
                (
                    "padding_right_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_top_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Padding top",
                    ),
                ),
                (
                    "padding_top_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_bottom_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Padding bottom",
                    ),
                ),
                (
                    "padding_bottom_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("aspect_ratio", models.CharField(blank=True, max_length=20)),
                (
                    "border_radius_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Border radius",
                    ),
                ),
                (
                    "border_radius_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
            ],
            options={
                "verbose_name": "Module Config",
                "verbose_name_plural": "Module Configs",
                "unique_together": {("module", "css_breakpoint")},
                "ordering": ("css_breakpoint",),
            },
        ),
        migrations.CreateModel(
            name="TextConfig",
            fields=[
                (
                    "moduleconfig_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="xprez.moduleconfig",
                    ),
                ),
                (
                    "font_size",
                    models.CharField(
                        choices=[
                            ("smallest", "Smallest"),
                            ("small", "Small"),
                            ("normal", "Normal"),
                            ("large", "Large"),
                            ("largest", "Largest"),
                            ("custom", "Custom"),
                        ],
                        default="normal",
                        max_length=20,
                        verbose_name="Font size",
                    ),
                ),
                (
                    "text_align",
                    models.CharField(
                        choices=[
                            ("left", "Left"),
                            ("center", "Center"),
                            ("right", "Right"),
                        ],
                        default="left",
                        max_length=20,
                        verbose_name="Text align",
                    ),
                ),
                (
                    "media_role",
                    models.CharField(
                        choices=[
                            ("background", "Background"),
                            ("lead", "Lead"),
                            ("icon", "Icon"),
                        ],
                        default="lead",
                        max_length=20,
                        verbose_name="Media role",
                    ),
                ),
                ("media_background_position", models.PositiveIntegerField(default=0)),
                ("media_lead_to_edge", models.BooleanField(default=True)),
                ("media_icon_max_size", models.PositiveIntegerField(default=100)),
                (
                    "media_crop",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("1:1", "1:1"),
                            ("3:2", "3:2"),
                            ("4:3", "4:3"),
                            ("16:9", "16:9"),
                        ],
                        blank=True,
                        default="",
                        max_length=5,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("xprez.moduleconfig",),
        ),
        migrations.CreateModel(
            name="GalleryConfig",
            fields=[
                (
                    "moduleconfig_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="xprez.moduleconfig",
                    ),
                ),
                (
                    "columns",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "1"),
                            (2, "2"),
                            (3, "3"),
                            (4, "4"),
                            (6, "6"),
                            (8, "8"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "gap_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="small",
                        max_length=20,
                        verbose_name="Gap",
                        blank=True,
                    ),
                ),
                ("gap_custom", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "padding_horizontal_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="",
                        max_length=20,
                        verbose_name="Padding horizontal",
                        blank=True,
                    ),
                ),
                (
                    "padding_horizontal_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "padding_vertical_choice",
                    models.CharField(
                        choices=[
                            ("", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="",
                        max_length=20,
                        verbose_name="Padding vertical",
                        blank=True,
                    ),
                ),
                (
                    "padding_vertical_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("xprez.moduleconfig",),
        ),
    ]
