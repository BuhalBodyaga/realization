# Generated by Django 4.2.20 on 2025-05-26 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_department_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='discipline_types',
            field=models.ManyToManyField(blank=True, related_name='employees', to='core.disciplinetype', verbose_name='Типы дисциплин, которые может вести'),
        ),
    ]
