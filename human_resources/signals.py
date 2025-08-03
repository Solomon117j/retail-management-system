# human_resources/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Payroll

@receiver(pre_save, sender=Payroll)
def calculate_net_pay(sender, instance, **kwargs):
    instance.net_pay = (instance.base_salary + 
                        instance.overtime_pay + 
                        instance.bonus - 
                        instance.deductions)