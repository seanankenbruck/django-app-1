# Generated by Django 4.2rc1 on 2023-03-23 02:06

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_tag_product_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.product_image_file_path),
        ),
    ]
