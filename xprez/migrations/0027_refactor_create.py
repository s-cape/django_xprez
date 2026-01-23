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
                        default="full",
                        max_length=16,
                        verbose_name="Max width",
                    ),
                ),
                (
                    "max_width_custom",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("alternate_color", models.BooleanField(default=False)),
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
                ("image", models.ImageField(upload_to="images", null=True, blank=True)),
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
                ("job_title", models.CharField(max_length=255)),
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
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("full", "Full"),
                            ("custom", "Custom"),
                        ],
                        default="medium",
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
                            ("none", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="Padding left",
                    ),
                ),
                (
                    "padding_right_choice",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="Padding right",
                    ),
                ),
                (
                    "padding_top_choice",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="Padding top",
                    ),
                ),
                (
                    "padding_bottom_choice",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="none",
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
                ("padding_x_linked", models.BooleanField(default=True)),
                ("padding_y_linked", models.BooleanField(default=True)),
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
                        default="medium",
                        max_length=20,
                        verbose_name="Gap",
                    ),
                ),
                ("gap_custom", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "vertical_align",
                    models.CharField(
                        choices=[
                            ("top", "Top"),
                            ("middle", "Middle"),
                            ("bottom", "Bottom"),
                            ("stretch", "Stretch"),
                        ],
                        default="top",
                        max_length=20,
                    ),
                ),
                (
                    "horizontal_align",
                    models.CharField(
                        choices=[
                            ("left", "Left"),
                            ("center", "Center"),
                            ("right", "Right"),
                            ("stretch", "Stretch"),
                        ],
                        default="left",
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
                    "horizontal_align",
                    models.CharField(
                        choices=[
                            ("left", "Left"),
                            ("center", "Center"),
                            ("right", "Right"),
                            ("stretch", "Stretch"),
                        ],
                        default="left",
                        max_length=20,
                    ),
                ),
                (
                    "rowspan",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Row span"
                    ),
                ),
                (
                    "vertical_align",
                    models.CharField(
                        choices=[
                            ("top", "Top"),
                            ("middle", "Middle"),
                            ("bottom", "Bottom"),
                            ("stretch", "Stretch"),
                        ],
                        default="top",
                        max_length=20,
                    ),
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
                    "background",
                    models.BooleanField(default=False),
                ),
                (
                    "border",
                    models.BooleanField(default=True),
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
                    "padding_horizontal_choice",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="Padding horizontal",
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
                            ("none", "None"),
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("custom", "Custom"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="Padding vertical",
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
