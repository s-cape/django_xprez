# Generated by Django 4.1.4 on 2024-11-04 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xprez', '0027_grid'),
    ]

    operations = [
        migrations.CreateModel(
            name='GridItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField()),
                ('text', models.TextField()),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='xprez.grid')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]