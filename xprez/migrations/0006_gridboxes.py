# Generated by Django 2.1 on 2019-12-15 15:22

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xprez', '0005_auto_20191025_1352'),
    ]

    operations = [
        migrations.CreateModel(
            name='GridBoxes',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='xprez.Content')),
                ('columns', models.PositiveSmallIntegerField(default=2)),
                ('margin', models.CharField(choices=[('none', 'none'), ('m', 'm'), ('l', 'l')], default='m', max_length=4)),
                ('text_size', models.CharField(choices=[('xs', 'xs'), ('s', 's'), ('m', 'm')], default='m', max_length=2)),
                ('padded', models.BooleanField(default=True)),
                ('content_centered', models.BooleanField(default=False)),
                ('edge_images', models.BooleanField(default=False)),
                ('boxes_filled', models.BooleanField(default=True)),
                ('border', models.BooleanField(default=True)),
                ('boxes', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None)),
            ],
            bases=('xprez.content',),
        ),
    ]
