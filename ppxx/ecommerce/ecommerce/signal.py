# signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from ecommerce.models import Product
from .models import Action


@receiver(post_save, sender=get_user_model())
def user_action_post_save(sender, instance, created, **kwargs):
    action_type = 'CREATE' if created else 'UPDATE'
    Action.objects.create(
        user=instance,
        action_types=action_type,
        content_type='User',
        # object_id=instance.id,
        object_repr=str(instance.email),
    )

@receiver(pre_delete, sender=get_user_model())
def user_action_pre_delete(sender, instance, **kwargs):
    Action.objects.create(
        user=instance,
        action_types='DELETE',
        content_type='User',
        object_id=instance.id,
        object_repr=str(instance.email),
    )


@receiver(post_save, sender=Product)
def product_action_post_save(sender, instance, created, **kwargs):
    action_type = 'CREATE' if created else 'UPDATE'
    Action.objects.create(
        user=instance.user,  # Utiliser l'utilisateur associé au produit
        action_types=action_type,
        content_type='Product',
        object_id=instance.id,
        object_repr=str(instance.name),
    )

@receiver(pre_delete, sender=Product)
def product_action_pre_delete(sender, instance, **kwargs):
    Action.objects.create(
        user=instance.user,  # Associer l'utilisateur du produit
        action_types='DELETE',
        content_type='Product',
        object_id=instance.id,
        object_repr=str(instance.name),
    )