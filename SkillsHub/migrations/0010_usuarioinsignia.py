# Generated by Django 5.0.4 on 2024-06-09 13:42

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SkillsHub', '0009_insignia'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsuarioInsignia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('activa', models.BooleanField(default=False)),
                ('desbloqueada', models.BooleanField(default=False)),
                ('insignia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SkillsHub.insignia')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
