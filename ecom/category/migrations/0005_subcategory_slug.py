# Generated by Django 3.2.7 on 2022-08-24 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='slug',
            field=models.SlugField(max_length=100, null=True, unique=True),
        ),
    ]
