# Generated by Django 5.0.4 on 2024-06-12 11:32

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SkillsHub', '0020_alter_mensaje_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensaje',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
