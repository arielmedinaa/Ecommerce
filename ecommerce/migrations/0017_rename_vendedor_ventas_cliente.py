# Generated by Django 5.0.4 on 2024-05-04 23:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0016_alter_product_control_stock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ventas',
            old_name='vendedor',
            new_name='cliente',
        ),
    ]
