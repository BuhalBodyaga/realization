# app/signals.py
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkloadDepartment, WorkloadTeacher
from .distribution_logic import distribute_for_instance


@receiver(post_save, sender=WorkloadDepartment)
def auto_distribute_workload(sender, instance, created, **kwargs):
    if created:
        print("⚙️ Автораспределение запущено")
        distribute_for_instance(instance)


@receiver(post_delete, sender=WorkloadDepartment)
def delete_related_workload_teacher(sender, instance, **kwargs):
    workload = instance.workload
    subgroup = instance.subgroups

    deleted_count, _ = WorkloadTeacher.objects.filter(
        workload=workload, subgroups=subgroup
    ).delete()

    print(
        f"🧹 Удалено {deleted_count} записей из WorkloadTeacher, связанных с удалённой нагрузкой на департамент."
    )
