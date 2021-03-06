# Generated by Django 2.1.5 on 2019-01-20 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0013_auto_20190120_0142'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='lng',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='workday',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='expenses.Project'),
        ),
    ]
