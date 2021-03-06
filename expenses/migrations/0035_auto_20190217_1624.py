# Generated by Django 2.1.5 on 2019-02-17 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0034_auto_20190217_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.AddField(
            model_name='expense',
            name='construction_division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.ConstructionDivision'),
        ),
        migrations.AddField(
            model_name='expense',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.Project'),
        ),
        migrations.AddField(
            model_name='expense',
            name='day',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.Day'),
        ),
        migrations.AddField(
            model_name='subcontractorproject',
            name='day',
            field=models.ManyToManyField(blank=True, null=True, to='expenses.Day'),
        ),
        migrations.AddField(
            model_name='workday',
            name='day',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.Day'),
        ),
    ]
