# Generated by Django 5.0.4 on 2024-04-07 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0003_rename_nombre_usuario_user_username_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
