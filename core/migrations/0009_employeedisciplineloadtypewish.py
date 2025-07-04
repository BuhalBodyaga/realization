# Generated by Django 4.2.20 on 2025-06-24 07:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_employeedisciplineloadtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeDisciplineLoadTypeWish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discipline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.discipline')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.employee')),
                ('load_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.loadtype')),
            ],
            options={
                'unique_together': {('employee', 'discipline', 'load_type')},
            },
        ),
    ]
