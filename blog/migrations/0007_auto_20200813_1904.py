# Generated by Django 3.0.8 on 2020-08-13 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20200813_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogcategory',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='blogcategory',
            name='slug',
            field=models.SlugField(allow_unicode=True, help_text='A slug to identify posts by this category', verbose_name='slug'),
        ),
    ]
