# Generated by Django 2.1.5 on 2019-02-03 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0025_auto_20190203_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='expense',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.Expense'),
        ),
    ]