# Generated by Django 2.1.5 on 2019-01-21 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0018_workday_images'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='files',
            new_name='file',
        ),
        migrations.AlterField(
            model_name='workday',
            name='images',
            field=models.ManyToManyField(blank=True, to='expenses.Image'),
        ),
    ]