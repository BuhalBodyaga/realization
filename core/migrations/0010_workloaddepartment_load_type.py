# Generated by Django 4.2.20 on 2025-06-24 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_employeedisciplineloadtypewish'),
    ]

    operations = [
        migrations.AddField(
            model_name='workloaddepartment',
            name='load_type',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='core.loadtype'),
            preserve_default=False,
        ),
    ]
