# Generated by Django 4.2.9 on 2024-01-02 12:40

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_profile_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="about",
            field=ckeditor.fields.RichTextField(default="No About..."),
        ),
    ]
