from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Transaction
from userauths.models import User

@receiver(post_save, sender=Transaction)
def update_user_balance(sender, instance, **kwargs):
    if instance.user:
        instance.user.sync_balance()