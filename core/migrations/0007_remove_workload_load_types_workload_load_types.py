# Generated by Django 4.2.20 on 2025-06-22 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_employee_degree_alter_employee_rank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workload',
            name='load_types',
        ),
        migrations.AddField(
            model_name='workload',
            name='load_types',
            field=models.ManyToManyField(to='core.loadtype'),
        ),
    ]
